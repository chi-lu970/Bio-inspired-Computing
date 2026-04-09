"""
PyVRP 求解器整合層。

職責：
1. 將 SolveRequest 轉換成 PyVRP Model
2. 手動組裝 GA（控制 nb_granular 鄰域大小避免小問題搜尋空間爆炸）
3. 委派 serializer 把結果序列化為 SolveResponse
"""
from typing import List

from pyvrp import Model, PenaltyManager, Population, RandomNumberGenerator, Solution
from pyvrp.diversity import broken_pairs_distance as bpd
from pyvrp.GeneticAlgorithm import GeneticAlgorithm
from pyvrp.Population import PopulationParams
from pyvrp.crossover import selective_route_exchange as srex
from pyvrp.search import NODE_OPERATORS, ROUTE_OPERATORS, LocalSearch, compute_neighbours
from pyvrp.search.neighbourhood import NeighbourhoodParams
from pyvrp.stop import TimedNoImprovement

from webapp.backend.api.schemas import SolveRequest, SolveResponse

from .coord import UtmPoint, euclidean, wgs84_batch_to_utm
from .exceptions import (
    InfeasibleByConstructionError,
    SolverInternalError,
    SolverTimeoutError,
)
from .serializer import solution_to_response

# 整數比例尺：UTM 公尺 ×10 → 0.1 公尺精度
SCALE = 10

# 鄰域大小：每個節點最多考慮幾個鄰居
# 預設 20 對小問題（<30 站）等於幾乎全圖，造成 local search 過慢
# 固定用 7 讓迭代速度可控
NB_GRANULAR = 7


def _check_construction_feasibility(req: SolveRequest) -> None:
    """快速檢查明顯不可行的輸入。"""
    total_demand = sum(s.demand for s in req.stores)
    total_capacity = sum(
        vt.capacity * vt.num_available for vt in req.vehicle_types
    )
    if total_demand > total_capacity:
        raise InfeasibleByConstructionError(
            f"總需求量 {total_demand} 超過總載重容量 {total_capacity}，"
            f"無可行解"
        )


def _build_model(
    req: SolveRequest,
    utm_points: List[UtmPoint],
) -> Model:
    """組裝 PyVRP Model。"""
    model = Model()

    # 1. 倉庫
    depot_pt = utm_points[0]
    depot_node = model.add_depot(
        x=int(depot_pt.x * SCALE),
        y=int(depot_pt.y * SCALE),
        tw_early=req.depot.time_window.start,
        tw_late=req.depot.time_window.end,
    )

    # 2. 店面
    client_nodes = []
    for store, pt in zip(req.stores, utm_points[1:]):
        c = model.add_client(
            x=int(pt.x * SCALE),
            y=int(pt.y * SCALE),
            demand=store.demand,
            service_duration=store.service_minutes,
            tw_early=store.time_window.start,
            tw_late=store.time_window.end,
        )
        client_nodes.append(c)

    # 3. 車型
    for vt in req.vehicle_types:
        model.add_vehicle_type(
            capacity=vt.capacity,
            num_available=vt.num_available,
        )

    # 4. 距離與時間邊
    speed_m_per_min = req.config.avg_speed_kmh * 1000.0 / 60.0
    locations = [depot_node] + client_nodes
    for i, a in enumerate(locations):
        for j, b in enumerate(locations):
            if i == j:
                continue
            dist_m = euclidean(utm_points[i], utm_points[j])
            duration_min = max(1, int(round(dist_m / speed_m_per_min)))
            model.add_edge(
                a,
                b,
                distance=int(round(dist_m * SCALE)),
                duration=duration_min,
            )

    return model


def solve(req: SolveRequest) -> SolveResponse:
    """求解主入口。"""
    # 1. 預檢
    _check_construction_feasibility(req)

    # 2. 座標轉換
    all_locs = [req.depot.location] + [s.location for s in req.stores]
    utm_points, utm_zone = wgs84_batch_to_utm(all_locs)

    # 3. 建 Model
    model = _build_model(req, utm_points)
    data = model.data()

    # 4. 手動組裝 GA，限制 nb_granular 避免小問題搜尋空間爆炸
    rng = RandomNumberGenerator(seed=req.config.seed)
    nb_granular = min(NB_GRANULAR, max(1, data.num_clients - 1))
    neighbours = compute_neighbours(
        data, NeighbourhoodParams(nb_granular=nb_granular)
    )
    ls = LocalSearch(data, rng, neighbours)
    for op in NODE_OPERATORS:
        ls.add_node_operator(op(data))
    for op in ROUTE_OPERATORS:
        ls.add_route_operator(op(data))

    pm = PenaltyManager()
    pop_params = PopulationParams()
    pop = Population(bpd, pop_params)
    init = [Solution.make_random(data, rng) for _ in range(pop_params.min_pop_size)]

    algo = GeneticAlgorithm(data, pm, rng, pop, ls, srex, init)

    # 5. 求解：NoImprovement 主控，MaxRuntime 保底
    stop = TimedNoImprovement(
        max_iterations=500,
        max_runtime=req.config.max_runtime_seconds,
    )
    try:
        result = algo.run(stop)
    except Exception as exc:  # noqa: BLE001
        raise SolverInternalError(f"PyVRP 求解失敗：{exc}") from exc

    # 6. 序列化
    return solution_to_response(
        result=result,
        request=req,
        scale=SCALE,
    )
