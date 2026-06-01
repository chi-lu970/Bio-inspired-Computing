"""
Pydantic 資料模型：定義 /api/solve 的 request 與 response 結構。

所有時間欄位統一為「從當日 00:00 起算的分鐘整數」（0 ~ 1440）。
所有座標為 WGS84 浮點經緯度。
"""
from typing import List

from pydantic import BaseModel, Field, model_validator


# ─────────────────────────────────────────────────────────────
# 共用基礎型別
# ─────────────────────────────────────────────────────────────


class LatLng(BaseModel):
    """WGS84 經緯度。"""

    lat: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="緯度（WGS84），範圍 -90 ~ 90",
        examples=[25.0478],
    )
    lng: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="經度（WGS84），範圍 -180 ~ 180",
        examples=[121.5170],
    )


class TimeWindow(BaseModel):
    """時間窗，以從當日 00:00 起算的分鐘整數表示。"""

    start: int = Field(
        ...,
        ge=0,
        le=1440,
        description="開始時間（分鐘，0 ~ 1440）",
        examples=[480],  # 08:00
    )
    end: int = Field(
        ...,
        ge=0,
        le=1440,
        description="結束時間（分鐘，0 ~ 1440），必須晚於 start",
        examples=[1080],  # 18:00
    )

    @model_validator(mode="after")
    def _validate_order(self) -> "TimeWindow":
        if self.end <= self.start:
            raise ValueError(
                f"end ({self.end}) 必須晚於 start ({self.start})"
            )
        return self


# ─────────────────────────────────────────────────────────────
# 請求模型
# ─────────────────────────────────────────────────────────────


class Depot(BaseModel):
    """倉庫定義（單一倉庫）。"""

    name: str = Field(default="Depot", description="倉庫名稱")
    location: LatLng
    time_window: TimeWindow


class Store(BaseModel):
    """店面（客戶）定義。"""

    id: str = Field(..., description="店面唯一識別碼，例如 S001")
    name: str = Field(..., description="店面顯示名稱")
    location: LatLng
    time_window: TimeWindow
    demand: int = Field(
        ...,
        ge=0,
        description="需求量（kg 或件數）",
        examples=[10],
    )
    service_minutes: int = Field(
        default=10,
        ge=0,
        description="在此店面的服務時長（分鐘）",
    )


class VehicleType(BaseModel):
    """車型定義。"""

    name: str = Field(..., description="車型名稱")
    capacity: int = Field(
        ...,
        gt=0,
        description="單台車的最大載重",
        examples=[100],
    )
    num_available: int = Field(
        ...,
        gt=0,
        description="此車型的可用台數",
        examples=[2],
    )


class SolverConfig(BaseModel):
    """求解器設定。"""

    max_runtime_seconds: float = Field(
        default=10.0,
        gt=0.0,
        le=300.0,
        description="求解最長執行秒數",
    )
    seed: int = Field(default=42, description="隨機種子，用於結果可重現")
    avg_speed_kmh: float = Field(
        default=40.0,
        gt=0.0,
        description="平均車速（km/h），用於由距離反推行駛時間",
    )


class SolveRequest(BaseModel):
    """`/api/solve` 的請求 body。"""

    depot: Depot
    stores: List[Store] = Field(..., min_length=1, description="店面列表")
    vehicle_types: List[VehicleType] = Field(
        ..., min_length=1, description="車型列表"
    )
    config: SolverConfig = Field(default_factory=SolverConfig)

    @model_validator(mode="after")
    def _validate_unique_store_ids(self) -> "SolveRequest":
        ids = [s.id for s in self.stores]
        duplicates = {sid for sid in ids if ids.count(sid) > 1}
        if duplicates:
            raise ValueError(f"店面 id 重複：{sorted(duplicates)}")
        return self


# ─────────────────────────────────────────────────────────────
# 回應模型
# ─────────────────────────────────────────────────────────────


class RouteStop(BaseModel):
    """路線中的單一停靠點（含倉庫起訖點）。"""

    store_id: str = Field(
        ...,
        description="店面 id；倉庫起訖點固定為 'depot'",
    )
    name: str
    location: LatLng
    arrival_minutes: int = Field(..., description="抵達時間（分鐘）")
    departure_minutes: int = Field(..., description="離開時間（分鐘）")
    wait_minutes: int = Field(
        default=0,
        ge=0,
        description="抵達後因時間窗未開的等待分鐘數",
    )
    distance_from_prev_km: float = Field(
        ..., ge=0.0, description="距上一停靠點的距離（km）"
    )
    cumulative_load: int = Field(
        ..., ge=0, description="此停靠點之後車輛累積載重"
    )


class VehicleRoute(BaseModel):
    """單一車輛的完整行程。"""

    vehicle_index: int = Field(..., ge=0, description="車輛索引")
    vehicle_type: str = Field(..., description="所屬車型名稱")
    color: str = Field(
        ...,
        description="前端繪圖用的顏色（hex），由後端預先指派",
        examples=["#E63946"],
    )
    stops: List[RouteStop]
    total_distance_km: float = Field(..., ge=0.0)
    total_duration_minutes: int = Field(..., ge=0)
    total_load: int = Field(..., ge=0)
    capacity: int = Field(..., gt=0)


class SolveResponse(BaseModel):
    """`/api/solve` 的回應 body。"""

    feasible: bool = Field(..., description="是否找到可行解")
    runtime_seconds: float = Field(..., ge=0.0, description="實際求解耗時")
    iterations: int = Field(..., ge=0, description="GA 迭代次數")
    total_distance_km: float = Field(..., ge=0.0, description="所有路線總距離")
    num_routes_used: int = Field(..., ge=0, description="實際使用的車輛數")
    routes: List[VehicleRoute]
    warnings: List[str] = Field(
        default_factory=list, description="非致命警告訊息"
    )


# ─────────────────────────────────────────────────────────────
# 錯誤回應模型（用於 4xx / 5xx）
# ─────────────────────────────────────────────────────────────


class ErrorResponse(BaseModel):
    """統一錯誤回應格式。"""

    error: str = Field(..., description="錯誤代碼，如 cross_utm_zone")
    message: str = Field(..., description="使用者可讀的中文錯誤訊息")
