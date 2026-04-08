"""
PyVRP Result → SolveResponse 序列化。

最棘手的部分是「累積時間計算」：PyVRP 的 Route 物件只給出 visits 順序與
總體統計，每站抵達/離開時間需要我們依以下規則自行 walk through：

  T0 = 倉庫出發時間（取倉庫 tw_early，簡化假設）
  for each stop in route:
      arrival = previous_departure + duration(prev → stop)
      effective_start = max(arrival, stop.tw_early)
      wait = effective_start - arrival
      departure = effective_start + service_duration
  最後從最後一站回到倉庫
"""
from typing import List

from pyvrp import Result

from webapp.backend.api.schemas import (
    LatLng,
    RouteStop,
    SolveRequest,
    SolveResponse,
    VehicleRoute,
)

# 預先定義 10 色 palette，供前端依 vehicle index 循環使用
COLOR_PALETTE = [
    "#E63946",  # 鮮紅
    "#2196F3",  # 亮藍
    "#FF9800",  # 橘
    "#4CAF50",  # 綠
    "#9C27B0",  # 紫
    "#00BCD4",  # 青
    "#FF4081",  # 桃紅
    "#FF5722",  # 深橘
    "#3F51B5",  # 靛藍
    "#009688",  # 藍綠
]


def _color_for(idx: int) -> str:
    return COLOR_PALETTE[idx % len(COLOR_PALETTE)]


def solution_to_response(
    result: Result,
    request: SolveRequest,
    scale: int,
) -> SolveResponse:
    """把 PyVRP 的 Result 物件展開成 SolveResponse。"""
    solution = result.best
    feasible = result.is_feasible()
    warnings: List[str] = []

    if not feasible:
        warnings.append("未能在時限內找到可行解，回傳最佳不可行解")

    # 建立 PyVRP 客戶索引 → Store 物件的對應表
    # PyVRP locations 順序：[depot, store_0, store_1, ...]
    # Route.visits() 回傳的索引從 1 開始（0 為 depot）
    stores_by_idx = {i + 1: store for i, store in enumerate(request.stores)}

    depot_loc = request.depot.location
    depot_tw = request.depot.time_window
    speed_m_per_min = request.config.avg_speed_kmh * 1000.0 / 60.0

    vehicle_routes: List[VehicleRoute] = []
    total_distance_km = 0.0

    for v_idx, route in enumerate(solution.get_routes()):
        visits = list(route.visits())
        if not visits:
            continue  # 跳過未使用的車輛

        vt_idx = route.vehicle_type()
        vt = request.vehicle_types[vt_idx]
        color = _color_for(v_idx)

        stops: List[RouteStop] = []

        # ── 起點：倉庫 ─────────────────────────────────────
        depart_time = depot_tw.start  # 簡化：以倉庫開放時間出發
        stops.append(
            RouteStop(
                store_id="depot",
                name=request.depot.name,
                location=depot_loc,
                arrival_minutes=depart_time,
                departure_minutes=depart_time,
                wait_minutes=0,
                distance_from_prev_km=0.0,
                cumulative_load=0,
            )
        )

        prev_loc = depot_loc
        prev_departure = depart_time
        cumulative_load = 0

        # ── 中途各站 ───────────────────────────────────────
        for client_idx in visits:
            store = stores_by_idx[client_idx]
            seg_km = _haversine_km(prev_loc, store.location)
            seg_min = max(1, int(round(seg_km * 1000.0 / speed_m_per_min)))

            arrival = prev_departure + seg_min
            effective_start = max(arrival, store.time_window.start)
            wait = effective_start - arrival
            departure = effective_start + store.service_minutes

            cumulative_load += store.demand

            stops.append(
                RouteStop(
                    store_id=store.id,
                    name=store.name,
                    location=store.location,
                    arrival_minutes=arrival,
                    departure_minutes=departure,
                    wait_minutes=wait,
                    distance_from_prev_km=round(seg_km, 3),
                    cumulative_load=cumulative_load,
                )
            )

            prev_loc = store.location
            prev_departure = departure

        # ── 終點：回到倉庫 ─────────────────────────────────
        seg_km = _haversine_km(prev_loc, depot_loc)
        seg_min = max(1, int(round(seg_km * 1000.0 / speed_m_per_min)))
        arrival = prev_departure + seg_min
        stops.append(
            RouteStop(
                store_id="depot",
                name=request.depot.name,
                location=depot_loc,
                arrival_minutes=arrival,
                departure_minutes=arrival,
                wait_minutes=0,
                distance_from_prev_km=round(seg_km, 3),
                cumulative_load=cumulative_load,
            )
        )

        # 從 PyVRP route 物件直接拿總距離（已 SCALE 過，需還原為 km）
        route_distance_km = route.distance() / scale / 1000.0
        route_duration_min = arrival - depart_time

        vehicle_routes.append(
            VehicleRoute(
                vehicle_index=v_idx,
                vehicle_type=vt.name,
                color=color,
                stops=stops,
                total_distance_km=round(route_distance_km, 3),
                total_duration_minutes=route_duration_min,
                total_load=cumulative_load,
                capacity=vt.capacity,
            )
        )
        total_distance_km += route_distance_km

    return SolveResponse(
        feasible=feasible,
        runtime_seconds=round(result.runtime, 3),
        iterations=result.num_iterations,
        total_distance_km=round(total_distance_km, 3),
        num_routes_used=len(vehicle_routes),
        routes=vehicle_routes,
        warnings=warnings,
    )


# ─────────────────────────────────────────────────────────────
# Haversine 公式：用 WGS84 經緯度直接算球面距離（km）
# 比再投影一次 UTM 簡單，且序列化時已不需要 PyVRP 級的精度
# ─────────────────────────────────────────────────────────────
def _haversine_km(a: LatLng, b: LatLng) -> float:
    from math import asin, cos, radians, sin, sqrt

    R = 6371.0088  # 地球平均半徑 (km)
    lat1, lng1 = radians(a.lat), radians(a.lng)
    lat2, lng2 = radians(b.lat), radians(b.lng)
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    h = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
    return 2 * R * asin(sqrt(h))
