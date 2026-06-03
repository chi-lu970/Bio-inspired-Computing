# PyVRP Web — 系統介紹

## 1. 系統概述

**PyVRP Web** 是一套以 PyVRP 為核心求解引擎、搭配全端 Web 介面的**車輛路線規劃（VRP）視覺化系統**。使用者不需要撰寫任何程式碼，只需透過瀏覽器填寫倉庫、店面、車隊資訊，即可在幾秒內取得最佳化配送路線，並在互動地圖上一覽全局。

本系統以台北市 7-ELEVEN 多門市補貨排程為示範情境，可廣泛應用於物流配送、外送排程、巡迴服務等場景。

---

## 2. 核心功能

### 2.1 路線最佳化求解
- 支援**多車型、多車輛**的車隊設定（各車型可設定載重上限與可用台數）
- 支援每個節點（倉庫、店面）各自設定**時間窗（Time Window）**
- 支援各店面設定**服務時間（service duration）**與**需求量（demand）**
- 自動排程，確保所有需求皆在時間窗內被服務

### 2.2 互動地圖視覺化
- 以 Leaflet.js 繪製 OpenStreetMap 底圖
- 各車輛路線以不同顏色折線顯示
- 可點擊各站標記，查看抵達時間、等待時間、累積載重等細節

### 2.3 範例資料快速載入
- 內建「7-11 台北市日班配送（16 家門市）」
- 內建「7-11 台北市大夜班配送（16 家門市）」
- 一鍵載入，立即求解，適合快速體驗與展示

### 2.4 求解統計摘要
- 頁面底部狀態列即時顯示：求解狀態、總距離（km）、使用車輛數、求解耗時

### 2.5 API 文件
- 內建 FastAPI 自動產生的 Swagger UI（`/docs`），可直接測試 API 端點

---

## 3. 技術架構

### 3.1 後端（Backend）

| 技術 | 用途 |
|---|---|
| **Python 3.11 / 3.13** | 主要後端語言 |
| **FastAPI** | REST API 框架，自動生成 OpenAPI 文件 |
| **Uvicorn** | ASGI 非同步 Web 伺服器 |
| **PyVRP v0.5.0** | 核心 VRP 求解引擎（Hybrid Genetic Search）|
| **Pydantic v2** | 請求/回應資料驗證與序列化 |
| **pyproj (UTM)** | WGS84 經緯度轉 UTM 座標，計算歐氏距離 |

**求解引擎細節（PyVRP）：**
- 演算法：**Hybrid Genetic Search（HGS）**
  - 族群管理（Population）+ 多樣性維護（broken pairs distance）
  - 交叉算子：**SREX（Selective Route Exchange）**
  - 局部搜尋：多種節點/路線算子（Relocate、Swap、2-Opt 等）
- 停止條件：`TimedNoImprovement`（連續 500 次迭代無改善 **或** 達到最長執行秒數）
- 鄰域限制：`nb_granular = 7`（避免小問題搜尋空間爆炸）
- 座標系：UTM 公尺 ×10（0.1 公尺精度整數表示）

### 3.2 前端（Frontend）

| 技術 | 用途 |
|---|---|
| **純 HTML / CSS / JavaScript** | 無框架，零建置步驟 |
| **Leaflet.js 1.9.4** | 互動地圖（OpenStreetMap 底圖）|
| **ES Module** | 模組化 JS（api.js / map.js / form.js）|

前端直接由 FastAPI 的 `StaticFiles` 掛載提供，不需要額外 Web 伺服器。

### 3.3 API 設計

| 端點 | 方法 | 說明 |
|---|---|---|
| `/api/health` | GET | 健康檢查，回傳 PyVRP 版本 |
| `/api/solve` | POST | VRP 求解主端點 |
| `/docs` | GET | Swagger UI API 文件 |
| `/` | GET | 前端網頁介面 |

**`POST /api/solve` 輸入結構：**
```
SolveRequest
├── depot        倉庫（名稱、座標、時間窗）
├── stores[]     店面列表（id、名稱、座標、時間窗、需求量、服務時間）
├── vehicle_types[] 車型列表（名稱、載重容量、可用台數）
└── config       求解設定（最長秒數、隨機種子、平均車速）
```

**`POST /api/solve` 輸出結構：**
```
SolveResponse
├── feasible          是否找到可行解
├── runtime_seconds   求解耗時
├── iterations        GA 迭代次數
├── total_distance_km 總距離（km）
├── num_routes_used   實際使用車輛數
└── routes[]          各車輛路線（含每站抵達/離開時間、等待時間、距離）
```

### 3.4 並發與安全機制
- 使用 `ThreadPoolExecutor`（max_workers=8）將同步的 PyVRP 求解放入 thread pool，避免阻塞 async event loop
- `asyncio.Semaphore(1)` 確保同時只有一個求解請求執行，後續請求立即收到 HTTP 503，防止 thread 堆積

---

## 4. 系統架構圖

```
使用者瀏覽器
     │
     │ HTTP
     ▼
┌──────────────────────────────────┐
│         Uvicorn (port 8000)      │
│  ┌───────────────────────────┐   │
│  │       FastAPI App         │   │
│  │  ┌─────────────────────┐  │   │
│  │  │   Static Files      │  │   │
│  │  │  (HTML/CSS/JS)      │  │   │
│  │  └─────────────────────┘  │   │
│  │  ┌─────────────────────┐  │   │
│  │  │   API Router        │  │   │
│  │  │  GET  /api/health   │  │   │
│  │  │  POST /api/solve    │  │   │
│  │  └────────┬────────────┘  │   │
│  └───────────┼───────────────┘   │
│              │ Thread Pool       │
│  ┌───────────▼───────────────┐   │
│  │    solver.py (PyVRP HGS)  │   │
│  │  WGS84 → UTM → Model      │   │
│  │  GeneticAlgorithm.run()   │   │
│  └───────────────────────────┘   │
└──────────────────────────────────┘
```

---

## 5. 適用場景

- 物流公司多點配送路線規劃
- 連鎖超商補貨排程（含時間窗限制）
- 外送平台多騎手路線分配
- 生物啟發式計算課程教學展示（GA 求解 VRP）

---

## 6. 版本資訊

| 項目 | 版本 |
|---|---|
| PyVRP | 0.5.0 |
| FastAPI | — |
| Uvicorn | — |
| Leaflet.js | 1.9.4 |
| Python | 3.11 / 3.13 |
