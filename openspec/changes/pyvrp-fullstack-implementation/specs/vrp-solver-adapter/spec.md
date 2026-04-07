# 規格：VRP 求解器轉接層（vrp-solver-adapter）

> **變更類型**：ADDED（全新 capability）
> **所屬變更**：`pyvrp-fullstack-implementation`
> **負責層級**：後端服務層
> **核心職責**：WGS84 ↔ UTM 座標轉換 + PyVRP `Model` 整合 + 結果序列化

---

## 目的

作為 API 層與 PyVRP 核心之間的轉接器（Adapter），負責：
1. 將使用者輸入的真實地理座標（WGS84）轉換為 PyVRP 可用的整數平面座標
2. 組裝 PyVRP `Model` 物件並呼叫 `solve()`
3. 將 PyVRP 回傳的 `Result` / `Solution` / `Route` 物件展開為前端可直接渲染的 JSON 結構

此層**不應暴露任何 PyVRP 原生型別**到 API 層或前端。

---

## ADDED Requirements

### Requirement: 單點座標轉換

系統 SHALL 提供 `wgs84_to_utm(lat: float, lng: float) -> tuple[float, float, int]` 函式，回傳 UTM x、y、zone number。

#### Scenario: 台北 101 轉換

- **WHEN** 呼叫 `wgs84_to_utm(25.0330, 121.5645)`
- **THEN** 回傳 `(x, y, 51)`，其中 x、y 為公尺
- **AND** 與已知 UTM 51N 座標誤差小於 1 公尺

#### Scenario: 南半球座標

- **WHEN** 呼叫 `wgs84_to_utm(-33.8688, 151.2093)`（雪梨）
- **THEN** 回傳的 zone 為 `56`，並使用南半球 UTM EPSG（如 32756）

---

### Requirement: 批次座標轉換與 UTM 帶檢查

系統 SHALL 提供 `wgs84_batch_to_utm(points: list[LatLng]) -> tuple[list[Point], int]` 函式，自動偵測共同 UTM 帶並一次轉換所有點；若點橫跨多帶則 raise 例外。

#### Scenario: 全部點在同一 UTM 帶

- **WHEN** 傳入 11 個台北市內的點
- **THEN** 回傳 `(11 個轉換後座標, zone=51)`

#### Scenario: 點橫跨多個 UTM 帶

- **WHEN** 傳入台北 101（51 帶）+ 蘭嶼（51 帶）+ 香港（49 帶）
- **THEN** raise `CrossUtmZoneError`，例外屬性包含 `zones=[49, 51]`

#### Scenario: 自動選擇主要 UTM 帶

- **WHEN** 傳入的點 95% 在 51 帶、5% 在邊界處被歸到 50 帶
- **THEN** 系統 SHALL 拒絕該請求，不允許「投票決定」帶別

---

### Requirement: PyVRP Model 建構

系統 SHALL 提供 `build_model(req: SolveRequest, utm_points: list[Point]) -> Model` 函式，組裝完整可解的 PyVRP `Model`。

#### Scenario: 標準建構流程

- **WHEN** 呼叫 `build_model(req, utm_points)`
- **THEN** 系統依序：
  1. 建立空 `Model`
  2. 呼叫 `add_depot(x, y, tw_early, tw_late)` 加入倉庫
  3. 對每個店面呼叫 `add_client(...)` 並保留回傳的 Client 參考
  4. 對每個車型呼叫 `add_vehicle_type(capacity, num_available)`
  5. 對所有 (i, j) 配對呼叫 `add_edge(frm, to, distance, duration)`，其中 distance 為 UTM 公尺乘以 SCALE 取整、duration 為公尺/速度反推的整數分鐘
- **AND** 回傳的 Model 可直接呼叫 `.solve()`

#### Scenario: 整數比例尺一致性

- **WHEN** 使用 `SCALE = 10`
- **THEN** 所有距離與座標皆乘以 10 後 `int()`
- **AND** 同一 `solve()` 呼叫內所有距離使用相同 SCALE

#### Scenario: 行駛時間反推

- **WHEN** 兩點 UTM 距離為 4000 公尺、`avg_speed_kmh = 40`
- **THEN** duration 為 `int(4000 / (40 * 1000 / 60)) = 6` 分鐘

---

### Requirement: 求解執行與超時控制

系統 SHALL 提供 `solve(req: SolveRequest) -> SolveResponse` 主入口，負責整合上述步驟並控制求解時間。

#### Scenario: 正常求解

- **WHEN** 呼叫 `solve(req)`，`max_runtime_seconds = 10`
- **THEN** 系統使用 `MaxRuntime(10)` 作為停止條件
- **AND** 求解完成後在 12 秒內回應

#### Scenario: 超時保護

- **WHEN** 求解程式因 PyVRP 內部問題持續超過 `max_runtime_seconds + 5`
- **THEN** 系統 raise `SolverTimeoutError`，由 API 層轉為 HTTP 504

#### Scenario: 求解失敗

- **WHEN** PyVRP 拋出例外
- **THEN** 系統捕捉並 raise `SolverInternalError`，附加原始錯誤訊息
- **AND** 由 API 層轉為 HTTP 500

---

### Requirement: 結果序列化

系統 SHALL 提供 `solution_to_response(result, req, utm_zone, scale) -> SolveResponse` 函式，將 PyVRP 結果展開為前端可用的 JSON。

#### Scenario: 路線展開

- **WHEN** PyVRP 回傳 2 條路線：`[0, 1, 3, 0]`、`[0, 2, 4, 5, 0]`（0 為倉庫）
- **THEN** 系統產生 2 個 `VehicleRoute`
- **AND** 每個 `VehicleRoute` 的 `stops` 陣列包含起點倉庫 → 各店面 → 終點倉庫

#### Scenario: 累積時間計算

- **WHEN** 車輛從倉庫 08:00 出發，行駛 6 分鐘抵達店面 A，服務 10 分鐘
- **THEN** 該店面的 `arrival_minutes = 486`（08:06）
- **AND** `departure_minutes = 496`（08:16）

#### Scenario: 等待時間處理

- **WHEN** 車輛 08:30 抵達，但店面時間窗 09:00 才開始
- **THEN** `arrival_minutes = 510`（08:30）
- **AND** `departure_minutes = 540 + service_minutes`（09:00 開始服務 + 服務時間）
- **AND** 該停靠點額外標記 `wait_minutes = 30`

#### Scenario: 距離反推

- **WHEN** PyVRP 內部距離為 45300（已 SCALE×10 後的整數）
- **THEN** 序列化後的 `total_distance_km = 4.53`

#### Scenario: 顏色預先指派

- **WHEN** 結果包含 3 條路線
- **THEN** 系統依固定 palette 指派 `color` 給每條路線（避免前端再算）

---

### Requirement: 例外型別定義

系統 SHALL 在 `webapp/backend/services/exceptions.py` 定義下列自訂例外，供 API 層 catch 後對應 HTTP 狀態：

| 例外類別 | 對應 HTTP | 用途 |
|----------|----------|------|
| `CrossUtmZoneError` | 422 | 跨 UTM 帶 |
| `InvalidTimeWindowError` | 422 | 時間窗順序錯誤（補強 Pydantic 未涵蓋的跨欄位驗證） |
| `SolverTimeoutError` | 504 | 求解超時 |
| `SolverInternalError` | 500 | PyVRP 內部錯誤 |
| `InfeasibleByConstructionError` | 422 | 總需求 > 總容量等明顯不可行 |

#### Scenario: 例外訊息一致性

- **WHEN** 任一自訂例外被 raise
- **THEN** 例外實例 SHALL 至少包含 `code`（字串）與 `message`（中文字串）兩個屬性
- **AND** API 層可直接序列化為 `{"error": code, "message": message}`
