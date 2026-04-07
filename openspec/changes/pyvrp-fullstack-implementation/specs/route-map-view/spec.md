# 規格：路線地圖視覺化（route-map-view）

> **變更類型**：ADDED（全新 capability）
> **所屬變更**：`pyvrp-fullstack-implementation`
> **負責層級**：前端展示層
> **核心套件**：Leaflet.js（OpenStreetMap 圖磚）

---

## 目的

將 VRP 求解結果以**互動式地圖**呈現，讓使用者能直觀理解每台車的實際路線、停靠順序、距離與時間，並能透過拖拉與縮放探索細節。地圖區應佔據網頁主要視覺位置（≥ 60% 寬度、≥ 70% 高度）。

---

## ADDED Requirements

### Requirement: 地圖初始化

系統 SHALL 在頁面載入時於中央區塊初始化一張 Leaflet 地圖，預設視角為台北車站、zoom level 12，使用 OpenStreetMap 圖磚。

#### Scenario: 首次載入

- **WHEN** 使用者開啟頁面
- **THEN** 中央顯示一張可拖拉、可縮放的地圖
- **AND** 預設中心為台北車站（25.0478, 121.5170）
- **AND** zoom 為 12
- **AND** 圖磚來源為 `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`

#### Scenario: 響應視窗縮放

- **WHEN** 使用者調整瀏覽器視窗大小
- **THEN** 地圖自動適應新尺寸並重繪
- **AND** 不出現灰色空白區塊

---

### Requirement: 倉庫標記

系統 SHALL 用視覺上明顯不同於店面的圖示在地圖上標記倉庫位置。

#### Scenario: 渲染倉庫

- **WHEN** 求解結果回傳後
- **THEN** 系統在倉庫經緯度位置放置一個**紅色房子 SVG 圖示**（或 emoji 🏠）
- **AND** 圖示尺寸為 32×32 px
- **AND** 點擊圖示彈出 popup，顯示倉庫名稱與開放時間窗

#### Scenario: 倉庫圖示優先層級

- **WHEN** 倉庫位置與某店面非常接近
- **THEN** 倉庫圖示 SHALL 渲染在店面圖示之上（z-index 較高）

---

### Requirement: 店面標記

系統 SHALL 為每個店面渲染一個帶有順序編號的圓圈圖示，圖示顏色與所屬車輛路線的顏色一致。

#### Scenario: 渲染店面

- **WHEN** 求解結果回傳
- **THEN** 系統為每個被服務的店面建立一個圓圈 marker
- **AND** 圓圈內顯示該店面在所屬路線中的順序編號（從 1 開始）
- **AND** 圓圈邊框與填色使用該路線的指派顏色

#### Scenario: 點擊店面 popup

- **WHEN** 使用者點擊店面圖示
- **THEN** popup 顯示：
  - 店面名稱
  - 預計抵達時間（HH:MM 格式）
  - 預計離開時間
  - 等待時間（若有）
  - 該店面的需求量

#### Scenario: 未被服務的店面（不可行解）

- **WHEN** 解為不可行且某店面未被任何路線涵蓋
- **THEN** 該店面以**灰色虛線圓圈**顯示
- **AND** popup 標註「未被服務」

---

### Requirement: 路線軌跡

系統 SHALL 為每條車輛路線繪製一條多色折線（polyline），顏色來自固定 palette，並支援箭頭方向指示。

#### Scenario: 繪製路線

- **WHEN** 求解結果包含 N 條路線
- **THEN** 系統繪製 N 條 `L.polyline`
- **AND** 每條 polyline 連接的點順序為：`倉庫 → 店面 1 → 店面 2 → ... → 倉庫`
- **AND** 每條使用不同顏色（依固定 palette 循環）
- **AND** 線寬為 4px，透明度 0.8

#### Scenario: 顏色一致性

- **WHEN** 第 1 條路線顏色為 `#E63946`
- **THEN** 該路線涵蓋的所有店面圖示也使用 `#E63946`
- **AND** 右側面板對應車輛 card 的標題色條也使用 `#E63946`

#### Scenario: 路線方向指示

- **WHEN** 路線繪製完成
- **THEN** 在每段折線中點位置加入箭頭裝飾，指向行進方向
- **AND** 使用 leaflet-polylinedecorator 或自製 SVG marker

#### Scenario: 滑鼠 hover 路線

- **WHEN** 使用者將滑鼠移到某條路線上
- **THEN** 該路線線寬加粗為 6px、其他路線淡化為 0.3 透明度
- **AND** 顯示 tooltip：`車輛 N: X.X km, X 站`

---

### Requirement: 自動 fitBounds

系統 SHALL 在每次渲染新結果時，自動將地圖視角縮放到能容納所有點的最小範圍。

#### Scenario: 載入結果

- **WHEN** 接收到 `/api/solve` 回應
- **THEN** 系統呼叫 `map.fitBounds([...])`
- **AND** 邊界包含倉庫與所有店面
- **AND** 留白 padding 50px

#### Scenario: 載入範例資料

- **WHEN** 使用者點擊「載入範例」
- **AND** 範例資料填入表單
- **THEN** 地圖在計算前先 fitBounds 到範例所有點，方便使用者預覽位置

---

### Requirement: 清空與重繪

系統 SHALL 在每次新求解前清空所有先前的標記與路線。

#### Scenario: 重複計算

- **WHEN** 使用者修改參數後再次點擊「開始計算」
- **THEN** 系統先清除所有 markers 與 polylines
- **AND** 顯示 loading overlay
- **AND** 收到新結果後重新渲染

#### Scenario: 圖層管理

- **WHEN** 系統渲染地圖元素時
- **THEN** SHALL 將所有 markers 與 polylines 加入同一個 `L.LayerGroup`
- **AND** 清空時呼叫 `layerGroup.clearLayers()` 一次完成

---

### Requirement: 與右側面板的雙向聯動

系統 SHALL 在地圖與右側車輛詳細資訊面板之間建立互動聯動。

#### Scenario: 點擊面板車輛 card

- **WHEN** 使用者點擊右側面板某台車輛的 card
- **THEN** 地圖上該車輛的路線變為強調狀態（線寬加粗、其他淡化）
- **AND** 地圖視角縮放到該路線的 bounding box

#### Scenario: 點擊地圖路線

- **WHEN** 使用者點擊地圖上的某條路線折線
- **THEN** 右側對應車輛 card 自動 scrollIntoView
- **AND** 該 card 加上強調邊框（2px solid 對應顏色）

#### Scenario: 取消選取

- **WHEN** 使用者點擊地圖空白處
- **THEN** 所有路線恢復正常透明度
- **AND** 右側面板取消強調

---

### Requirement: 載入狀態與錯誤提示

系統 SHALL 在求解期間於地圖上方顯示半透明遮罩與 loading spinner。

#### Scenario: 求解中

- **WHEN** 使用者點擊「開始計算」
- **THEN** 地圖上方顯示一個半透明白色遮罩
- **AND** 中央顯示 spinner + 文字 `求解中...`
- **AND** 地圖互動暫時禁用

#### Scenario: 求解失敗

- **WHEN** 後端回應 4xx/5xx
- **THEN** loading 遮罩消失
- **AND** 地圖上方彈出 toast 訊息，背景紅色，顯示對應中文錯誤
- **AND** 地圖保留上一次的成功結果（不被清空）
