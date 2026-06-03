"""
API 路由定義。

端點：
  GET  /api/health   健康檢查
  POST /api/solve    VRP 求解
"""
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, HTTPException

from webapp.backend.api.schemas import ErrorResponse, SolveRequest, SolveResponse
from webapp.backend.services import solver as solver_svc
from webapp.backend.services.exceptions import (
    CrossUtmZoneError,
    InfeasibleByConstructionError,
    InvalidTimeWindowError,
    SolverInternalError,
    SolverTimeoutError,
    WebAppError,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

# 用於在 async 端點內跑同步阻塞的 solver
_executor = ThreadPoolExecutor(max_workers=8)

# 同時只允許一個求解請求，避免 thread 堆積卡死系統
_solver_semaphore = asyncio.Semaphore(1)


# ─────────────────────────────────────────────────────────────
# GET /api/health
# ─────────────────────────────────────────────────────────────


@router.get("/health", summary="健康檢查")
def health() -> dict:
    """確認服務可運作，並回傳 PyVRP 版本。"""
    import pyvrp

    return {
        "status": "ok",
        "pyvrp_version": getattr(pyvrp, "__version__", "unknown"),
    }


# ─────────────────────────────────────────────────────────────
# POST /api/solve
# ─────────────────────────────────────────────────────────────


@router.post(
    "/solve",
    response_model=SolveResponse,
    responses={
        422: {"model": ErrorResponse, "description": "輸入驗證失敗"},
        504: {"model": ErrorResponse, "description": "求解逾時"},
        500: {"model": ErrorResponse, "description": "伺服器內部錯誤"},
    },
    summary="VRP 求解",
    description=(
        "接收倉庫、店面、時間窗、車隊設定，執行 PyVRP 求解後回傳最佳路線。"
    ),
)
async def solve(req: SolveRequest) -> SolveResponse:
    """PyVRP 求解端點。

    求解在 thread pool 中執行（避免阻塞 event loop）。
    停止條件由 solver 內的 TimedNoImprovement 負責（NoImprovement + MaxRuntime），
    不依賴 asyncio.wait_for 當超時機制（Python 3.12+ 的 wait_for 在 thread 無法取消時會卡住）。
    同時只允許一個求解請求，後續請求會立即收到 503。
    """
    # 若有另一個求解正在執行，立即拒絕（避免 thread 堆積卡死系統）
    if _solver_semaphore.locked():
        logger.warning("solve rejected: another solve is in progress")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "solver_busy",
                "message": "目前有另一個求解正在執行中，請稍後再試。",
            },
        )

    loop = asyncio.get_event_loop()

    logger.info(
        "solve start stores=%d vehicle_types=%d max_runtime=%.1fs",
        len(req.stores),
        len(req.vehicle_types),
        req.config.max_runtime_seconds,
    )

    async with _solver_semaphore:
        try:
            # 直接 await executor，停止時間由 solver 裡的 TimedNoImprovement 控制
            result: SolveResponse = await loop.run_in_executor(
                _executor, solver_svc.solve, req
            )
        except (CrossUtmZoneError, InvalidTimeWindowError, InfeasibleByConstructionError) as exc:
            logger.info("solve 422 error: %s", exc)
            raise HTTPException(status_code=422, detail=exc.to_dict())
        except SolverTimeoutError as exc:
            logger.warning("solver timeout: %s", exc)
            raise HTTPException(status_code=504, detail=exc.to_dict())
        except SolverInternalError as exc:
            logger.error("solver internal error: %s", exc)
            raise HTTPException(status_code=500, detail=exc.to_dict())
        except WebAppError as exc:
            logger.error("unexpected webapp error: %s", exc)
            raise HTTPException(status_code=500, detail=exc.to_dict())

    logger.info(
        "solve done feasible=%s routes=%d distance=%.3fkm runtime=%.3fs",
        result.feasible,
        result.num_routes_used,
        result.total_distance_km,
        result.runtime_seconds,
    )
    return result
