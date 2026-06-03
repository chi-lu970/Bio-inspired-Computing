# Final Project Presentation — Design

> 接續 [proposal.md](./proposal.md)

---

## 1. 整體簡報結構設計

### 1.1 投影片流程圖

```
Slide 1: Title
    ↓
Slide 2: Agenda / Outline
    ↓
[INTRODUCTION — 4 slides]
Slide 3: Problem Definition — What is VRP?
Slide 4: Why VRP is Hard (NP-hard)
Slide 5: Why Bio-inspired? (GA 的動機)
Slide 6: Our Contributions
    ↓
[RELATED WORK — 3 slides]
Slide 7: Existing VRP Solvers Comparison
Slide 8: Prior HGS Research (Vidal 2013→2022)
Slide 9: PyVRP Paper Overview (2024)
    ↓
[METHODS — 7 slides]
Slide 10: HGS Algorithm Overview (混合架構)
Slide 11: Genetic Algorithm Component (選擇→交叉→改善)
Slide 12: Local Search — Operators
Slide 13: Population Management & Diversity
Slide 14: Penalty Management (動態懲罰)
Slide 15: System Architecture (Fullstack)
Slide 16: Key Implementation Challenges
    ↓
[RESULTS — 4 slides]
Slide 17: CVRP Benchmark Results
Slide 18: VRPTW Benchmark Results
Slide 19: System Demo — Screenshots
Slide 20: Example Run (台北配送)
    ↓
[CONCLUSION — 2 slides]
Slide 21: Summary & Contributions
Slide 22: Future Work & Limitations
    ↓
Slide 23: Q&A + References
```

---

## 2. 視覺設計方針

### 2.1 色彩語言

| 用途 | 顏色 | 說明 |
|------|------|------|
| 強調生物/演化概念 | 綠色系 `#2D9248` | 仿生主題 |
| 演算法流程 | 藍色系 `#2563EB` | 技術邏輯 |
| 結果/數據 | 橘色系 `#EA580C` | 突顯成效 |
| 警告/限制 | 黃色 `#D97706` | 注意事項 |
| 系統 UI | 直接截圖 | 真實感 |

### 2.2 每張投影片的固定結構

```
┌─────────────────────────────────────────────────────┐
│  [SECTION TAG]                            [Slide #] │
│                                                     │
│  Slide Title (大字、粗體)                             │
│  ─────────────────────────                          │
│                                                     │
│  [主要內容區域：圖表 / 條列 / 流程圖]                 │
│                                                     │
│  [底部：重點一句話 takeaway]                          │
└─────────────────────────────────────────────────────┘
```

### 2.3 圖示風格建議

每個核心概念配一個視覺化比喻：

| 概念 | 視覺比喻 |
|------|---------|
| VRP 問題 | 台北市地圖 + 多色路線 |
| 遺傳演算法 | DNA 雙螺旋 / 染色體圖示 |
| 交叉算子（SREX）| 兩條路線互換片段的動畫截圖 |
| 族群演化 | 多個解在品質-多樣性空間的散點圖 |
| 局部搜尋 | 鄰域操作示意圖（節點移動、交換）|
| 系統架構 | 四層架構圖（來自實作報告）|
| Benchmark 結果 | 橫條圖：PyVRP vs OR-Tools vs HGS |

---

## 3. 各章節設計細節

### 3.1 Introduction 設計

**設計目標**：30 秒內讓聽眾理解「物流派車是什麼難題、為什麼值得用仿生演算法」。

**投影片流程**：
1. 生活化引入（快遞公司每天要解的問題）→ 2. 數學抽象（NP-hard，暴力解不可能）→ 3. 類比演化（自然界如何解決「最佳化」）→ 4. 我們做了什麼

**關鍵類比**：
> "傳統電腦窮舉找最佳路線就像在所有可能的 DNA 序列中找最健康的一個——根本不現實。演化讓自然界找到夠好的解，**遺傳演算法**也讓電腦找到夠好的路線。"

### 3.2 Methods 設計

**設計目標**：讓聽眾對 HGS 的每個機制有直觀理解，不需要看懂數學公式。

**Slide 10 — HGS 總覽**：用流程圖表示整個演算法，每個方塊用顏色區分（GA vs. LS）。

**Slide 11 — 遺傳演算法詳細**：
```
                親本 A        親本 B
               ──────         ──────
               路線 1 2 3     路線 4 5 6
                    ↓ SREX 交叉
               後代：路線 4 + 路線 2 + (貪心補齊缺漏客戶)
                    ↓ 局部搜尋改善
               精煉後代
```

**Slide 12 — 局部搜尋**：列出 11 種節點操作 + 2 種路線操作，各配一個小示意圖。

**Slide 13 — 族群管理**：
- 雙子群結構（可行 / 不可行）
- Biased Fitness 公式（品質排名 + 多樣性排名）
- 淘汰機制（定期清理最差解）

**Slide 14 — 懲罰管理**：
- 目標：維持 43% 可行解
- 動態調整懲罰 → 避免全困在不可行區或喪失探索能力

**Slide 15 — 系統架構**：直接用實作報告的四層架構圖。

**Slide 16 — 技術挑戰**：3 個最有趣的問題（sys.path 衝突、小問題鄰域大小、UTM 座標轉換）。

### 3.3 Results 設計

**設計目標**：快速傳達「PyVRP 解的品質接近世界頂尖」，以及「我們的系統真的能用」。

**Benchmark 數據呈現策略**：
- 不要放 Table 4/5 的完整表格（太密）
- 改用橫條圖，只顯示 Mean Gap 這一個指標
- 加上明確的 callout：「與 BKS 差距 < 0.5%」

**Demo 截圖策略**：
- 截圖 1：初始空白表單（Before）
- 截圖 2：載入範例資料後的地圖預覽（During）
- 截圖 3：求解完成的多色路線地圖（After，最重要）
- 截圖 4：右側路線詳細面板（顯示時間、距離資訊）

### 3.4 Conclusion 設計

**雙軌貢獻框架**：

| 貢獻層面 | 內容 |
|---------|------|
| 學術/演算法層 | 理解並實作 HGS（Bio-inspired + LS 混合架構）|
| 工程/系統層 | 將研究級演算法包裝成可用系統（Fullstack Web App）|

---

## 4. Presenter Notes 撰寫原則

1. 每張投影片的 Notes 以一句「這張投影片的核心訊息」開頭
2. 提供 1–2 個可以用來活絡氣氛的問句（"Have you ever wondered..."）
3. 標注可能的提問點和預備回答
4. 標注轉場語（"Now that we understand X, let's look at Y..."）

---

## 5. 時間配置計畫

| 章節 | 投影片數 | 建議時間 |
|------|---------|---------|
| Title + Agenda | 2 | 1 分鐘 |
| Introduction | 4 | 2.5 分鐘 |
| Related Work | 3 | 1.5 分鐘 |
| Methods | 7 | 4 分鐘 |
| Results | 4 | 2.5 分鐘 |
| Conclusion | 2 | 1.5 分鐘 |
| Q&A buffer | 1 | 2 分鐘 |
| **合計** | **23** | **~15 分鐘** |
