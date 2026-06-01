"""
PyVRP Web API — FastAPI 應用入口

啟動方式：
    uv run --python 3.11 uvicorn webapp.backend.main:app --port 8000

啟動後：
    前端介面：http://localhost:8000/
    API 文件：http://localhost:8000/docs
"""
# ── 必須在所有其他 import 之前 ──────────────────────────────────
# 本地目錄有未編譯的 pyvrp/ 原始碼，會被 Python 優先載入並蓋掉
# 已安裝的 PyVRP wheel。透過把 venv site-packages 插到 sys.path
# 最前面，確保使用已編譯的版本。
import sys
from pathlib import Path as _Path

_venv_site = _Path(__file__).parents[2] / ".venv" / "Lib" / "site-packages"
if _venv_site.exists() and str(_venv_site) not in sys.path:
    sys.path.insert(0, str(_venv_site))
# ────────────────────────────────────────────────────────────────

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from webapp.backend.api.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(name)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = FastAPI(
    title="PyVRP Web API",
    description="PyVRP 全端視覺化操作介面的後端 API",
    version="0.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 路由
app.include_router(router)

# 掛載前端靜態檔案（必須在所有 API 路由之後）
FRONTEND_DIR = _Path(__file__).resolve().parents[1] / "frontend"
if FRONTEND_DIR.exists():
    app.mount(
        "/",
        StaticFiles(directory=str(FRONTEND_DIR), html=True),
        name="frontend",
    )
