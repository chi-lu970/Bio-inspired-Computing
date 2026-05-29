# Spec: Related Work Slides (Slides 7–9)

---

## Slide 7 — Existing VRP Solvers Comparison

**標題**：`Related Work: VRP Solver Landscape`

**主要內容：比較表格**

| Solver | Type | Performance | Flexibility | License | 論文原文評語 |
|--------|------|-------------|-------------|---------|------------|
| **PyVRP** | Python + C++ (HGS) | ★★★★★ | ★★★★★ | MIT (Open) | Unique combination of scope, performance, flexibility, ease-of-use |
| HGS-CVRP (Vidal 2022) | Pure C++ | ★★★★★ | ★★☆☆☆ | MIT | Customisation requires changes to C++ source code |
| LKH-3 (Helsgaun) | C (Lin-Kernighan) | ★★★★☆ | ★☆☆☆☆ | Academic only | Hard to customise; non-commercial license |
| OR-Tools (Google) | C++/Python | ★★★☆☆ | ★★★★☆ | Apache | "Its performance is far from the state of the art" |
| VRPSolver | Exact solver | ★★★★★ (exact) | ★★★☆☆ | Academic only | "Does not scale to instances with more than a few hundred customers" |
| VROOM | C++ | ★★★☆☆ | ★★★☆☆ | Open | "Unable to compete with state-of-the-art algorithms" |

**論文直接引語 Callout（橘色框）**：
```
"While each of these projects has their own merit, PyVRP has a unique combination 
of scope, performance, flexibility and ease-of-use, making it a useful addition 
to this set of projects."
                                                        — Wouda et al., 2024
```

**特別背景 — ML 研究角度（補充）**：
```
The authors explicitly target ML researchers:
"We especially hope that PyVRP will help machine learning (ML) researchers 
 interested in vehicle routing to easily build on the state-of-the-art, 
 and move beyond LKH-3 as the most commonly used baseline."
                                                        — Wouda et al., 2024

LKH-3 had been the de-facto baseline in VRP+ML research for years.
PyVRP provides a significantly stronger and more flexible alternative.
```

**Presenter Notes**：
> "The authors directly critique each competitor in the paper. LKH-3, despite being widely used in ML research as a baseline, is only available under an academic non-commercial license and is hard to customize. OR-Tools from Google is convenient but the paper explicitly states its 'performance is far from the state of the art.' PyVRP is the only solver offering top-tier performance, MIT license, AND Python-level customization."

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
- Python + C++ 混合架構（arXiv:2403.13795，INFORMS JoC 2024）
- 擴充支援 VRPTW；SWAP* 加入時間窗 caching + 提早終止
- 可自定義交叉算子、多樣性指標、鄰域結構
- **簡化移除**競賽特化組件（more robust, less overfitted）
- 延長計算改善 27 個 H&G 歷史最佳解

**重要設計取捨引語**：
```
"Complex components with limited contribution to the overall performance 
have been removed to strike a balance between simplicity and performance."
                                                        — Wouda et al., 2024

→ PyVRP would have ranked 2nd (not 1st) in DIMACS VRPTW competition.
  Trade-off: slightly lower performance, much higher maintainability.
```

**Presenter Notes**：
> "PyVRP didn't invent HGS from scratch. It took 14 years of research, starting from the SREX crossover operator in 2010, through Vidal's original HGS in 2013, to the 2024 open-source Python package. Critically, the authors made a deliberate trade-off: they removed some competition-specific optimizations to make the code cleaner and more maintainable. This explains why PyVRP performs slightly below HGS-DIMACS on VRPTW benchmarks."

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
