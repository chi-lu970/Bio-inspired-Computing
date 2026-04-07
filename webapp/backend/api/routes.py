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
_executor = ThreadPoolExecutor(max_workers=4)


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

    求解在 thread pool 中執行（避免阻塞 event loop），
    並設有 `max_runtime_seconds + 5` 秒的外部 timeout 保護。
    """
    loop = asyncio.get_event_loop()
    outer_timeout = req.config.max_runtime_seconds + 15.0

    logger.info(
        "solve start stores=%d vehicle_types=%d max_runtime=%.1fs",
        len(req.stores),
        len(req.vehicle_types),
        req.config.max_runtime_seconds,
    )

    try:
        result: SolveResponse = await asyncio.wait_for(
            loop.run_in_executor(_executor, solver_svc.solve, req),
            timeout=outer_timeout,
        )
    except asyncio.TimeoutError:
        logger.warning("solve timeout after %.1fs", outer_timeout)
        raise HTTPException(
            status_code=504,
            detail=SolverTimeoutError(
                req.config.max_runtime_seconds
            ).to_dict(),
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
