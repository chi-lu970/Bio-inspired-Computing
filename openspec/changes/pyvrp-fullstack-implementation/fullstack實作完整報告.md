# PyVRP 全端視覺化操作介面 — 實作完整報告

> **變更 ID**：`pyvrp-fullstack-implementation`
> **作者**：alex.lu
> **完成日期**：2026-04-10
> **課程**：Bio-inspired Computing（仿生計算）

---

## 目錄

1. [動機與背景](#1-動機與背景)
2. [系統整體架構](#2-系統整體架構)
3. [對原作者程式碼的分析與改動](#3-對原作者程式碼的分析與改動)
4. [後端實作細節](#4-後端實作細節)
5. [前端實作細節](#5-前端實作細節)
6. [解決的關鍵技術問題](#6-解決的關鍵技術問題)
7. [範例資料設計](#7-範例資料設計)
8. [錯誤處理與健壯性設計](#8-錯誤處理與健壯性設計)
9. [啟動方式](#9-啟動方式)
10. [成果驗收](#10-成果驗收)

---

## 1. 動機與背景

### 1.1 原始 PyVRP 的使用痛點

PyVRP 是一套以 **Hybrid Genetic Search（HGS，混合遺傳搜尋）** 為核心的 Vehicle Routing Problem（VRP，車輛路線問題）求解引擎，底層以 C++ 實作，Python 提供高層 API。然而，原始套件僅能透過 Python 程式碼操作：

| 痛點 | 影響 |
|------|------|
| 必須手寫 Python 程式呼叫 `Model` API | 非工程師（物流人員、教師、學生）完全無法使用 |
| WGS84 經緯度需自行轉換成 UTM 平面座標才能輸入 | 所有使用者都必須額外處理地理座標轉換 |
| 求解結果是 Python 物件（`Route`、`Solution`），無任何圖形化呈現 | 難以直覺理解配送路線與效果 |
| 想驗證演算法效果需每次自寫 plotting 程式碼 | 研究者、教學展示皆不便 |
| 無法即時調整參數後比較結果 | 課堂展示、業務試算受限 |

### 1.2 實作目標

將 PyVRP 包裝成「**填表單 → 點按鈕 → 看地圖**」的零程式碼操作介面，使 VRP 求解能力從「Python 開發者限定」擴展到物流規劃師、教師、學生與決策者。

### 1.3 學術連結

本課程主題「仿生計算（Bio-inspired Computing）」，PyVRP 使用的 HGS 演算法正是仿生計算的代表——透過模擬生物演化的**遺傳演算法（Genetic Algorithm, GA）** 搭配**局部搜尋（Local Search）**，反覆疊代改良解的品質。透過本次視覺化前端，可直接在地圖上呈現演算法輸出的最佳配送路線，讓觀念由抽象具象化。

---

## 2. 系統整體架構

### 2.1 分層架構圖

```
┌──────────────────────────────────────────────────────────────────┐
│                      展示層（Presentation）                        │
│         HTML  +  CSS  +  Vanilla JS（3 模組）  +  Leaflet.js      │
│              （無框架、無建置工具、CDN 引入、ES Module）             │
└──────────────────────────────────┬───────────────────────────────┘
                                   │  fetch() / JSON（同源請求）
┌──────────────────────────────────▼───────────────────────────────┐
│                        API 層（FastAPI）                           │
│   路由定義 / Pydantic 驗證 / CORS / OpenAPI 自動文件               │
│   ThreadPoolExecutor（非同步執行同步阻塞求解）                      │
│   Semaphore（限制同時只允許一個求解請求）                           │
└──────────────────────────────────┬───────────────────────────────┘
                                   │  Python function call
┌──────────────────────────────────▼───────────────────────────────┐
│                      服務層（Service Layer）                       │
│   ┌──────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│   │  座標轉換器   │  │  VRP 模型建構層   │  │   結果序列化器    │  │
│   │  coord.py    │  │  solver.py       │  │  serializer.py   │  │
│   │  pyproj 庫   │  │  PyVRP Model API │  │  Pydantic models │  │
│   └──────────────┘  └──────────────────┘  └──────────────────┘  │
└──────────────────────────────────┬───────────────────────────────┘
                                   │  GA + Local Search + HGS
┌──────────────────────────────────▼───────────────────────────────┐
│                       求解引擎（PyVRP）                            │
│           GeneticAlgorithm + LocalSearch + SREX crossover         │
│           TimedNoImprovement 停止策略                             │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 目錄結構（實際交付）

```
Bio-inspired-Computing/
├── pyvrp/                          # 原作者 PyVRP 套件（不修改）
├── webapp/                         # ★ 本次新增
│   ├── __init__.py
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI 應用入口、CORS、靜態掛載
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py           # GET /api/health, POST /api/solve
│   │   │   └── schemas.py          # Pydantic 請求/回應模型（8 個 class）
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── coord.py            # WGS84 ↔ UTM 座標轉換（pyproj）
│   │   │   ├── solver.py           # PyVRP Model 整合 + GA 手動組裝
│   │   │   ├── serializer.py       # PyVRP Result → SolveResponse
│   │   │   └── exceptions.py       # 5 種自訂例外
│   │   └── examples/
│   │       ├── taipei_demo.json        # 日班範例（16 店）
│   │       └── taipei_711_night.json   # 大夜班範例（16 店）
│   └── frontend/
│       ├── index.html              # 單頁應用主框架
│       ├── css/
│       │   └── style.css           # CSS 變數 + Grid 版面 + 元件樣式
│       ├── js/
│       │   ├── api.js              # fetch 封裝、AbortController、逾時
│       │   ├── map.js              # Leaflet 地圖、圖層管理、高亮互動
│       │   └── form.js             # 表單邏輯、驗證、序列化、結果渲染
│       └── examples/
│           ├── taipei_demo.json        # 前端側範例（與 backend 同步）
│           └── taipei_711_night.json
├── run_server.py                   # ★ 啟動腳本（解決 sys.path 衝突）
└── openspec/changes/
    └── pyvrp-fullstack-implementation/
        ├── proposal.md             # 需求提案
        ├── design.md               # 技術設計
        └── 實作完整報告.md          # 本文件
```

### 2.3 技術選型決策

| 層 | 選擇 | 理由 |
|----|------|------|
| 前端框架 | **Vanilla JS + HTML + CSS（ES Module）** | 課程規模不需重型工具鏈；無需 webpack/npm；零建置流程；3 個模組檔案即可完成 |
| 地圖套件 | **Leaflet.js 1.9.4（CDN）** | 開源、免 API key、tile 使用 CartoCDN、文件完整 |
| 後端框架 | **FastAPI** | Python 原生 async/await；Pydantic 型別驗證；自動產生 OpenAPI 互動文件；比 Flask 更現代 |
| 座標轉換 | **pyproj** | 地理運算事實標準；支援 EPSG 投影切換；Transformer 建立成本透過快取攤薄 |
| 求解整合 | **PyVRP 高層 Model API** | 不直接操作 C++ 層；降低耦合；便於替換底層版本 |
| 資料格式 | **JSON** | 前後端共通；Pydantic 自動序列化/反序列化；人眼可讀易除錯 |

---

## 3. 對原作者程式碼的分析與改動

### 3.1 原作者程式碼總結

原作者（PyVRP 開源社群）的程式碼架構如下：

| 模組 | 職責 |
|------|------|
| `pyvrp/Model.py` | 高層 Python API：建立倉庫、客戶、車型、邊，呼叫 C++ 求解 |
| `pyvrp/GeneticAlgorithm.py` | HGS 主迴圈：選擇、交叉、局部搜尋、種群管理 |
| `pyvrp/Population.py` | 種群（Population）與子種群（SubPopulation）管理 |
| `pyvrp/PenaltyManager.py` | 動態調整違反容量／時間窗的懲罰係數 |
| `pyvrp/crossover/selective_route_exchange.py` | SREX 交叉算子 |
| `pyvrp/search/LocalSearch.py` | 局部搜尋框架，掛載多種鄰域算子 |
| `pyvrp/search/neighbourhood.py` | `compute_neighbours` 計算鄰域圖 |
| `pyvrp/stop/` | 停止條件：`MaxRuntime`、`MaxIterations`、`NoImprovement`、`TimedNoImprovement` |
| `pyvrp/cli.py` | 命令列介面，讀取 VRPLIB 格式求解 |

### 3.2 本次對原作者程式碼的改動策略

**核心原則：不修改 PyVRP 套件本體，僅作為函式庫呼叫。**

原作者程式碼零修改，所有新功能透過 `webapp/` 目錄新增，與 `pyvrp/` 完全隔離。

### 3.3 整合時發現的問題與解法

#### 問題 1：本地 `pyvrp/` 目錄遮蔽已安裝 wheel

**現象**：Python 預設從 `sys.path` 優先載入當前目錄，根目錄的 `pyvrp/` 原始碼（未編譯的純 Python，缺少 C++ 擴充）會蓋掉 `.venv` 中已安裝的 wheel 版本，導致 `import pyvrp` 失敗或功能殘缺。

**解法**（`webapp/backend/main.py` 第 11–21 行）：
```python
import sys
from pathlib import Path as _Path

_venv_site = _Path(__file__).parents[2] / ".venv" / "Lib" / "site-packages"
if _venv_site.exists() and str(_venv_site) not in sys.path:
    sys.path.insert(0, str(_venv_site))  # 強制 venv 版本優先
```

另外提供 `run_server.py`，在啟動前完整整理 `sys.path`，同時移除 CWD 的干擾並確保 venv 在最前。

#### 問題 2：`Model.solve()` API 的停止策略選擇

**原作者提供的方式**：直接呼叫 `model.solve(stop=MaxRuntime(...))`，由高層 API 包裝整個 GA 組裝流程。

**本次採用的方式**：手動組裝 GA（`GeneticAlgorithm` + `LocalSearch` + `Population`），使用 `TimedNoImprovement` 作為停止條件。

**原因**：
1. 原始 `model.solve()` 使用的 `nb_granular`（鄰域大小）預設值 20，對小問題（< 30 站）意味著幾乎全圖搜尋，每次局部搜尋耗時過長，迭代速度極慢。
2. 透過手動組裝，可將 `nb_granular` 固定為 7（`min(7, 最多客戶數 - 1)`），讓局部搜尋保持可控的速度。
3. `TimedNoImprovement` 結合「無改善迭代上限（500 次）」與「總執行時間上限」，比單純 `MaxRuntime` 更早停止在解質穩定時，也避免無限等待。

```python
# solver.py — 關鍵改動：手動組裝 GA
NB_GRANULAR = 7  # 固定鄰域大小，避免小問題搜尋空間爆炸

nb_granular = min(NB_GRANULAR, max(1, data.num_clients - 1))
neighbours = compute_neighbours(data, NeighbourhoodParams(nb_granular=nb_granular))
ls = LocalSearch(data, rng, neighbours)
for op in NODE_OPERATORS:
    ls.add_node_operator(op(data))
for op in ROUTE_OPERATORS:
    ls.add_route_operator(op(data))

pm = PenaltyManager()
pop = Population(bpd, PopulationParams())
init = [Solution.make_random(data, rng) for _ in range(pop_params.min_pop_size)]
algo = GeneticAlgorithm(data, pm, rng, pop, ls, srex, init)

stop = TimedNoImprovement(max_iterations=500, max_runtime=req.config.max_runtime_seconds)
result = algo.run(stop)
```

#### 問題 3：PyVRP 使用整數座標，使用者輸入 WGS84 浮點經緯度

**原作者設計**：`Model.add_depot()` / `add_client()` 接受整數 `x, y`，假設呼叫者自行提供平面座標。

**本次整合**：新增 `coord.py`，透過 `pyproj` 將 WGS84 轉換為 UTM 平面座標（公尺），再乘以比例尺 `SCALE = 10`（0.1 公尺精度）後取整傳入 PyVRP：

```python
SCALE = 10  # UTM 公尺 ×10 → 精度 0.1m

dist_m = euclidean(utm_points[i], utm_points[j])
model.add_edge(a, b,
    distance=int(round(dist_m * SCALE)),   # 整數距離
    duration=max(1, int(round(dist_m / speed_m_per_min)))  # 整數分鐘
)
```

---

## 4. 後端實作細節

### 4.1 FastAPI 應用入口（`main.py`）

- 建立 `FastAPI` 應用，設定 CORS（僅允許 `localhost:8000` 同源）
- 以 `include_router(router)` 掛載 API 路由（前綴 `/api`）
- 以 `StaticFiles(html=True)` 掛載前端目錄（`/`），API 路由在前，靜態檔在後，確保 API 端點不被靜態檔案攔截

### 4.2 Pydantic 資料模型（`schemas.py`）

共定義 **8 個模型**，分為請求與回應兩組：

**請求模型**

| 模型 | 欄位 | 說明 |
|------|------|------|
| `LatLng` | `lat`（-90~90）, `lng`（-180~180） | WGS84 經緯度，有範圍驗證 |
| `TimeWindow` | `start`, `end`（0~1440 分鐘）| `model_validator` 確保 end > start |
| `Depot` | `name`, `location`, `time_window` | 倉庫定義 |
| `Store` | `id`, `name`, `location`, `time_window`, `demand`, `service_minutes` | 客戶/店面定義 |
| `VehicleType` | `name`, `capacity`（>0）, `num_available`（>0） | 車型定義 |
| `SolverConfig` | `max_runtime_seconds`（1~300）, `seed`, `avg_speed_kmh` | 求解器設定 |
| `SolveRequest` | `depot`, `stores`（≥1）, `vehicle_types`（≥1）, `config` | 完整求解請求，`model_validator` 驗證店面 ID 不重複 |

**回應模型**

| 模型 | 重要欄位 | 說明 |
|------|---------|------|
| `RouteStop` | `store_id`, `name`, `location`, `arrival_minutes`, `departure_minutes`, `wait_minutes`, `distance_from_prev_km`, `cumulative_load` | 單一停靠點（含倉庫起訖）|
| `VehicleRoute` | `vehicle_index`, `vehicle_type`, `color`, `stops`, `total_distance_km`, `total_duration_minutes`, `total_load`, `capacity` | 單車完整行程 |
| `SolveResponse` | `feasible`, `runtime_seconds`, `iterations`, `total_distance_km`, `num_routes_used`, `routes`, `warnings` | 求解結果 |
| `ErrorResponse` | `error`（錯誤代碼）, `message`（中文說明）| 統一錯誤格式 |

### 4.3 API 路由（`routes.py`）

**GET `/api/health`**：健康檢查，回傳服務狀態與 PyVRP 版本。

**POST `/api/solve`**：VRP 求解主端點。

關鍵設計：
1. **ThreadPoolExecutor（8 workers）**：PyVRP 求解為同步阻塞操作，放入 executor 避免阻塞 FastAPI 的 event loop
2. **asyncio.Semaphore(1)**：同時只允許一個求解請求，後續請求直接收到 503，避免並發求解造成系統卡死
3. **分層錯誤處理**：依例外型別分別回傳 422（輸入問題）、504（超時）、500（內部錯誤）

```python
# 若有另一個求解正在執行，立即拒絕
if _solver_semaphore.locked():
    raise HTTPException(status_code=503, detail={...})

async with _solver_semaphore:
    result = await loop.run_in_executor(_executor, solver_svc.solve, req)
```

### 4.4 座標轉換層（`coord.py`）

- `wgs84_to_utm(lat, lng)` → 單點 WGS84 轉 UTM（自動選帶）
- `wgs84_batch_to_utm(points)` → 批次轉換，並驗證所有點屬於同一 UTM 帶，跨帶時拋出 `CrossUtmZoneError`
- `euclidean(a, b)` → UTM 平面歐式距離（公尺）
- Transformer 物件依 EPSG 代碼快取，避免重複建立的開銷

UTM 帶偵測邏輯：
```python
def _utm_zone_for_lng(lng: float) -> int:
    return int((lng + 180.0) / 6.0) + 1  # 1~60
```

北半球（台灣）使用 EPSG `32600 + zone`（326XX 系列）。

### 4.5 求解器整合層（`solver.py`）

**`_check_construction_feasibility()`**：快速預檢，若總需求 > 總容量，直接拋出 `InfeasibleByConstructionError`，不進入耗時的 GA 流程。

**`_build_model()`**：
1. 將倉庫 UTM 座標 × SCALE 取整後呼叫 `model.add_depot()`，傳入時間窗（分鐘整數）
2. 對每個店面同樣轉換後呼叫 `model.add_client()`，傳入需求量與服務時長
3. 對每種車型呼叫 `model.add_vehicle_type()`
4. 用 O(N²) 雙重迴圈對所有節點對建立邊（`model.add_edge()`），距離採 UTM 歐式，行駛時間由距離 / 平均車速推算（最小 1 分鐘）

**行駛時間反推公式**：
```
speed_m_per_min = avg_speed_kmh × 1000 / 60
duration_min = max(1, round(dist_m / speed_m_per_min))
```

### 4.6 結果序列化層（`serializer.py`）

**顏色指派**：預先定義 10 色 palette（與前端 `map.js` 相同順序），依車輛索引循環使用，確保前後端顏色一致。

**每站時間計算**（PyVRP 僅提供訪問順序，各站時間需手動推算）：
```
出發時間 T₀ = 倉庫 tw_early（倉庫開放即出發）
for each stop:
    arrival = prev_departure + haversine距離轉分鐘
    effective_start = max(arrival, stop.tw_early)  # 提早到需等待
    wait = effective_start - arrival
    departure = effective_start + service_minutes
```

**距離計算**：序列化時不再使用 UTM 座標，改用 Haversine 球面距離公式，直接從 WGS84 經緯度計算（精度已足夠，且避免再次投影）：
```python
def _haversine_km(a, b):
    R = 6371.0088  # 地球平均半徑 km
    # ... 標準 Haversine 公式
```

---

## 5. 前端實作細節

### 5.1 版面配置

採 CSS Grid 三欄式 + Header/Footer 的五區佈局：

```
┌────────────────────────────────────────────────────────────────────┐
│  PyVRP Web │ 📂 載入範例 ▾                         API 文件         │ ← Header (52px)
├──────────────┬─────────────────────────────────────┬───────────────┤
│ 🏠 倉庫      │                                     │ 📋 路線詳細資訊  │
│  名稱/座標   │                                     │               │
│  時間窗      │         Leaflet 地圖                 │  🚚 車輛 1     │
│              │      (CartoCDN Voyager 底圖)          │  ─────────    │
│ 📦 店面(16) │      倉庫🏠 + 編號圓圈 + 多色路線      │  距離/載重    │
│  [動態列表]  │      + 方向箭頭                       │  停靠點清單   │
│              │                                     │               │
│ 🚛 車隊設定  │       求解中 spinner overlay          │  🚚 車輛 2    │
│  [動態列表]  │                                     │  ...          │
│              │       Toast 錯誤/警告提示             │               │
│ ⚙️ 求解設定  │                                     │               │
│              │                                     │               │
│  [開始計算]  │                                     │               │
│  [取消計算]  │                                     │               │
├──────────────┴─────────────────────────────────────┴───────────────┤
│ 狀態：求解完成 ✓ │ 總距離：92.4 km │ 使用車輛：3 台 │ 求解耗時：4.2s │ ← Footer (36px)
└────────────────────────────────────────────────────────────────────┘
    320px              中央自適應（flex:1）                  360px
```

### 5.2 JavaScript 模組設計（ES Module 架構）

三個模組透過 `window.PyVRP` 命名空間互通：

| 模組 | 職責 | 對外暴露 |
|------|------|---------|
| `api.js` | HTTP 請求封裝、AbortController、前端逾時 | `window.PyVRP.api.solve()`, `cancelSolve()`, `loadExample()` |
| `map.js` | Leaflet 地圖初始化、圖層管理、渲染、高亮 | `window.PyVRP.map.render()`, `previewLocations()`, `highlightRoute()`, `clearAll()` |
| `form.js` | 表單驗證、序列化、UI 狀態管理、結果渲染 | 無（入口模組） |

**載入順序**（`index.html`）：`api.js` → `map.js` → `form.js`，後者依賴前兩者。

### 5.3 表單功能（`form.js`）

**即時驗證**：
- 倉庫/店面緯度 (-90~90)、經度 (-180~180)：`input` 事件觸發，不合法顯示紅框 + 錯誤訊息
- 時間窗：`end ≤ start` 時顯示警告
- 「開始計算」按鈕：任何驗證錯誤、店面清單空、車型清單空、倉庫座標未填，均自動 disabled

**動態新增/刪除**：
- 店面（Store）：點擊「＋ 新增店面」動態插入表單卡片，每張卡片含完整驗證邏輯與刪除按鈕
- 車型（VehicleType）：同上機制
- ID 自動生成：`S001`, `S002`, ... 遞增序號

**區塊縮合（Collapsible）**：點擊 section card 標題即可摺疊/展開，節省畫面空間。

**範例資料載入**：Header 提供下拉選單，點選後 fetch `/examples/*.json` → 填入表單所有欄位 → 地圖預覽所有地點（在按下「開始計算」前即可看到位置分布）。

**表單序列化（`collectFormData()`）**：
- 時間格式轉換：`"HH:MM"` ↔ 分鐘整數（`timeToMin` / `minToTime`）
- 組裝成符合 `SolveRequest` schema 的 JSON 物件

**必填欄位檢核（`findFirstEmptyField()`）**：提交前二次確認所有必填欄位非空，若有遺漏則展開所在的 section card、捲動到目標欄位並標記錯誤。

**求解主流程（`onSolve()`）**：
1. 必填檢核
2. 序列化表單資料
3. 顯示地圖 loading overlay，切換「開始計算」→「取消計算」按鈕
4. 呼叫 `window.PyVRP.api.solve(payload)`
5. 成功：渲染地圖 + 右側結果面板 + 更新狀態列
6. 失敗：依錯誤類型顯示 Toast 訊息
7. 不論成功/失敗：隱藏 loading、還原按鈕狀態

### 5.4 API 封裝（`api.js`）

**AbortController 取消機制**：
- 每次呼叫 `solve()` 建立新 controller，若前一個請求仍在等待先行 abort
- 使用者點「取消計算」呼叫 `cancelSolve()` → 取消 fetch

**前端逾時保護**：
- 前端 timeout = `max_runtime_seconds × 3 + 10` 秒
- 正常情況由後端 `TimedNoImprovement` 控制停止，前端 timeout 僅作最後保障

**統一錯誤格式**：後端回傳 4xx/5xx 時解析 `detail.error` 與 `detail.message`，以相同格式拋出，供 `form.js` 統一處理。

### 5.5 地圖視覺化（`map.js`）

**底圖**：CartoCDN Voyager（淡色系、無過多細節干擾路線呈現）。

**圖層分離**（各自獨立 `LayerGroup`）：
| 圖層 | 內容 |
|------|------|
| `depotLayer` | 倉庫圖示（紅色房子形 divIcon） |
| `storeLayer` | 店面圓圈 marker（編號 + 路線顏色） |
| `routeLayer` | 路線折線（每條車輛一種顏色） |
| `arrowLayer` | 方向箭頭（每段線段中點，顯示行進方向） |
| `previewLayer` | 範例載入後的預覽 marker（未求解時） |

**自訂圖示**：全部使用 `L.divIcon` CSS-in-JS 風格，無需外部圖片資源：
- **倉庫**：旋轉 45° 的紅色氣球形（`border-radius: 50% 50% 50% 0`），房屋 emoji
- **已服務店面**：彩色實心圓 + 白色數字（依車輛顏色染色）+ 外圈白色 box-shadow
- **未服務店面**（不可行解時）：灰色圓圈 + 虛線邊框
- **方向箭頭**：三角形 `▲` + CSS rotate 對準方向

**Popup 資訊**：點擊倉庫顯示開放時間，點擊店面顯示抵達/離開時間、等待時間、距上站距離。

**路線互動**：
- 點擊地圖折線：高亮該條路線（其他路線半透明），右側面板對應 card 閃爍並捲動到可見位置
- 點擊右側面板 card：高亮對應路線並 fitBounds
- 點擊地圖空白處：重置所有路線透明度
- 高亮動畫：`card-flash` 使用 CSS `--flash-color` 自訂屬性傳入路線顏色，每輛車閃爍自己的顏色

**未服務店面**：不可行解時，未被任何路線訪問的店面以灰色顯示，popup 標示「未被服務」。

### 5.6 右側結果面板（`form.js` renderResults）

每輛車一張 route card，包含：
- 顏色點 + 車型名稱 + 車輛編號
- 統計：總距離、總載重/容量、滿載百分比、總時長
- 停靠點清單：每站顯示站名、抵達/離開時間、等待時間（若有）、距上站距離

不可行解時，面板頂部顯示黃色警告橫幅。

### 5.7 狀態列（Footer）

即時更新 4 個狀態欄位：

| 欄位 | 說明 |
|------|------|
| 狀態 | 待機 / 求解中… / 求解完成 ✓（綠）/ 求解失敗（紅）/ 不可行解 ⚠ |
| 總距離 | 所有路線總 km |
| 使用車輛 | 實際使用台數 |
| 求解耗時 | 後端回報的 runtime 秒數 |

---

## 6. 解決的關鍵技術問題

### 6.1 sys.path 衝突問題

**問題**：PyVRP 以 Python + C++ 混合實作，根目錄的 `pyvrp/` 純 Python 原始碼（缺少編譯後的 `.pyd` 擴充）被 Python 優先載入，造成 `ImportError` 或功能不完整。

**解法**：在所有 import 之前，強制將 `.venv/Lib/site-packages` 插到 `sys.path[0]`。同時提供 `run_server.py` 啟動腳本，確保啟動環境乾淨。

### 6.2 GA 鄰域大小導致小問題求解過慢

**問題**：PyVRP 預設 `nb_granular=20`（每個節點考慮 20 個最近鄰居），對 16 個客戶的問題等同全圖搜尋，每次局部搜尋幾乎遍歷所有可能，迭代極慢，10 秒內迭代次數極少，解質差。

**解法**：固定 `NB_GRANULAR = 7`，對小問題以 `min(7, num_clients - 1)` 限制，讓每次局部搜尋快速完成，相同時間內可迭代更多次，解質顯著提升。

### 6.3 座標精度問題

**問題**：PyVRP 使用整數座標。若直接把 WGS84 度數乘以某倍數取整，台灣範圍（約 120~122°E, 22~25°N）精度極差；若使用 Web Mercator（EPSG:3857）又有嚴重的距離失真。

**解法**：
1. 使用 pyproj 轉換 WGS84 → UTM（公尺級精度，台灣位於 UTM 50N/51N 帶）
2. UTM 公尺值乘以比例尺 10 再取整，提供 0.1 公尺精度
3. 偵測跨帶情況，拋出 422 錯誤要求使用者分區處理

### 6.4 各站時間計算

**問題**：PyVRP `Route` 物件只提供訪問節點的索引順序，不直接提供各站抵達/離開時間。

**解法**：在 `serializer.py` 中手動模擬時間推算（walk-through），依序計算每站的抵達時間、等待時間（若早於時間窗開放）、出發時間，最後回到倉庫的時間。

### 6.5 前端與後端顏色一致性

**問題**：後端 `serializer.py` 需要先指派顏色給每條路線，前端地圖再依 `route.color` 繪製，兩邊必須一致。

**解法**：後端 palette 和前端 `PALETTE` 陣列使用相同的 10 色清單，均依 `vehicle_index % 10` 循環，後端在 `SolveResponse` 中每條路線帶上 `color` 欄位，前端地圖完全信賴此值，不自行計算。

### 6.6 並發求解造成系統卡死

**問題**：若使用者多次快速點擊「開始計算」，多個求解任務同時進入 executor，PyVRP 的 C++ 核心佔用大量 CPU，系統可能無回應。

**解法**：`asyncio.Semaphore(1)` 確保同時只有一個求解在執行，後續請求立即收到 503 錯誤；前端使用 AbortController，新請求發出前先 abort 舊請求。

---

## 7. 範例資料設計

### 7.1 日班配送範例（`taipei_demo.json`）

| 設定 | 值 |
|------|-----|
| 場景 | 7-ELEVEN 台北市日班補貨 |
| 倉庫 | 統一超商台北物流中心（台北車站附近，25.0478°N, 121.517°E）|
| 出發時間窗 | 09:30–13:00（570–780 分鐘）|
| 店面數 | 16 家，分布台北市各區（新莊、三重、蘆洲、士林、北投、中山、大安、內湖、松山、信義、板橋、中和、文山、南港等）|
| 店面時間窗 | 10:00–13:00（600–780 分鐘）|
| 總需求量 | 383 單位 |
| 車型 | 大型貨車（容量 140，2 台）+ 中型貨車（容量 80，4 台） |
| 總容量 | 600 單位 |
| 平均車速 | 28 km/h（市區白天車速） |
| 求解時限 | 10 秒 |

### 7.2 大夜班配送範例（`taipei_711_night.json`）

| 設定 | 值 |
|------|-----|
| 場景 | 7-ELEVEN 台北市大夜班補貨 |
| 倉庫 | 同上，00:30 出車 |
| 出發時間窗 | 00:30–07:00（30–420 分鐘）|
| 店面數 | 16 家，分布士林、中山、北投、內湖、南港、信義、大安、文山、大同、萬華、中正等區 |
| 店面時間窗 | 01:00–06:00（60–360 分鐘）|
| 總需求量 | 408 單位 |
| 車型 | 大型貨車（容量 140，1 台）+ 中型貨車（容量 80，4 台） |
| 總容量 | 460 單位 |
| 平均車速 | 42 km/h（深夜車速較快）|
| 求解時限 | 30 秒（大夜班窗口較緊，需更長求解時間）|

---

## 8. 錯誤處理與健壯性設計

### 8.1 自訂例外體系（`exceptions.py`）

所有例外繼承 `WebAppError`，統一提供 `to_dict()` 轉 API 回應格式：

| 例外類別 | 代碼 | 觸發情況 | HTTP 狀態 |
|----------|------|---------|-----------|
| `CrossUtmZoneError` | `cross_utm_zone` | 店面/倉庫跨越多個 UTM 帶 | 422 |
| `InvalidTimeWindowError` | `invalid_time_window` | 時間窗 end ≤ start（補強 Pydantic 跨欄位驗證）| 422 |
| `InfeasibleByConstructionError` | `infeasible_by_construction` | 總需求 > 總容量，明顯無解 | 422 |
| `SolverTimeoutError` | `solver_timeout` | 求解超過時限 | 504 |
| `SolverInternalError` | `solver_internal_error` | PyVRP 內部拋出異常 | 500 |

### 8.2 不可行解處理

找不到完全可行解時（如時間窗過緊），PyVRP 仍回傳「最佳不可行解」：
- 後端：`feasible: false` + `warnings: ["未能在時限內找到可行解，回傳最佳不可行解"]`
- 前端地圖：正常繪製路線，未被訪問的店面以灰色顯示
- 前端面板：顯示黃色警告橫幅
- 狀態列：以橘色顯示「不可行解 ⚠」

### 8.3 前端 Toast 通知系統

- 紅色 Toast：輸入驗證錯誤、網路錯誤、求解失敗
- 黃色 Toast（`.warn`）：不可行解警告、前端超時、求解器忙碌
- 5 秒後自動消失，重複觸發重置計時器

---

## 9. 啟動方式

### 環境需求

- Python 3.11（需與 PyVRP wheel 版本一致）
- 已安裝 `fastapi`、`uvicorn`、`pyproj`

### 啟動指令

```bash
# 方式 1（推薦）：使用 run_server.py
uv run --python 3.11 python run_server.py

# 方式 2：直接使用 uvicorn
uv run --python 3.11 uvicorn webapp.backend.main:app --port 8000
```

### 存取頁面

| 路徑 | 說明 |
|------|------|
| `http://localhost:8000/` | 前端操作介面 |
| `http://localhost:8000/docs` | FastAPI 自動產生的 OpenAPI 互動文件（Swagger UI） |
| `http://localhost:8000/api/health` | 健康檢查 API |

---

## 10. 成果驗收

### 功能完成清單

| 項目 | 狀態 |
|------|------|
| 使用者打開 `http://localhost:8000` 看到完整表單頁面 | ✅ |
| 可新增 1 個倉庫 + 多個店面（支援動態新增/刪除）| ✅ |
| 可設定多種車型（動態新增/刪除）| ✅ |
| 前端即時驗證（座標範圍、時間窗順序、必填欄位）| ✅ |
| 一鍵載入範例資料（日班 / 大夜班）並預覽地圖 | ✅ |
| 點擊「開始計算」後求解並在地圖顯示多色路線 | ✅ |
| 路線折線帶方向箭頭 | ✅ |
| 右側面板顯示每台車的停靠順序、距離、抵達時間、載重 | ✅ |
| 點擊地圖路線/右側卡片互動高亮 | ✅ |
| 不可行解友善提示（灰色未服務店面 + 警告橫幅）| ✅ |
| 求解過程顯示 loading overlay + 可取消 | ✅ |
| 狀態列即時更新（狀態、距離、車輛數、耗時）| ✅ |
| 後端 `/docs` 自動產生 OpenAPI 互動文件 | ✅ |
| Logo 回首頁（清除所有資料）並有確認對話框 | ✅ |
| 區塊縮合/展開節省面板空間 | ✅ |
| 並發保護（同時只允許一個求解）| ✅ |

### 已知限制（Out of Scope）

- 不支援多倉庫（PyVRP 本身限制）
- 不支援行動裝置 RWD
- 不支援 VRPLIB 格式匯入
- 不支援 GA 收斂動畫（Stretch Goal，未實作）
- 不提供雲端部署

---

## 附錄：API 規格摘要

### POST /api/solve

**Request Body**
```json
{
  "depot": {
    "name": "統一超商 台北物流中心",
    "location": { "lat": 25.0478, "lng": 121.5170 },
    "time_window": { "start": 570, "end": 780 }
  },
  "stores": [
    {
      "id": "S001",
      "name": "7-ELEVEN 新莊思源店",
      "location": { "lat": 25.0438, "lng": 121.4412 },
      "time_window": { "start": 600, "end": 780 },
      "demand": 20,
      "service_minutes": 12
    }
  ],
  "vehicle_types": [
    { "name": "大型貨車", "capacity": 140, "num_available": 2 }
  ],
  "config": {
    "max_runtime_seconds": 10,
    "avg_speed_kmh": 28,
    "seed": 42
  }
}
```

**Response Body（200 OK）**
```json
{
  "feasible": true,
  "runtime_seconds": 8.234,
  "iterations": 412,
  "total_distance_km": 87.356,
  "num_routes_used": 3,
  "routes": [
    {
      "vehicle_index": 0,
      "vehicle_type": "大型貨車",
      "color": "#E63946",
      "stops": [
        {
          "store_id": "depot",
          "name": "統一超商 台北物流中心",
          "location": { "lat": 25.0478, "lng": 121.517 },
          "arrival_minutes": 570,
          "departure_minutes": 570,
          "wait_minutes": 0,
          "distance_from_prev_km": 0.0,
          "cumulative_load": 0
        },
        {
          "store_id": "S001",
          "name": "7-ELEVEN 新莊思源店",
          "location": { "lat": 25.0438, "lng": 121.4412 },
          "arrival_minutes": 595,
          "departure_minutes": 612,
          "wait_minutes": 5,
          "distance_from_prev_km": 7.432,
          "cumulative_load": 20
        }
      ],
      "total_distance_km": 42.1,
      "total_duration_minutes": 187,
      "total_load": 138,
      "capacity": 140
    }
  ],
  "warnings": []
}
```
