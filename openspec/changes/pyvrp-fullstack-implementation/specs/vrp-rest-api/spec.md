# 規格：VRP REST API（vrp-rest-api）

> **變更類型**：ADDED（全新 capability）
> **所屬變更**：`pyvrp-fullstack-implementation`
> **負責層級**：後端 API 層
> **技術棧**：FastAPI + Pydantic + Uvicorn

---

## 目的

提供一個輕量、自我描述（self-documenting）的 HTTP API，讓前端（或任何客戶端）能透過 JSON 提交 VRP 問題並取得求解結果。所有端點皆遵循 RESTful 慣例，並透過 FastAPI 自動生成 OpenAPI 3.0 規格。

---

## ADDED Requirements

### Requirement: 健康檢查端點

系統 SHALL 提供 `GET /api/health` 端點，回傳服務狀態與 PyVRP 版本資訊。

#### Scenario: 服務正常運作

- **WHEN** 任何用戶端發送 `GET /api/health`
- **THEN** 系統回應 HTTP 200，body 為：
  ```json
  {
    "status": "ok",
    "pyvrp_version": "0.5.0",
    "uptime_seconds": 123.4
  }
  ```

---

### Requirement: 求解端點

系統 SHALL 提供 `POST /api/solve` 端點，接收 `SolveRequest` JSON 並回傳 `SolveResponse`。

#### Scenario: 正常求解成功

- **WHEN** 用戶端 POST 合法的 `SolveRequest`
- **AND** PyVRP 在 `max_runtime_seconds` 內找到可行解
- **THEN** 系統回應 HTTP 200，body 為 `SolveResponse`，且 `feasible: true`

#### Scenario: 找不到可行解但仍回傳最佳解

- **WHEN** PyVRP 在時限內無法找到滿足所有限制的解
- **THEN** 系統仍回應 HTTP 200
- **AND** `feasible: false`
- **AND** `warnings` 陣列包含 `"未能在時限內找到可行解，回傳最佳不可行解"`

#### Scenario: 求解超時

- **WHEN** 求解時間超過 `max_runtime_seconds + 5 秒`（緩衝時間）
- **THEN** 系統回應 HTTP 504，body 為：
  ```json
  { "error": "solver_timeout", "max_runtime_seconds": 10.0 }
  ```

---

### Requirement: 輸入驗證

系統 SHALL 對所有請求進行 Pydantic 驗證，並在驗證失敗時回應 HTTP 422 與詳細錯誤訊息。

#### Scenario: 缺少必填欄位

- **WHEN** 用戶端 POST 缺少 `depot` 欄位的請求
- **THEN** 系統回應 HTTP 422
- **AND** body 包含 FastAPI 標準錯誤格式，指出 `field required`

#### Scenario: 經緯度超出範圍

- **WHEN** 用戶端送出 `lat: 100`
- **THEN** 系統回應 HTTP 422 並指出該欄位 `ensure this value is less than or equal to 90`

#### Scenario: 時間窗順序錯誤

- **WHEN** 用戶端送出店面 `time_window: { start: 1000, end: 500 }`
- **THEN** 系統回應 HTTP 422
- **AND** body：`{ "error": "invalid_time_window", "store_id": "S001", "message": "end must be > start" }`

#### Scenario: 跨 UTM 帶錯誤

- **WHEN** 用戶端輸入的點橫跨多個 UTM 帶
- **THEN** 系統回應 HTTP 422
- **AND** body：`{ "error": "cross_utm_zone", "zones": [50, 51], "message": "資料跨越多個 UTM 帶，請分區處理" }`

---

### Requirement: CORS 與靜態檔案掛載

系統 SHALL 允許同源的前端靜態檔案訪問 API，並掛載前端目錄為靜態服務。

#### Scenario: 前端從同主機載入

- **WHEN** 瀏覽器從 `http://localhost:8000/` 載入前端
- **AND** 前端 JS 對 `http://localhost:8000/api/solve` 發送 fetch
- **THEN** 請求成功，無 CORS 阻擋

#### Scenario: 訪問靜態檔案

- **WHEN** 瀏覽器請求 `GET /`
- **THEN** 系統回傳 `webapp/frontend/index.html`

#### Scenario: 訪問靜態資源

- **WHEN** 瀏覽器請求 `GET /css/style.css`
- **THEN** 系統回傳對應靜態檔案，Content-Type 為 `text/css`

---

### Requirement: 自動化 OpenAPI 文件

系統 SHALL 在 `/docs` 路徑提供 Swagger UI 互動文件，並在 `/openapi.json` 提供原始 OpenAPI 3.0 JSON。

#### Scenario: 開發者瀏覽 API 文件

- **WHEN** 開發者訪問 `http://localhost:8000/docs`
- **THEN** 顯示 Swagger UI 介面
- **AND** 列出 `GET /api/health`、`POST /api/solve`
- **AND** 每個端點皆可展開查看 request/response schema 與範例

#### Scenario: 在 Swagger UI 試打 API

- **WHEN** 開發者在 Swagger UI 點擊 `POST /api/solve` 的「Try it out」並送出範例請求
- **THEN** 系統實際執行求解並回傳結果

---

### Requirement: 結構化日誌

系統 SHALL 對每次 `/api/solve` 呼叫寫入結構化日誌，包含時間戳、店面數、車型數、求解耗時、是否可行。

#### Scenario: 成功求解

- **WHEN** `/api/solve` 完成求解
- **THEN** 系統 log 一行：
  ```
  [2026-04-07 14:23:01] INFO solve stores=10 vehicles=2 runtime=4.2s feasible=true cost=92.4
  ```
