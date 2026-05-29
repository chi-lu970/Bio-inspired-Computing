# Spec: Related Work Slides (Slides 7–9)

---

## Slide 7 — Existing VRP Solvers Comparison

**標題**：`Related Work: VRP Solver Landscape`

**主要內容：比較表格**

| Solver | Type | Performance | Flexibility | License |
|--------|------|-------------|-------------|---------|
| **PyVRP** | Python + C++ (HGS) | ★★★★★ | ★★★★★ | MIT (Open) |
| HGS-CVRP (Vidal 2022) | Pure C++ | ★★★★★ | ★★☆☆☆ | MIT |
| LKH-3 (Helsgaun) | C (Lin-Kernighan) | ★★★★☆ | ★☆☆☆☆ | Academic only |
| OR-Tools (Google) | C++/Python | ★★★☆☆ | ★★★★☆ | Apache |
| VRPSolver | Exact solver | ★★★★★ (exact) | ★★★☆☆ | Academic only |
| VROOM | C++ | ★★★☆☆ | ★★★☆☆ | Open |

**橘色 Callout**：
```
PyVRP achieves top-tier performance AND remains fully customizable in Python.
No competitor offers all three: speed + flexibility + open license.
```

**Presenter Notes**：
> "PyVRP stands out because it achieves nearly the same solution quality as specialized C++ solvers, while being fully customizable in Python. Google's OR-Tools is widely used in industry but falls significantly short on solution quality for academic benchmarks."

---

## Slide 8 — HGS Research Lineage

**標題**：`Standing on the Shoulders of Giants: HGS History`

**時間軸設計（橫向，由左至右）**：

```
2010         2013           2022           2024
  │            │              │              │
  ▼            ▼              ▼              ▼
SREX        HGS-VRPTW    HGS-CVRP       PyVRP
Crossover   (Vidal et al.) (Vidal 2022)  (Wouda et al.)
invented    Original HGS  Open-source   Python+C++
(Nagata &   for time-      C++ impl +    multi-variant
Kobayashi)  windowed VRP   SWAP*         solver
```

**各節點說明**：

**2010 — SREX（Nagata & Kobayashi）**：
- 提出 Selective Route Exchange 交叉算子
- 核心思想：繼承父母各自擅長的路線片段

**2013 — HGS（Vidal et al.）**：
- 完整提出混合遺傳搜尋框架
- 引入雙子群結構（可行 + 不可行）
- 動態懲罰機制
- DIMACS 競賽奪冠（2021）

**2022 — HGS-CVRP（Vidal）**：
- 開源 C++ 實作
- 引入 SWAP* 算子
- Biased Fitness 公式

**2024 — PyVRP（Wouda, Lan, Kool）**：
- Python + C++ 混合架構
- 擴充支援 VRPTW
- 可自定義交叉算子、多樣性指標
- 改善 27 個 VRPTW 歷史最佳解

**Presenter Notes**：
> "PyVRP didn't invent HGS from scratch. It took 14 years of research, starting from the SREX crossover operator in 2010, through Vidal's original HGS in 2013, to the 2024 open-source Python package. What the authors contributed was making this research accessible and extensible."

---

## Slide 9 — PyVRP Paper Overview

**標題**：`PyVRP: A High-Performance VRP Solver Package (2024)`

**論文資訊 Box（左上）**：
```
Authors: Niels A. Wouda, Leon Lan, Wouter Kool
Journal: INFORMS Journal on Computing
Year: 2024, Vol. 36(4), pp. 943–955
```

**三大貢獻（三個圓形圖示）**：

```
   [圖示: 🏗️]              [圖示: ⚡]              [圖示: 🏆]
  Framework              Algorithm               Benchmarks
  Design                Enhancements            

Python+C++           VRPTW extension         #1 in DIMACS 2021
hybrid arch          SWAP* with caching      #1 EURO NeurIPS 2022
Fully modular        Simplified for          Improved 27 BKS on
customizable         open-source use         H&G instances
```

**Python vs C++ 分工（小圖）**：
```
Python (邏輯層)：GA 主迴圈、族群管理、懲罰管理
       ↕ 
C++ (效能層)：局部搜尋操作符（佔 80–90% 運行時間）
```

**引用數據**：
```
"PyVRP combines the flexibility of Python 
 with the performance of C++"
                    — Wouda et al., 2024
```

**Presenter Notes**：
> "The key innovation isn't a new algorithm—it's making an existing world-class algorithm accessible. By implementing only the performance-critical local search operators in C++, and keeping everything else in Python, they achieved near-competitive performance with unprecedented flexibility."
