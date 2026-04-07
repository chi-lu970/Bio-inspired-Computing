"""
PyVRP Web 伺服器啟動腳本

使用方式：
    uv run --python 3.11 python run_server.py

原因：本專案根目錄下有 pyvrp/ 原始碼目錄（未編譯），
Python 預設會優先從 CWD 載入，蓋掉已安裝的 PyVRP wheel。
此腳本在 import 任何東西之前，先把 CWD 從 sys.path 移除，
確保使用 .venv 中已編譯的版本。
"""
import sys
from pathlib import Path

# 1. 移除所有指向 CWD 的 sys.path 項目
_cwd = str(Path(__file__).parent.resolve())
sys.path = [p for p in sys.path if p not in ('', '.', _cwd)]

# 2. 確保 venv site-packages 在最前面
_venv_site = Path(__file__).parent / ".venv" / "Lib" / "site-packages"
if _venv_site.exists():
    sys.path.insert(0, str(_venv_site))

# 3. 把專案根目錄加回來（webapp package 仍需要能被 import）
#    但放在 venv site-packages 之後
sys.path.append(_cwd)

# 診斷輸出
print("[run_server] sys.path:")
for i, p in enumerate(sys.path[:6]):
    print(f"  [{i}] {p}")

# 4. 確認 pyvrp 使用的是 venv 版本
import pyvrp as _chk
print(f"[run_server] pyvrp 載入自: {_chk.__file__}")

# 5. 啟動 uvicorn
import uvicorn
uvicorn.run(
    "webapp.backend.main:app",
    host="127.0.0.1",
    port=8000,
    reload=False,
)
