# Fig. 1 — HGS 主迴圈流程圖

> **用途**：截圖後存為 `report/figures/fig1_hgs_flowchart.png`，放入 Overleaf。
>
> **截圖方法**：
> 1. 將下方 Mermaid 程式碼貼入 [mermaid.live](https://mermaid.live)
> 2. 右側預覽調整 Theme 為 `default`（白底）
> 3. 點擊右上角 **PNG** 下載（或直接截圖）
> 4. 存為 `report/figures/fig1_hgs_flowchart.png`

---

```mermaid
flowchart TD
    A([▶ 開始]) --> B

    B["🔧 初始化族群 P
    min_pop_size = 25 個隨機解
    α = 20, β = 6  初始懲罰權重"]

    B --> C

    C(["🔁 迴圈開始"])

    C --> D["👥 TournamentSelect P
    選出親本 p₁, p₂
    （基於 biased fitness 二元錦標賽）"]

    D --> E["🧬 SREX p₁, p₂  →  子代 c
    Selective Route Exchange 交叉
    繼承 p₂ 完整路線 + 貪婪填入 p₁ 剩餘客戶"]

    E --> F["🔍 LocalSearch c
    11 個 Node 算子 + 2 個 Route 算子
    粒度鄰域 k = 20 / 40"]

    F --> G{rand &lt; p_repair
    且 c 不可行？}

    G -- 是 --> H["🔧 修復搜尋
    LocalSearch c, α×12, β×12
    高懲罰強制導向可行解"]
    H --> I

    G -- 否 --> I

    I["➕ P ← P ∪ c
    將子代加入族群"]

    I --> J{"| P | > n_min + n_gen
    65 個上限？"}

    J -- 是 --> K["✂ SurvivorSelection P
    移除重複解
    按 biased fitness 淘汰
    縮回 n_min = 25"]
    K --> L

    J -- 否 --> L

    L["⚖ UpdatePenalties P
    每 50 / 100 代調整 α, β
    目標：維持 43% 可行解比率
    α × 1.34 若可行率 &lt; 38%
    α × 0.32 若可行率 &gt; 48%"]

    L --> M{"停止條件達成？
    TimedNoImprovement
    max_iterations = 500
    或 MaxRuntime"}

    M -- 否 --> C
    M -- 是 --> N

    N["🏆 返回最佳可行解"]
    N --> O([⏹ 結束])

    style A fill:#4CAF50,color:#fff,stroke:none
    style O fill:#f44336,color:#fff,stroke:none
    style C fill:#2196F3,color:#fff,stroke:none
    style G fill:#FF9800,color:#fff,stroke:none
    style J fill:#FF9800,color:#fff,stroke:none
    style M fill:#9C27B0,color:#fff,stroke:none
    style N fill:#4CAF50,color:#fff,stroke:none
    style H fill:#FF5722,color:#fff,stroke:none
```

---

## 各節點對應論文位置

| 節點 | 對應章節 |
|------|---------|
| 初始化族群 | Methods III-B, Algorithm 1 line 1–2 |
| TournamentSelect | Methods III-B §Population Management |
| SREX 交叉 | Methods III-B §SREX Crossover |
| LocalSearch | Methods III-B §Local Search（11+2 operators） |
| 修復搜尋 | Methods III-B §Dynamic Penalty（repair booster ×12） |
| SurvivorSelection | Methods III-B §Population Management（n_min=25） |
| UpdatePenalties | Methods III-B §Dynamic Penalty（43% target） |
| 停止條件 | Methods III-C（TimedNoImprovement, max_iterations=500） |
