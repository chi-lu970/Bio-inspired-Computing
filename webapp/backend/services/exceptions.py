"""
自訂例外型別。

每個例外都帶有 `code`（給機器讀）與 `message`（給人讀的繁體中文），
API 層可直接序列化為 `{"error": code, "message": message}`。
"""
from typing import List, Optional


class WebAppError(Exception):
    """所有 webapp 自訂例外的基底類別。"""

    code: str = "internal_error"
    message: str = "發生未預期的錯誤"

    def __init__(self, message: Optional[str] = None) -> None:
        if message is not None:
            self.message = message
        super().__init__(self.message)

    def to_dict(self) -> dict:
        return {"error": self.code, "message": self.message}


class CrossUtmZoneError(WebAppError):
    """輸入的點橫跨多個 UTM 帶。"""

    code = "cross_utm_zone"

    def __init__(self, zones: List[int]) -> None:
        self.zones = sorted(set(zones))
        super().__init__(
            f"資料跨越多個 UTM 帶 {self.zones}，請分區處理"
        )

    def to_dict(self) -> dict:
        return {**super().to_dict(), "zones": self.zones}


class InvalidTimeWindowError(WebAppError):
    """時間窗順序錯誤（補強 Pydantic 未涵蓋的跨欄位驗證）。"""

    code = "invalid_time_window"

    def __init__(self, store_id: str, message: str) -> None:
        self.store_id = store_id
        super().__init__(message)

    def to_dict(self) -> dict:
        return {**super().to_dict(), "store_id": self.store_id}


class InfeasibleByConstructionError(WebAppError):
    """輸入本身明顯不可行（如總需求 > 總容量）。"""

    code = "infeasible_by_construction"


class SolverTimeoutError(WebAppError):
    """求解時間超過上限。"""

    code = "solver_timeout"

    def __init__(self, max_runtime_seconds: float) -> None:
        self.max_runtime_seconds = max_runtime_seconds
        super().__init__(
            f"求解超過時限 {max_runtime_seconds} 秒"
        )

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "max_runtime_seconds": self.max_runtime_seconds,
        }


class SolverInternalError(WebAppError):
    """PyVRP 內部錯誤。"""

    code = "solver_internal_error"
