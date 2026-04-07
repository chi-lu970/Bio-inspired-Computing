# 實作任務清單：PyVRP 全端視覺化操作介面

> **變更 ID**：`pyvrp-fullstack-implementation`
> **配套文件**：`proposal.md` / `design.md`
> **使用方式**：完成任務時將 `[ ]` 改為 `[x]`

---

## 階段總覽

| 階段 | 名稱 | 任務數 | 預估難度 | 依賴 |
|------|------|--------|----------|------|
| **0** | 環境準備 | 4 | ★☆☆ | — |
| **1** | 後端基礎架構 | 6 | ★★☆ | 階段 0 |
| **2** | 座標轉換與求解整合 | 7 | ★★★ | 階段 1 |
| **3** | API 端點實作 | 5 | ★★☆ | 階段 2 |
| **4** | 前端基礎頁面 | 5 | ★★☆ | 階段 0 |
| **5** | 輸入表單實作 | 7 | ★★☆ | 階段 4 |
| **6** | 地圖視覺化 | 6 | ★★★ | 階段 4 |
| **7** | 前後端整合 | 5 | ★★☆ | 階段 3、5、6 |
| **8** | 示範資料與文件 | 4 | ★☆☆ | 階段 7 |
| **9** | 驗收與優化 | 5 | ★★☆ | 階段 8 |

---

## 階段 0：環境準備

- [x] **0.1** 建立 `webapp/` 目錄結構（`backend/`, `frontend/`, `backend/api/`, `backend/services/`, `backend/examples/`, `frontend/css/`, `frontend/js/`, `frontend/assets/`）
- [x] **0.2** 在 `pyproject.toml` 的 `[tool.poetry.group.webapp.dependencies]`（optional group）新增：`fastapi ^0.109`、`uvicorn[standard] ^0.27`、`pyproj ^3.6`、`pydantic ^2.5`
- [ ] **0.3** 執行 `poetry install --with webapp` 確認依賴可正常安裝（**待使用者環境執行**）
- [x] **0.4** 建立 `webapp/backend/__init__.py`、`webapp/backend/main.py` 空殼，確認 `uvicorn webapp.backend.main:app` 可啟動

---

## 階段 1：後端基礎架構

- [x] **1.1** 在 `webapp/backend/main.py` 建立 FastAPI 應用實例，設定 `title="PyVRP Web API"`、`version="0.1.0"`
- [x] **1.2** 加入 CORS middleware，允許 `http://localhost:8000` 與 `http://127.0.0.1:8000`
- [x] **1.3** 掛載 `webapp/frontend/` 為 StaticFiles，路徑 `/`
- [x] **1.4** 建立 `webapp/backend/api/schemas.py`，定義 design.md §3.1 所有 Pydantic 模型（`LatLng`、`TimeWindow`、`Depot`、`Store`、`VehicleType`、`SolverConfig`、`SolveRequest`、`SolveResponse`、`RouteStop`、`VehicleRoute`）
- [x] **1.5** 為所有模型加上 `Field` 驗證（範圍、必填、描述），確保自動產生的 OpenAPI 文件可讀
- [x] **1.6** 撰寫 `GET /api/health` 端點，回傳 `{"status": "ok", "pyvrp_version": "..."}`

---

## 階段 2：座標轉換與求解整合

- [x] **2.1** 建立 `webapp/backend/services/coord.py`，實作 `wgs84_to_utm(lat, lng) -> (x, y, zone)` 函式（用 pyproj `Transformer`）
- [x] **2.2** 在同檔案實作 `wgs84_batch_to_utm(points)`，自動偵測 UTM 帶並驗證所有點屬於同一帶；跨帶時 raise `CrossUtmZoneError`
- [ ] **2.3** 撰寫 `coord.py` 單元測試：以台北 101（25.0330, 121.5645）為基準，驗證 UTM 帶為 51N，座標誤差 < 1m（**待 poetry install 後執行**）
- [x] **2.4** 建立 `webapp/backend/services/solver.py`，實作 `solve(req: SolveRequest) -> SolveResponse` 主函式
- [x] **2.5** 在 `solver.py` 內依 design.md §5 順序：座標轉換 → 建 Model → 加 depot/clients/vehicles/edges → 呼叫 `Model.solve()`
- [x] **2.6** 處理「找不到可行解」情況：檢查 `result.is_feasible()`，若為 False 仍序列化最佳不可行解並在 `warnings` 欄位提示
- [x] **2.7** 建立 `webapp/backend/services/serializer.py`，實作 `solution_to_response(result, req, scale) -> SolveResponse`：把 PyVRP 的 `Route` 物件展開成 `RouteStop`，計算每站累積時間、累積載重

---

## 階段 3：API 端點實作

- [x] **3.1** 建立 `webapp/backend/api/routes.py`，新增 `POST /api/solve` 端點，request body 為 `SolveRequest`，回應 `SolveResponse`
- [x] **3.2** 在端點內呼叫 `services.solver.solve(req)`，並用 `try/except` 對應 design.md §2.5 的錯誤碼表
- [x] **3.3** 加入 `asyncio.wait_for` 包裝同步 solver 呼叫，超時拋出 `HTTPException(504)`
- [x] **3.4** 在 `main.py` 註冊 `routes.router`
- [ ] **3.5** 啟動服務後到 `http://localhost:8000/docs` 確認可以用 Swagger UI 直接測試 `/api/solve`（**待安裝依賴後執行**）

---

## 階段 4：前端基礎頁面

- [x] **4.1** 建立 `webapp/frontend/index.html`，引入 Leaflet CSS/JS（CDN）與自訂 `css/style.css`、`js/api.js`、`js/form.js`、`js/map.js`
- [x] **4.2** 用 CSS Grid 切版：左側 320px 表單面板、中央自適應地圖、右側 360px 結果面板
- [x] **4.3** 在 `style.css` 定義視覺規範：主色變數、字型、圓角、間距 token
- [x] **4.4** 建立 header（logo、範例載入按鈕、API 文件連結）與 footer（狀態列）
- [ ] **4.5** 確認靜態服務可正確顯示版面（**待 poetry install 後執行**）

---

## 階段 5：輸入表單實作

- [x] **5.1** 倉庫區塊：名稱、經緯度、時間窗
- [x] **5.2** 店面區塊：動態 `+ 新增`、`× 刪除`，每筆含名稱/經緯度/時間窗/需求量/服務時長
- [x] **5.3** 車隊區塊：動態新增車型，每型有名稱/容量/數量
- [x] **5.4** 即時驗證：經緯度範圍、時間窗 start < end、需求量 ≥ 0；錯誤時紅框 + 提示文字；全域管理按鈕 disabled 狀態
- [x] **5.5** `collectFormData()` 把表單序列化為符合 `SolveRequest` 的 JSON（時間 HH:MM → 分鐘整數）
- [x] **5.6** 「開始計算」點擊：顯示 loading overlay、呼叫 API、更新地圖/右側面板/footer、錯誤 toast
- [x] **5.7** 「載入範例」按鈕：覆蓋確認 → fetch 範例 JSON → fillForm() 填入所有欄位

---

## 階段 6：地圖視覺化

- [x] **6.1** 在 `js/map.js` 初始化 Leaflet 地圖，預設中心為台北車站，zoom 12，圖磚使用 OSM
- [x] **6.2** 實作 `renderDepot(depot)`：紅色 pin 圖示顯示倉庫，popup 顯示名稱與時間窗
- [x] **6.3** 實作 `renderStoreMarker(stop, orderNum, color)`：圓圈內顯示順序編號，顏色依所屬車輛
- [x] **6.4** 實作 `renderPolyline(route)`：L.polyline 繪製路線 + 自製方向箭頭（divIcon 中點放置）
- [x] **6.5** 實作 `clearAll()` 與 `fitAll(latLngs)`：四個 LayerGroup 一次清空、fitBounds 含 padding
- [x] **6.6** 10 色 palette 定義，依 vehicle index 循環指派；hover/click 路線高亮聯動右側面板

---

## 階段 7：前後端整合

- [x] **7.1** `js/api.js` 實作 `solve(payload)`：fetch、AbortSignal timeout、4xx/5xx 統一拋錯
- [x] **7.2** 串接「開始計算」：表單 → API → map.render() → renderResults() → footer
- [x] **7.3** 右側面板：每台車一個 card，顯示顏色條/車型/載重/距離/每站抵達離開時間
- [x] **7.4** footer 狀態列：求解完成/失敗狀態、總距離、使用車輛數、耗時
- [x] **7.5** 錯誤 toast：5 秒自動消失；不可行解顯示黃色警告 toast

---

## 階段 8：示範資料與文件

- [ ] **8.1** 建立 `webapp/backend/examples/taipei_demo.json`：1 個倉庫（台北車站）+ 10 個店面（台北市便利商店真實座標）+ 2 種車型
- [ ] **8.2** 撰寫 `webapp/README.md`：包含啟動指令、API 範例、截圖位置
- [ ] **8.3** 在主 `README.md` 新增「Web Interface」章節，連結到 `webapp/README.md`
- [ ] **8.4** 在 `webapp/README.md` 內加入 1~2 張畫面截圖（待實際做完再補）

---

## 階段 9：驗收與優化

- [ ] **9.1** 走完 proposal.md §5 的所有 acceptance criteria checklist
- [ ] **9.2** 用示範資料壓測：3/5/10/20/50 個店面分別求解，記錄耗時
- [ ] **9.3** 檢查極端輸入：1 個店面、所有時間窗都過短、需求量超過總容量
- [ ] **9.4** 移除所有 `console.log`、`print` 除錯訊息
- [ ] **9.5** 提交 PR，PR 描述附上 demo 截圖與啟動方式

---

## 任務統計

- **總任務數**：54
- **建議完成順序**：嚴格依階段順序執行；同階段內可平行
- **MVP 最短路徑**（如果時間緊）：0 → 1 → 2 → 3 → 4 → 5 → 6 → 7（跳過 8.4 截圖、9.2 壓測）

---

## 進度追蹤模板

```
階段 0  ░░░░░░░░░░  0/4
階段 1  ░░░░░░░░░░  0/6
階段 2  ░░░░░░░░░░  0/7
階段 3  ░░░░░░░░░░  0/5
階段 4  ░░░░░░░░░░  0/5
階段 5  ░░░░░░░░░░  0/7
階段 6  ░░░░░░░░░░  0/6
階段 7  ░░░░░░░░░░  0/5
階段 8  ░░░░░░░░░░  0/4
階段 9  ░░░░░░░░░░  0/5
─────────────────────────
總計    ░░░░░░░░░░  0/54
```
