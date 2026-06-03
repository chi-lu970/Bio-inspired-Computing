"""
WGS84 ↔ UTM 座標轉換。

使用 pyproj 把使用者輸入的 (lat, lng) 轉成公尺單位的 UTM 平面座標。
PyVRP 內部使用整數，故 solver 層會把公尺乘以 SCALE 後取整。
"""
from dataclasses import dataclass
from typing import List, Sequence, Tuple

from pyproj import Transformer

from webapp.backend.api.schemas import LatLng

from .exceptions import CrossUtmZoneError


@dataclass(frozen=True)
class UtmPoint:
    """UTM 平面座標（單位：公尺）。"""

    x: float
    y: float


# Transformer 建立成本不低，依 zone 快取
_transformer_cache: dict[int, Transformer] = {}


def _utm_zone_for_lng(lng: float) -> int:
    """依經度計算 UTM 帶號（1 ~ 60）。"""
    return int((lng + 180.0) / 6.0) + 1


def _epsg_for_zone(zone: int, northern: bool) -> int:
    """UTM 帶 → EPSG 代碼。北半球 326XX、南半球 327XX。"""
    return (32600 if northern else 32700) + zone


def _get_transformer(zone: int, northern: bool) -> Transformer:
    key = (32600 if northern else 32700) + zone
    if key not in _transformer_cache:
        _transformer_cache[key] = Transformer.from_crs(
            "EPSG:4326",  # WGS84 經緯度
            f"EPSG:{key}",  # 對應 UTM 帶
            always_xy=True,  # 輸入順序為 (lng, lat)
        )
    return _transformer_cache[key]


def wgs84_to_utm(lat: float, lng: float) -> Tuple[float, float, int]:
    """單點 WGS84 → UTM。

    Returns
    -------
    (x, y, zone)
        x、y 為 UTM 平面座標（公尺），zone 為 UTM 帶號。
    """
    zone = _utm_zone_for_lng(lng)
    northern = lat >= 0
    transformer = _get_transformer(zone, northern)
    x, y = transformer.transform(lng, lat)
    return x, y, zone


def wgs84_batch_to_utm(
    points: Sequence[LatLng],
) -> Tuple[List[UtmPoint], int]:
    """批次轉換並驗證所有點屬於同一 UTM 帶。

    Parameters
    ----------
    points
        待轉換的 WGS84 經緯度列表（順序保留）。

    Returns
    -------
    (utm_points, zone)
        轉換後的 UTM 點列表（順序與輸入相同）與共同 UTM 帶號。

    Raises
    ------
    CrossUtmZoneError
        若輸入點橫跨多個 UTM 帶。
    """
    if not points:
        return [], 0

    zones = {_utm_zone_for_lng(p.lng) for p in points}
    if len(zones) > 1:
        raise CrossUtmZoneError(list(zones))

    zone = next(iter(zones))
    # 以第一個點的半球為準（避免赤道附近混用）
    northern = points[0].lat >= 0
    transformer = _get_transformer(zone, northern)

    utm_points: List[UtmPoint] = []
    for p in points:
        x, y = transformer.transform(p.lng, p.lat)
        utm_points.append(UtmPoint(x=x, y=y))

    return utm_points, zone


def euclidean(a: UtmPoint, b: UtmPoint) -> float:
    """兩個 UTM 點的歐式距離（公尺）。"""
    dx = a.x - b.x
    dy = a.y - b.y
    return (dx * dx + dy * dy) ** 0.5
