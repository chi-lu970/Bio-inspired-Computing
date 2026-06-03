"""
API 路由定義。

端點：
  GET  /api/health   健康檢查
  POST /api/solve    VRP 求解
"""
import asyncio
import logging
import threading
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, HTTPException, Request

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


async def _poll_disconnect(
    request: Request,
    cancel_event: threading.Event,
) -> None:
    """每 0.5 秒輪詢客戶端是否已斷線，斷線後設定取消旗標以中止 solver thread。"""
    try:
        while not cancel_event.is_set():
            if await request.is_disconnected():
                cancel_event.set()
                logger.info("client disconnected: solver cancel signal sent")
                return
            await asyncio.sleep(0.5)
    except asyncio.CancelledError:
        pass


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
async def solve(req: SolveRequest, request: Request) -> SolveResponse:
    """PyVRP 求解端點。

    求解在 thread pool 中執行（避免阻塞 event loop）。
    cancel_event 傳入 solver，讓 GA 每次迭代都能檢查並提早結束：
      - _poll_disconnect 每 0.5s 輪詢客戶端是否斷線（F5、關分頁），斷線即設旗標。
      - 伺服器端硬逾時（max_runtime + 10s）觸發時也設旗標並回傳 504。
      - finally 確保任何退出路徑都會通知 solver thread 停止。
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

    # 伺服器端硬逾時 = solver max_runtime + 10s 緩衝，保底釋放 semaphore
    hard_timeout = req.config.max_runtime_seconds + 10
    cancel_event = threading.Event()

    async with _solver_semaphore:
        future = loop.run_in_executor(_executor, solver_svc.solve, req, cancel_event)
        disconnect_watcher = asyncio.create_task(
            _poll_disconnect(request, cancel_event)
        )
        try:
            # asyncio.shield 保護 future 不被 cancel（thread 無法強制中止）；
            # wait_for 逾時或 CancelledError 時，finally 會設旗標讓 thread 自行結束。
            result: SolveResponse = await asyncio.wait_for(
                asyncio.shield(future), timeout=hard_timeout
            )
        except asyncio.TimeoutError:
            logger.warning("hard server timeout after %.0fs", hard_timeout)
            raise HTTPException(
                status_code=504,
                detail={
                    "error": "solver_timeout",
                    "message": (
                        f"求解超過伺服器硬逾時（{hard_timeout:.0f} 秒），"
                        "請縮短最大運算時間或減少店面數量後重試。"
                    ),
                },
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
        finally:
            # 無論正常完成、逾時、斷線或例外，都通知 solver thread 可以停止
            cancel_event.set()
            disconnect_watcher.cancel()

    logger.info(
        "solve done feasible=%s routes=%d distance=%.3fkm runtime=%.3fs",
        result.feasible,
        result.num_routes_used,
        result.total_distance_km,
        result.runtime_seconds,
    )
    return result
