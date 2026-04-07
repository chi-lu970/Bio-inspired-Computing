"""
PyVRP 求解器整合層。

職責：
1. 將 SolveRequest 轉換成 PyVRP Model
2. 呼叫 Model.solve() 求解
3. 委派 serializer 把結果序列化為 SolveResponse
"""
from typing import List

from pyvrp import Model
from pyvrp.stop import MaxRuntime

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
    """組裝 PyVRP Model。

    Parameters
    ----------
    req
        原始請求。
    utm_points
        已轉換的 UTM 座標列表，順序為：[depot, store_0, store_1, ...]
    """
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
    """求解主入口。

    Raises
    ------
    CrossUtmZoneError
        輸入點橫跨多個 UTM 帶。
    InfeasibleByConstructionError
        總需求超過總容量。
    SolverTimeoutError
        求解時間超過限制（包含緩衝）。
    SolverInternalError
        PyVRP 內部錯誤。
    """
    # 1. 預檢
    _check_construction_feasibility(req)

    # 2. 座標轉換
    all_locs = [req.depot.location] + [s.location for s in req.stores]
    utm_points, utm_zone = wgs84_batch_to_utm(all_locs)

    # 3. 建 Model
    model = _build_model(req, utm_points)

    # 4. 求解（同步阻塞）
    try:
        result = model.solve(
            stop=MaxRuntime(req.config.max_runtime_seconds),
            seed=req.config.seed,
        )
    except TimeoutError as exc:
        raise SolverTimeoutError(req.config.max_runtime_seconds) from exc
    except Exception as exc:  # noqa: BLE001
        raise SolverInternalError(f"PyVRP 求解失敗：{exc}") from exc

    # 5. 序列化
    return solution_to_response(
        result=result,
        request=req,
        scale=SCALE,
    )
