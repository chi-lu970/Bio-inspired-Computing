# 技術設計文件：PyVRP 全端視覺化操作介面

> **配套文件**：請先閱讀 `proposal.md` 了解動機與範圍
> **狀態**：草案
> **最後更新**：2026-04-07

---

## 1. 整體架構

### 1.1 系統分層

```
┌──────────────────────────────────────────────────────────────┐
│                         展示層 (Presentation)                  │
│         HTML  +  CSS  +  Vanilla JS  +  Leaflet.js            │
│              （無框架、無建置工具、CDN 引入）                    │
└──────────────────────────────────┬───────────────────────────┘
                                   │ fetch() / JSON
┌──────────────────────────────────▼───────────────────────────┐
│                       API 層 (FastAPI)                        │
│   路由定義 / Pydantic 驗證 / CORS / OpenAPI 自動文件            │
└──────────────────────────────────┬───────────────────────────┘
                                   │ Python function call
┌──────────────────────────────────▼───────────────────────────┐
│                    服務層 (Service Layer)                      │
│   ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│   │ 座標轉換器   │  │ VRP 模型建構  │  │ 結果序列化器       │   │
│   │ (pyproj)    │  │ (PyVRP Model)│  │ (Pydantic models)│   │
│   └─────────────┘  └──────────────┘  └──────────────────┘   │
└──────────────────────────────────┬───────────────────────────┘
                                   │ pyvrp.Model.solve()
┌──────────────────────────────────▼───────────────────────────┐
│                      求解引擎 (PyVRP)                          │
│        Genetic Algorithm + Local Search + HGS                 │
└──────────────────────────────────────────────────────────────┘
```

### 1.2 目錄結構建議

```
Bio-inspired-Computing/
├── pyvrp/                     # 既有 PyVRP 套件，不動
├── webapp/                    # ★ 新增：Web 介面
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI 應用入口
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py      # /api/solve、/api/health 等端點
│   │   │   └── schemas.py     # Pydantic 請求/回應模型
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── coord.py       # WGS84 ↔ UTM 轉換
│   │   │   ├── solver.py      # PyVRP Model 整合
│   │   │   └── serializer.py  # Solution → JSON
│   │   └── examples/
│   │       └── taipei_demo.json   # 示範資料
│   └── frontend/
│       ├── index.html         # 主頁面
│       ├── css/
│       │   └── style.css
│       ├── js/
│       │   ├── form.js        # 表單邏輯
│       │   ├── map.js         # Leaflet 地圖
│       │   └── api.js         # API 呼叫封裝
│       └── assets/
│           ├── depot.svg
│           └── store.svg
└── pyproject.toml             # 修改：新增 fastapi/pyproj/uvicorn
```

---

## 2. 關鍵技術決策

### 決策 1：採用 FastAPI 而非 Flask

| 評估項 | FastAPI | Flask |
|--------|---------|-------|
| 自動產生 OpenAPI 文件 | ✅ 內建 | ❌ 需 flask-restx |
| 型別檢查與自動驗證 | ✅ Pydantic | ❌ 需手寫 |
| 非同步支援 | ✅ async/await 原生 | ⚠️ 需 quart 或外掛 |
| 學習曲線 | 中（type hints） | 低 |
| 與課程主題契合 | ✅ 現代 Python 寫法 | ⚠️ 偏傳統 |

**結論**：選 FastAPI。即使 v1 是同步求解，未來轉非同步時 FastAPI 過渡平滑。

---

### 決策 2：座標轉換策略

#### 問題

PyVRP 內部使用**整數平面座標**，而使用者輸入的是 **WGS84 浮點經緯度**。
若處理不當會：
- 精度損失（直接 `int()` 會丟掉小數，公里級誤差）
- UTM 帶切換錯誤（台灣西部跨 50N、東部跨 51N）

#### 方案比較

| 方案 | 做法 | 優點 | 缺點 |
|------|------|------|------|
| **A. UTM + 比例尺** ★ | pyproj 轉 UTM 公尺，再 ×10 取整（精度 0.1m） | 精準、業界標準 | 需處理跨帶 |
| B. Web Mercator | 用 EPSG:3857 | 簡單 | 距離失真嚴重 |
| C. 局部平面座標 | 自訂等矩投影 | 短距精準 | 跨城市失真 |
| D. Haversine 距離矩陣 | 不投影，直接算球面距離 | 全球皆準 | 需自行構造距離矩陣（不能用 `add_edge` 走預設） |

#### 決策

採 **方案 A**（UTM + 比例尺 ×10），並在 v1 加入下列保護：

- 偵測使用者輸入的所有點，自動選擇對應 UTM 帶
- 若所有點橫跨超過 1 個 UTM 帶 → 回傳 422 錯誤訊息：「資料跨越多個 UTM 帶，請分區處理」
- 在回應 JSON 同時附上原始經緯度與轉換後座標，方便除錯

---

### 決策 3：時間單位

#### 問題

PyVRP 時間是無單位整數；但使用者填的可能是「08:00 ~ 17:30」這種時刻。

#### 決策

**統一以「分鐘」為時間單位，從當日 00:00 起算**。

| 使用者輸入 | 後端轉換 |
|-----------|---------|
| `08:00` | `480`（分鐘） |
| `17:30` | `1050` |
| 服務時長 `15` 分鐘 | `15` |

行駛時間則由 UTM 距離 / 平均車速（預設 40 km/h，可調）反推為分鐘整數。

---

### 決策 4：API 同步 vs 非同步

#### 決策

**v1 採同步**：`POST /api/solve` 直接阻塞等到 PyVRP 回傳結果。

#### 理由

- 課程展示通常 ≤ 10 秒可解完
- 同步 API 前後端邏輯都簡單
- 若 v2 需要長任務，再升級為「提交任務 → 輪詢結果」模式

#### 防呆

- 預設 `max_runtime=10` 秒
- 前端 `fetch` 設 30 秒 timeout
- 後端用 `asyncio.wait_for` 包裹，超時回傳 504

---

### 決策 5：求解中斷與錯誤處理

| 情境 | HTTP 狀態 | 回應 |
|------|----------|------|
| 輸入欄位缺失或型別錯誤 | 422 | Pydantic 自動產生的詳細錯誤 |
| 跨 UTM 帶 | 422 | `{"error": "cross_utm_zone", "zones": [50, 51]}` |
| 時間窗早 > 晚 | 422 | `{"error": "invalid_time_window", "store": "..."}` |
| 求解超時 | 504 | `{"error": "solver_timeout", "runtime": 10.0}` |
| 找不到可行解 | 200 + `feasible: false` | 仍回傳最佳不可行解供使用者參考 |
| PyVRP 內部錯誤 | 500 | 紀錄 traceback，回傳通用錯誤訊息 |

---

## 3. 資料模型

### 3.1 請求模型（`SolveRequest`）

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class LatLng(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="緯度（WGS84）")
    lng: float = Field(..., ge=-180, le=180, description="經度（WGS84）")

class TimeWindow(BaseModel):
    start: int = Field(..., ge=0, le=1440, description="開始時間（分鐘）")
    end: int = Field(..., ge=0, le=1440, description="結束時間（分鐘）")

class Depot(BaseModel):
    name: str = "Depot"
    location: LatLng
    time_window: TimeWindow

class Store(BaseModel):
    id: str
    name: str
    location: LatLng
    time_window: TimeWindow
    demand: int = Field(..., ge=0, description="需求量（kg 或件數）")
    service_minutes: int = Field(default=10, ge=0)

class VehicleType(BaseModel):
    name: str
    capacity: int = Field(..., gt=0)
    num_available: int = Field(..., gt=0)

class SolverConfig(BaseModel):
    max_runtime_seconds: float = 10.0
    seed: int = 42
    avg_speed_kmh: float = 40.0

class SolveRequest(BaseModel):
    depot: Depot
    stores: List[Store]
    vehicle_types: List[VehicleType]
    config: SolverConfig = SolverConfig()
```

### 3.2 回應模型（`SolveResponse`）

```python
class RouteStop(BaseModel):
    store_id: str            # "depot" 表示倉庫
    name: str
    location: LatLng
    arrival_minutes: int
    departure_minutes: int
    distance_from_prev_km: float
    cumulative_load: int

class VehicleRoute(BaseModel):
    vehicle_index: int
    vehicle_type: str
    stops: List[RouteStop]
    total_distance_km: float
    total_duration_minutes: int
    total_load: int
    capacity: int
    color: str               # 前端繪圖用，後端預先指派

class SolveResponse(BaseModel):
    feasible: bool
    runtime_seconds: float
    iterations: int
    total_distance_km: float
    num_routes_used: int
    routes: List[VehicleRoute]
    warnings: List[str] = []
```

---

## 4. 前端設計

### 4.1 版面配置（Wireframe）

```
┌────────────────────────────────────────────────────────────────────┐
│  PyVRP Web │ 範例資料載入  說明  GitHub                   ⚙ 設定   │ ← Header
├──────────────┬─────────────────────────────────────┬───────────────┤
│              │                                     │               │
│  📍 倉庫      │                                     │  🚚 車輛 1     │
│  ┌─────────┐ │                                     │  ──────────   │
│  │ 名稱    │ │                                     │  容量 100     │
│  │ 經度    │ │                                     │  載重 85      │
│  │ 緯度    │ │                                     │  距離 45.3 km │
│  │ 開放時間 │ │         🗺  Leaflet 地圖              │  ────────    │
│  └─────────┘ │      （倉庫🏠 + 店面📦 + 多色路線）     │  順序：       │
│              │                                     │   1. 店 A     │
│  📦 店面 (5)  │                                     │      08:15   │
│  ┌─────────┐ │                                     │   2. 店 C     │
│  │ + 新增   │ │                                     │      08:42   │
│  └─────────┘ │                                     │   ...         │
│              │                                     │               │
│  🚛 車隊      │                                     │  🚚 車輛 2     │
│  ┌─────────┐ │                                     │  ...          │
│  │ + 新增   │ │                                     │               │
│  └─────────┘ │                                     │               │
│              │                                     │               │
│  ┌─────────┐ │                                     │               │
│  │ 開始計算 │ │                                     │               │
│  └─────────┘ │                                     │               │
├──────────────┴─────────────────────────────────────┴───────────────┤
│ 狀態：求解完成 ✓  │ 總距離 92.4 km │ 用車 2/5 │ 耗時 4.2s │           │ ← Footer
└────────────────────────────────────────────────────────────────────┘
   ←── 320px ──→        ←── 自適應 (≥60%) ──→         ←── 360px ──→
```

### 4.2 互動流程

```
使用者                  前端 JS                  後端 API              PyVRP
  │                      │                        │                    │
  │  填寫表單            │                        │                    │
  │─────────────────────>│                        │                    │
  │                      │  即時驗證              │                    │
  │                      │  (時間窗、座標範圍)    │                    │
  │  點擊「開始計算」     │                        │                    │
  │─────────────────────>│                        │                    │
  │                      │  顯示 Loading          │                    │
  │                      │  POST /api/solve       │                    │
  │                      │───────────────────────>│                    │
  │                      │                        │  WGS84 → UTM       │
  │                      │                        │  建立 Model        │
  │                      │                        │  Model.solve()     │
  │                      │                        │───────────────────>│
  │                      │                        │                    │ 求解
  │                      │                        │<───────────────────│
  │                      │                        │  序列化 Solution   │
  │                      │  200 OK + JSON         │                    │
  │                      │<───────────────────────│                    │
  │                      │  渲染地圖路線          │                    │
  │                      │  渲染車輛明細面板      │                    │
  │  看到結果            │                        │                    │
  │<─────────────────────│                        │                    │
```

### 4.3 視覺風格

| 元素 | 規範 |
|------|------|
| 主色 | `#2E86AB`（PyVRP 藍） |
| 強調色 | `#F18F01`（Action 橘） |
| 倉庫圖示 | 紅色房子 emoji 或自製 SVG |
| 店面圖示 | 編號圓圈，顏色依所屬車輛 |
| 路線顏色 | 預先定義 10 色 palette，循環使用 |
| 字型 | `'Inter', 'Noto Sans TC', sans-serif` |
| 圓角 | 8px |
| 間距 | 8 / 16 / 24 px 三檔 |

---

## 5. 後端關鍵流程程式碼草圖

```python
# webapp/backend/services/solver.py
from pyvrp import Model
from pyvrp.stop import MaxRuntime
from .coord import wgs84_batch_to_utm
from .serializer import solution_to_response

SCALE = 10  # UTM 公尺 ×10 → 0.1 公尺精度

def solve(req: SolveRequest) -> SolveResponse:
    # 1. 統一座標轉換
    all_points = [req.depot.location] + [s.location for s in req.stores]
    utm_points, utm_zone = wgs84_batch_to_utm(all_points)

    # 2. 建立 PyVRP Model
    model = Model()
    depot_xy = utm_points[0]
    depot = model.add_depot(
        x=int(depot_xy.x * SCALE),
        y=int(depot_xy.y * SCALE),
        tw_early=req.depot.time_window.start,
        tw_late=req.depot.time_window.end,
    )

    clients = []
    for store, xy in zip(req.stores, utm_points[1:]):
        c = model.add_client(
            x=int(xy.x * SCALE),
            y=int(xy.y * SCALE),
            demand=store.demand,
            service_duration=store.service_minutes,
            tw_early=store.time_window.start,
            tw_late=store.time_window.end,
        )
        clients.append(c)

    # 3. 加入車型
    for vt in req.vehicle_types:
        model.add_vehicle_type(capacity=vt.capacity, num_available=vt.num_available)

    # 4. 建立距離與時間邊（依平均車速反推）
    speed_m_per_min = req.config.avg_speed_kmh * 1000 / 60
    locations = [depot] + clients
    for i, a in enumerate(locations):
        for j, b in enumerate(locations):
            if i == j:
                continue
            dist_m = euclidean(utm_points[i], utm_points[j])
            duration_min = int(dist_m / speed_m_per_min)
            model.add_edge(a, b,
                           distance=int(dist_m * SCALE),
                           duration=duration_min)

    # 5. 求解
    result = model.solve(stop=MaxRuntime(req.config.max_runtime_seconds),
                         seed=req.config.seed)

    # 6. 序列化回應
    return solution_to_response(result, req, utm_zone, SCALE)
```

---

## 6. 替代方案（已被淘汰但需留紀錄）

### 替代方案 A：用 Streamlit 取代「FastAPI + 自寫前端」

**優點**：開發超快、Python 一把搞定
**淘汰原因**：地圖互動性受限、課程作業展示力較弱、無法精細排版

### 替代方案 B：直接修改 `pyvrp/cli.py` 加 web 介面

**優點**：不用新增目錄
**淘汰原因**：污染 PyVRP 套件本體，未來上游升級時容易衝突

### 替代方案 C：用 Folium 直接從後端產生靜態 HTML

**優點**：完全沒有前端 JS 程式碼
**淘汰原因**：無法即時編輯參數重算，互動性不足

---

## 7. 開放問題（需與指導老師或同組討論）

1. ❓ **是否需要支援存檔/讀檔**？若要，採 JSON 還是 CSV？
2. ❓ **示範資料的地點選擇**？建議用台北市中山區 10 家便利商店真實座標
3. ❓ **車隊圖示**？要不要每台車有不同的卡通圖示，或統一用顏色區分即可
4. ❓ **時間單位**？除了 24 小時制分鐘，是否需要支援「相對時間」（如「出發後 30 分鐘內」）
5. ❓ **是否要在前端顯示求解過程的迭代統計**（best cost vs iteration 折線圖）
