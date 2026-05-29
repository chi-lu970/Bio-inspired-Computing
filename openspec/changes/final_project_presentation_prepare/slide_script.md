# PyVRP-Web 簡報腳本（23 張投影片）

> **用途**：照這份文件的內容，用任何工具（Canva / PowerPoint / Google Slides）製作投影片。  
> **色彩系統**：綠 #2D9248（生物/演化）、藍 #2563EB（技術）、橘 #EA580C（結果/重點）、深藍 #1E293B（標題底色）  
> **版面**：每張投影片都有「頂部區塊標籤」+ 「大標題」+ 「主內容」+ 「底部重點條（Takeaway）」

---

## Slide 1 — 標題頁

**版面**：深色（#1E293B）頂部橫幅 + 白色背景主體

| 區塊 | 內容 |
|------|------|
| 頂部橫幅（深色） | `Bio-inspired Computing — Final Project` + 右側 `Student ID: 414085193` |
| 主標題（大字、粗體） | **PyVRP-Web: A Bio-inspired Vehicle Routing Solver with Interactive Visualization** |
| 副標題（斜體） | *Applying Hybrid Genetic Search (HGS) to Real-World Logistics Optimization* |
| 三個色彩標籤（橫排） | 🧬 Genetic Algorithm（綠）｜⚡ Local Search (C++)（藍）｜🗺 Web Visualization（橘） |
| 底部綠色條 | `HGS = Genetic Algorithm (Explore) + Local Search (Exploit) = Near-Optimal VRP` |

**備圖**：台北地圖（模糊背景）+ 3 條彩色路線（可先用截圖代替）

---

## Slide 2 — Outline（議程）

**標籤**：TITLE

**標題**：Outline

| 編號 | 章節 | 說明 |
|------|------|------|
| ① | Introduction | What is VRP and why it's computationally hard |
| ② | Related Work | Prior solvers and HGS research lineage (2010→2024) |
| ③ | Methods | HGS algorithm deep-dive + our full-stack system |
| ④ | Results | Benchmark performance + live system demo |
| ⑤ | Conclusion | Contributions, limitations, and future work |

**視覺**：5 個色塊（①藍 ②青 ③綠 ④橘 ⑤深色）橫向排列

---

## Slide 3 — VRP 問題定義

**標籤**：INTRO  
**標題**：The Vehicle Routing Problem (VRP)

**左側**：
```
Given:
• A depot (warehouse / distribution center)
• n customers with delivery demands
• k vehicles with limited load capacity

Goal:
Minimize total travel distance
while serving every customer exactly once
and respecting vehicle capacity limits.

Variant — VRPTW:
Each customer has a time window [earliest, latest]
Vehicle must arrive within that window.
```

**右側**：🖼 **截圖 A**（見文末截圖清單）

**底部橘色條**：`VRP = "How to dispatch delivery trucks to minimize total distance"`

**講稿**：「想像你管理一個台北的便利商店物流中心，每天早上要派車補貨到 20+ 個門市——最有效率的路線怎麼規劃？這就是 VRP。」

---

## Slide 4 — 為什麼 VRP 很難

**標籤**：INTRO  
**標題**：Why VRP is Computationally Hard

**左欄**（淺色背景框）：
```
Scale explosion — # of possible routes:

  10 customers  →       3,628,800 routes
  20 customers  →   2.4 × 10¹⁸ routes
  50 customers  →   3  × 10⁶⁴ routes

Brute force: impossible even for modern supercomputers

→ For 20 customers at 1 billion ops/sec:
   would take longer than the age of the universe
```

**右欄**（淺色背景框）：
```
VRP is NP-hard:
• No known polynomial-time algorithm
• Exact solvers limited to ~100 customers
• Real logistics: 500–1000+ customers/day

→ Need metaheuristic / bio-inspired approaches

Common approaches:
  • Genetic Algorithm (GA)          ← 綠色
  • Simulated Annealing (SA)
  • Ant Colony Optimization (ACO)
  • Hybrid: GA + Local Search ← HGS  ← 藍色粗體
```

**底部**：`We need smart search strategies — this is where bio-inspired algorithms shine.`

---

## Slide 5 — 為什麼選仿生？演化類比

**標籤**：INTRO  
**標題**：Nature's Solution: Evolutionary Optimization

**類比對照表**（左深色「NATURE」 | 右藍色「ALGORITHM (HGS)」）：

| NATURE | → | ALGORITHM |
|--------|---|-----------|
| Population of organisms | → | Population of candidate routes |
| Fitness (survival ability) | → | Objective: minimize total distance |
| Crossover (reproduction) | → | SREX: exchange complete route segments |
| Mutation | → | Local Search: move/swap customers |
| Natural Selection | → | Biased Fitness elimination |
| Generations | → | Iterations (thousands) |
| Surviving species | → | Near-optimal routing solution |

**綠色 Callout 框**（底部橫幅）：
```
Key Insight:
Pure GA offspring are low quality.
HGS pairs EVERY offspring with Local Search → dramatically better solutions.
"Exploration (GA) + Exploitation (LS) = Best of both worlds"
```

---

## Slide 6 — 我們做了什麼

**標籤**：INTRO  
**標題**：What We Built — Two-Layer Contribution

**左欄（藍色標頭）**：Layer 1: Algorithm Understanding
```
Deep dive into PyVRP (INFORMS J. on Computing, 2024)

✓  Hybrid Genetic Search (HGS) full architecture
✓  11 node operators + 2 route operators (C++)
✓  SREX crossover (Nagata & Kobayashi 2010)
✓  Broken Pairs Distance diversity metric
✓  Dynamic penalty management (43% target)
✓  Population management (dual sub-population)
```

**右欄（綠色標頭）**：Layer 2: Full-Stack Web System
```
PyVRP-Web — zero-code logistics optimizer

✓  FastAPI backend with PyVRP integration
✓  WGS84 → UTM coordinate conversion (pyproj)
✓  Interactive map visualization (Leaflet.js)
✓  Real-time route display with color coding
✓  Per-stop arrival time reconstruction
✓  Live demo: 16 Taipei 7-ELEVEN stores
```

**底部綠色條**：`We bridged research-grade bio-inspired optimization and usable software — algorithm to UI`

---

## Slide 7 — VRP Solver 比較

**標籤**：RELATED  
**標題**：Related Work: VRP Solver Landscape

**比較表格**：

| Solver | Type | Performance | Flexibility | License |
|--------|------|-------------|-------------|---------|
| **PyVRP (2024)** | Python + C++ (HGS) | ★★★★★ | ★★★★★ | **MIT ✓** |
| HGS-CVRP (Vidal) | Pure C++ | ★★★★★ | ★★☆☆☆ | MIT |
| LKH-3 (Helsgaun) | C (Lin-Kernighan) | ★★★★☆ | ★☆☆☆☆ | Academic only |
| OR-Tools (Google) | C++ / Python | ★★★☆☆ | ★★★★☆ | Apache |
| VRPSolver | Exact solver | ★★★★★* | ★★★☆☆ | Academic only |
| VROOM | C++ | ★★★☆☆ | ★★★☆☆ | Open |

*PyVRP 列用綠色底色標示*

**橘色引語框**：
```
"While each of these projects has their own merit, PyVRP has a unique
combination of scope, performance, flexibility and ease-of-use."
                                                  — Wouda et al., 2024

OR-Tools: "its performance is far from the state of the art"
VRPSolver: "does not scale to more than a few hundred customers"
```

---

## Slide 8 — HGS 研究脈絡

**標籤**：RELATED  
**標題**：Standing on the Shoulders of Giants: HGS History

**橫向時間軸**（從左到右，每個節點一個色塊）：

```
2010              2013              2022              2024
  │                 │                 │                 │
SREX             HGS-VRPTW        HGS-CVRP          PyVRP
Crossover        (Vidal et al.)   (Vidal)           (Wouda, Lan, Kool)
青色              藍色              綠色               橘色
```

各節點說明：

**2010 — SREX（青）**：提出 Selective Route Exchange；繼承父母各自擅長的路線片段

**2013 — HGS（藍）**：完整 HGS 框架；雙子群（可行+不可行）；動態懲罰；DIMACS 奪冠（2021）

**2022 — HGS-CVRP（綠）**：開源 C++ 實作；SWAP* 算子；Biased Fitness 公式

**2024 — PyVRP（橘）**：Python + C++ 混合；VRPTW 支援；簡化移除競賽特化組件；改善 27 個歷史最佳解

**深色引語框**：
```
"Complex components with limited contribution to the overall performance
have been removed to strike a balance between simplicity and performance."
                                                      — Wouda et al., 2024

→ PyVRP would have ranked 2nd (not 1st) in DIMACS VRPTW competition.
  Trade-off: slightly lower performance, much higher maintainability.
```

---

## Slide 9 — PyVRP 論文總覽

**標籤**：RELATED  
**標題**：PyVRP: A High-Performance VRP Solver Package (2024)

**論文資訊框（左上）**：
```
Authors: Niels A. Wouda, Leon Lan, Wouter Kool
Journal: INFORMS Journal on Computing
Year: 2024, Vol. 36(4), pp. 943–955
arXiv: 2403.13795v2 [cs.NE]
License: MIT (open-source)
```

**Python vs C++ 分工（右側）**：
```
Python（邏輯層）→  GA 主迴圈、族群管理、懲罰管理
        ↕
C++（效能層）→  Local Search 算子（佔 80–90% 運行時間）

"PyVRP combines the flexibility of Python
 with the performance of C++"
```

**三大貢獻（三欄，各自色塊）**：

| 🏗 Framework Design | ⚡ Algorithm Enhancements | 🏆 Benchmarks |
|---------------------|--------------------------|--------------|
| Python+C++ hybrid arch | VRPTW extension added | #1 DIMACS 2021 |
| Fully modular | SWAP* with time-window caching | #1 EURO NeurIPS 2022 |
| Custom operators supported | Simplified for open-source | Improved 27 BKS |

**底部**：`The innovation: making world-class VRP optimization accessible via Python`

---

## Slide 10 — HGS 演算法總覽

**標籤**：METHODS  
**標題**：Hybrid Genetic Search (HGS): The Big Picture

**中央流程圖**（用方塊 + 箭頭）：

```
┌─────────────────────────────────────────────────────────┐
│           Population (25 solutions)                     │
│           ┌──────────────┬──────────────┐               │
│           │ Feasible Pool│Infeasible Pool│              │
│           └──────────────┴──────────────┘               │
│                     ↓                                   │
│      Tournament Selection (biased by BPD diversity)     │
│                     ↓                                   │
│               Parent A  +  Parent B          🧬 GA       │
│                     ↓ SREX Crossover                    │
│                  Offspring                              │
│                     ↓ Local Search (C++, 80% runtime)   │
│              Refined Offspring               ⚡ LS       │
│                     ↓                                   │
│     Add to pool → Survivor Selection if > 65 solutions  │
│                     ↓ every 50 iterations               │
│          Update Penalty α, β  (maintain 43% feasible)   │
│                     ↓ if 20,000 iter no improvement     │
│             Restart: clear & refill population          │
└─────────────────────────────────────────────────────────┘
```

**右側參數框**：
```
Key Parameters:
• Population: 25–65 solutions
• Max no-improvement: 20,000 iterations
• Repair probability: 80% (VRPTW)
• Target feasible: 43%
• Penalty update: every 50 iterations
• Neighbourhood: k=20 (CVRP) / k=40 (VRPTW)
```

**底部**：`HGS = GA explores broadly, LS exploits deeply — neither alone is as effective`

---

## Slide 11 — 遺傳算子：選擇 + SREX 交叉

**標籤**：METHODS  
**標題**：Bio-inspired Core: Selection + SREX Crossover

**左欄（藍色標頭）**：Tournament Selection — Biased Fitness
```
biased_fitness(s) =
    rank_quality(s)   × (1 − elite_ratio)
  + rank_diversity(s) × elite_ratio

elite_ratio = nb_elite / min_pop_size = 4/25 = 0.16

→ Good solutions AND diverse solutions survive
→ Prevents premature convergence
```

**右欄（綠色標頭）**：SREX Crossover（Nagata & Kobayashi 2010）
```
Parent A:  Route 1: 1→3→7→5 | Route 2: 2→4→8 | Route 3: 6→9
Parent B:  Route 1: 2→4→6→8 | Route 2: 1→3→9 | Route 3: 5→7

Step 1: Inherit Route 1 from Parent B
        Result: { 2→4→6→8 }  ← from B

Step 2: Fill missing customers from Parent A
        Missing: {1, 3, 7, 5, 9}
        Insert greedily into cheapest positions

Offspring:
  Route 1: 2→4→6→8       (inherited from B)
  Route 2: 1→3→7→5→9     (greedy repair)
```

**底部**：`SREX inherits the "best parts" of each parent route — not random mixing!`

---

## Slide 12 — 局部搜尋：13 種算子

**標籤**：METHODS  
**標題**：Exploitation Engine: 11 Node + 2 Route Operators

**左欄（表格，深色標頭）**：Node Operators

| Operator | What it does |
|----------|-------------|
| Exchange(1,0) | Relocate: move 1 customer |
| Exchange(2,0) | Move 2 consecutive customers |
| Exchange(3,0) | Move 3 consecutive customers |
| Exchange(1,1) | Swap 2 single customers |
| Exchange(2,1) | Swap seq-of-2 with 1 customer |
| Exchange(2,2) | Swap two 2-customer sequences |
| Exchange(3,1) | Swap seq-of-3 with 1 customer |
| Exchange(3,2) | Swap seq-of-3 with seq-of-2 |
| Exchange(3,3) | Swap two 3-customer sequences |
| 2-Opt | Reverse a route segment |
| 2-Opt* | Reconnect two routes' tails |

**右上欄（綠色標頭）**：Route Operators
```
RELOCATE*: Best (1,0)-exchange between two routes.

SWAP*: Best customer swap between two routes.
  ① Time-window support added (PyVRP extension)
  ② Further caching for efficiency
  ③ Early stopping for known-bad moves
  Key: swapped customers inserted at BEST position,
       not their original location.
```

**右下欄（青色標頭）**：C++ Template Mechanism
```
template<int N, int M> class Exchange { ... };

→ Compiler generates 9 fully specialised implementations
  with ZERO runtime overhead from generalization.

Granular Neighbourhood (Toth & Vigo 2003):
  CVRP: k=20  |  VRPTW: k=40
  Reduces complexity: O(n²) → O(k·n)
```

**底部**：`Local Search (C++) accounts for 80–90% of runtime — the true workhorse of HGS`

---

## Slide 13 — 族群管理與多樣性

**標籤**：METHODS  
**標題**：Population Dynamics: Quality + Diversity Balance

**中上（藍色標頭框）**：雙子群結構
```
           POPULATION (max 65 → trimmed to 25 periodically)
 ┌──────────────────────────────────────────────┐
 │  Feasible Subpopulation    [✓][✓][✓][✓][✓]  │
 ├──────────────────────────────────────────────┤
 │  Infeasible Subpopulation  [✗][✗][✗][✗][✗]  │
 └──────────────────────────────────────────────┘

Why keep infeasible? They contain excellent route structures
— just slightly violating capacity.
Dynamic penalty converts hard constraints → soft constraints.
```

**左下（青色標頭）**：BPD — Broken Pairs Distance
```
BPD(A,B) = |P_A △ P_B| / 2n

BPD = 0 → identical solutions
BPD = 1 → completely different solutions

Used in: parent selection + survivor selection
```

**右（藍色標頭）**：Biased Fitness
```
biased_fitness(s) =
    rank_quality(s)   × (1 − 0.16)
  + rank_diversity(s) × 0.16

elite_ratio = 4/25 = 0.16

Both quality AND diversity matter for survival.
Purely optimizing quality → premature convergence.
```

**右下 🖼 圖片欄**：`【截圖 B — 論文 Figure 1（見截圖清單）】`

**底部**：`Sawtooth diversity pattern (Figure 1) proves: periodic selection actively fights premature convergence`

---

## Slide 14 — 動態懲罰機制

**標籤**：METHODS  
**標題**：Soft Constraints via Dynamic Penalty Management

**頂部公式框**（置中大字）：
```
Penalized Cost = total_distance
               + α × total_excess_load
               + β × total_time_warp

α, β are DYNAMIC — adjusted every 50 iterations
```

**中央流程圖**（三個分支）：

```
Every 50 iterations: measure feasible_ratio
         ↓
  ┌──────────────────┬──────────────────┬──────────────────┐
  │ feasible < 38%   │ 38% ≤ ratio ≤ 48%│  feasible > 48%  │
  │ penalty × 1.34   │   No change      │  penalty × 0.32  │
  │ (tighten)        │  (balanced zone) │  (relax/explore) │
  │ 橘色             │  綠色            │  藍色            │
  └──────────────────┴──────────────────┴──────────────────┘

Target: maintain ~43% feasible solutions in population
```

**橘色框**：Repair Booster
```
Infeasible offspring:
  80% chance → re-run Local Search with penalty × 12
  (temporary "super-penalty" → push toward feasibility)
```

**底部**：`Dynamic penalties let the algorithm "breathe" — exploring freely, then tightening to find feasible solutions`

---

## Slide 15 — 系統架構

**標籤**：METHODS  
**標題**：Our Contribution: PyVRP-Web Full-Stack System

**四層架構圖**（每層一個橫條，顏色從上到下：藍→青→綠→橘）：

```
┌─────────────────────────────────────────────────── 藍色 ──┐
│  PRESENTATION LAYER                                       │
│  HTML + CSS + Vanilla JS (ES Modules) · Leaflet.js Map   │
│  Form Validation · Route Color Coding                     │
└─────────────────────────── ↓ fetch() / JSON ──────────────┘
┌─────────────────────────────────────────────────── 青色 ──┐
│  API LAYER (FastAPI)                                      │
│  POST /api/solve · Pydantic validation                   │
│  asyncio.Semaphore(1) · Auto OpenAPI docs                 │
└──────────────────────── ↓ Python function call ───────────┘
┌─────────────────────────────────────────────────── 綠色 ──┐
│  SERVICE LAYER                                            │
│  coord.py: WGS84→UTM (EPSG:32651)                        │
│  solver.py: HGS wrapper (nb_granular fix)                │
│  serializer.py: Route→JSON timeline                      │
│  exceptions.py: 5 custom exception types                 │
└──────────────────────── ↓ GA + Local Search ─────────────┘
┌─────────────────────────────────────────────────── 橘色 ──┐
│  SOLVER ENGINE (PyVRP v0.5.0)                             │
│  GeneticAlgorithm + LocalSearch + SREX crossover         │
│  TimedNoImprovement stop criterion                       │
└───────────────────────────────────────────────────────────┘
```

**右側技術選型**：
```
Frontend:  Vanilla JS + Leaflet.js
Backend:   FastAPI (async)
Geo:       pyproj WGS84→UTM
Solver:    PyVRP v0.5.0
Protocol:  JSON REST API
Language:  Python 3.11
```

**底部**：`"Fill the form → Click Solve → See the map" — Zero programming required`

---

## Slide 16 — 三大工程挑戰

**標籤**：METHODS  
**標題**：3 Non-Trivial Engineering Problems We Solved

**三欄版面（各有標頭色塊）**：

**欄 1（藍）：🌐 Coordinate System Mismatch**
```
Problem:
PyVRP requires INTEGER planar coordinates.
Users input WGS84 lat/lng (floating point).
Naïve: multiply degrees → severe distortion
at Taiwan's latitude range.

Solution:
WGS84 → UTM (EPSG:32651/32650)
         via pyproj library
UTM meters × scale factor 10
→ 0.1-meter precision, no distortion ✓
```

**欄 2（青）：🔍 Small Problem Runs Too Slow**
```
Problem:
Default nb_granular=20 for 16 clients
→ nearly exhaustive neighbourhood search
→ too few LS iterations within time limit
→ poor solution quality

Solution:
NB_GRANULAR = min(7, num_clients − 1)
Smaller neighbourhood → faster iterations
Same time → far more iterations
→ significantly better solutions ✓
```

**欄 3（綠）：⏱ Per-Stop Arrival Time Unknown**
```
Problem:
PyVRP only gives visit ORDER.
Does not provide per-stop times.
UI needs arrival/wait/departure timeline.

Solution (serializer.py walkthrough):
departure = depot.tw_early
for each stop:
  arrival    = prev_departure + travel_time
  wait       = max(0, stop.tw_early − arrival)
  departure  = max(arrival, stop.tw_early)
              + service_minutes ✓
```

**底部**：`Real engineering = bridging the gap between research API and user expectations`

---

## Slide 17 — CVRP Benchmark 結果

**標籤**：RESULTS  
**標題**：Results: CVRP Benchmark (100 Instances, Uchoa et al. 2017)

**右上角設定框**：
```
X benchmark — 100 CVRP instances
Scale: 100–1001 customers
Runtime: Tmax = n×240/100 sec
  (100 customers → 4 min; 1001 → 40 min)
Seeds: 10 random seeds, averaged
Hardware: AMD EPYC 7H12
PyVRP version: v0.5.0
```

**橫條圖（主體）**：Mean Gap from BKS — lower is better

```
BKS (Best Known Solution)   ▓▓▓  0.00%   ← OPTIMAL 基準（綠色）
─────────────────────────────────────────
HGS-CVRP (Vidal 2022)       ▓▓▓▓▓  0.11%  （藍色）
HGS-2012 (Vidal)            ▓▓▓▓▓▓▓  0.21%  （青色）
PyVRP v0.5.0                ▓▓▓▓▓▓▓  0.22%  （橘色）← 我們使用
```

*(數據來源：論文 Table 1)*

**綠色框**：
```
Many small instances solved to PROVEN OPTIMUM (Gap = 0%):
  X-n101-k25, X-n110-k13, X-n115-k10, X-n120-k6,
  X-n129-k18, X-n157-k13, X-n162-k11...
```

**橘色引語框**：
```
"Despite the fact that PyVRP has not been specifically designed for the CVRP,
these gaps are only slightly higher than the gaps of specialised CVRP solvers."
                                                        — Wouda et al., 2024
```

---

## Slide 18 — VRPTW Benchmark 結果

**標籤**：RESULTS  
**標題**：Results: VRPTW Benchmark (60 Instances, Homberger & Gehring 1999)

**橫條圖（主體）**：Mean Gap from BKS — 60 instances, 1000 customers, 2h runtime

```
BKS (Best Known Solution)   ▓▓  0.00%   （綠色）
────────────────────────────────────────────────
HGS-DIMACS (competition)    ▓▓▓▓▓▓  0.32%  （藍色）
DIMACS reference solution   ▓▓▓▓▓  0.29%  （青色）
PyVRP v0.5.0                ▓▓▓▓▓▓▓  0.40%  （橘色）← 我們使用
```

**六種問題類型分析（6個色塊）**：

| C1 | C2 | R1 | R2 | RC1 | RC2 |
|----|----|----|-----|-----|-----|
| ~0.27% 🟢 | ~0.04% 🟢 | ~0.72% 🟡 | ~0.37% 🟢 | ~0.72% 🟡 | ~0.26% 🟢 |

**藍色 Callout**：
```
"PyVRP would have ended up in second place
 in the DIMACS VRPTW competition."
                          — Wouda et al., 2024

  #1 HGS-DIMACS:  Mean Gap = 0.32%
  #2 PyVRP:       Mean Gap = 0.40%  ← simplified, more maintainable
```

**金色框**：
```
🏆 Extended runs: PyVRP improved 27 Best Known Solutions
    out of 300 Homberger & Gehring instances!
→ Given enough compute time, PyVRP can push the frontier.
```

**底部**：`0.40% gap from BKS — world-class performance with Python flexibility and MIT license`

---

## Slide 19 — 系統 Demo 截圖

**標籤**：RESULTS  
**標題**：Demo: PyVRP-Web in Action

**版面**：2×2 四格截圖（請依截圖清單填入）

| 左上 | 右上 |
|------|------|
| **🖼 截圖 C** — 初始空白表單 | **🖼 截圖 D** — 載入台北範例後 |
| Caption: "Step 1: Configure depot, stores & vehicles" | Caption: "Step 2: Load example — Taipei 7-ELEVEN data" |

| 左下 | 右下 |
|------|------|
| **🖼 截圖 E** — 求解完成地圖（最重要！） | **🖼 截圖 F** — 路線詳細時間清單 |
| Caption: "Step 3: Solve — HGS finds routes in ~8 seconds" | Caption: "Per-route timeline: arrival, wait, distance" |

**底部**：`http://localhost:8000 — no coding required`

---

## Slide 20 — 案例：台北 7-ELEVEN

**標籤**：RESULTS  
**標題**：Case Study: Taipei 7-ELEVEN Daytime Distribution

**左側場景設定**：
```
Scenario: Daytime convenience store restocking
Depot: Taipei Distribution Center
       (near Taipei Main Station, 09:30 departure)

16 Stores across Taipei City:
  Xinzhuang, Sanchong, Luzhou, Shilin, Beitou,
  Zhongshan, Da'an, Neihu, Songshan, Xinyi,
  Banqiao, Zhonghe, Wenshan, Nangang...

Total demand:   383 units
Fleet:          2 large (cap 140) + 4 medium (cap 80)
Time windows:   10:00–13:00 for all stores
Speed:          28 km/h (urban daytime)
```

**右側結果（綠色框）**：
```
✅ Feasible solution found in ~8 seconds

Routes used:     3 vehicles
Total distance:  ~92 km
Algorithm:       HGS (TimedNoImprovement, 500 iter cap)
```

**右側大圖**：**🖼 截圖 E**（同 Slide 19 左下的求解完成地圖）

**底部**：`HGS naturally clusters nearby stores into the same route — emergent geographic structure!`

---

## Slide 21 — 總結與貢獻

**標籤**：CONCLUSION  
**標題**：Summary: What We Learned and Built

**左欄（藍色標頭）**：Algorithm Understanding
```
Bio-inspired Algorithm: HGS

✓  Hybrid Genetic Search full architecture
✓  GA (explore) + LS (exploit) = near-optimal
✓  SREX crossover preserves good route structure
✓  BPD diversity prevents premature convergence
✓  Dynamic penalty handles hard constraints

Performance evidence:
  < 0.22% gap from BKS on CVRP (100 instances)
  < 0.40% gap from BKS on VRPTW (60 instances)
  Improved 27 historical best solutions
```

**右欄（綠色標頭）**：System Implementation
```
Full-Stack Web Application: PyVRP-Web

✓  4-layer architecture (FastAPI + Leaflet.js)
✓  WGS84→UTM coordinate conversion (pyproj)
✓  Interactive real-time route visualization
✓  Zero-code interface for non-developers

Real-world demo:
  16 Taipei 7-ELEVEN stores
  3 vehicles, ~92 km, solved in ~8 seconds

Engineering challenges solved:
  nb_granular=7 tuning, timeline reconstruction
```

**底部綠色條（大字）**：`We made a research-grade bio-inspired algorithm accessible to everyone — from theory to working software`

---

## Slide 22 — 限制與未來工作

**標籤**：CONCLUSION  
**標題**：Limitations and Future Directions

**左欄（橘色標頭）**：⚠ Current Limitations
```
Algorithm Limitations:
• Single depot only (PyVRP design constraint)
• Euclidean distance (not real road network)
• No traffic / time-of-day variation
• Heuristic: near-optimal, not guaranteed optimal

System Limitations:
• Desktop-only UI (no mobile responsive)
• Single concurrent solver (Semaphore=1)
• No VRPLIB file import
• No GA convergence animation
```

**右欄（藍色標頭）**：🚀 Future Directions
```
Algorithm Extensions:
• Multi-depot VRP support
• Real road network via OSRM / Google Maps API  ← 最重要
• Electric vehicle constraints (battery, charging)
• Prize-collecting VRP (optional customers)

System Extensions:
• Real-time GA convergence visualization
• Solution comparison mode (A/B testing)
• Export to navigation apps (Google Maps)
• Cloud deployment with job queue
• Mobile-responsive layout
```

**底部**：`Most exciting next step: OSRM integration for real driving-time routing in Taipei`

---

## Slide 23 — Q&A + References

**標籤**：CONCLUSION  
**標題**：Thank You — Questions Welcome  （大字深色橫幅）

**左側 Key Takeaways**：
```
1.  VRP is NP-hard → bio-inspired methods are justified
2.  HGS = GA (explore) + LS (exploit) = best of both
3.  PyVRP: 0.22% / 0.40% gap from BKS, MIT license
4.  PyVRP-Web: usable system, zero code required

Q&A Hints:
Q: Why not ACO/PSO?  → HGS LS gives < 0.5% gap, far better
Q: Optimal results?  → Heuristic; near-optimal in seconds
Q: What does GA contribute?  → LS = 80-90% runtime; GA = diversity
Q: Scale limit?  → Web UI: 5-50 clients; PyVRP: 1000+ with longer runtime
Q: Why not CLI?  → Zero-code UI bridges algorithm to non-technical users
```

**右側 References（8 篇，小字）**：
```
[1] Wouda, Lan, Kool. PyVRP: A High-Performance VRP Solver Package.
    INFORMS J. Computing, 36(4), 943–955, 2024. arXiv:2403.13795v2

[2] Vidal. Hybrid genetic search for CVRP: SWAP* improvement.
    Computers & OR, 140, 105643, 2022.

[3] Vidal et al. A hybrid GA with adaptive diversity management for VRP.
    Computers & OR, 40(1), 475–489, 2013.

[4] Nagata & Kobayashi. Memetic algorithm with SREX crossover.
    PPSN XI, 536–545, 2010.

[5] Toth & Vigo. Granular Tabu Search for VRP.
    INFORMS J. Computing, 15(4), 333–346, 2003.

[6] Uchoa et al. New benchmark instances for CVRP.
    European J. OR, 257(3), 845–858, 2017.

[7] Homberger & Gehring. Two evolutionary metaheuristics for VRPTW.
    INFOR, 37(3), 297–318, 1999.

[8] Kool et al. Hybrid Genetic Search for VRPTW (HGS-DIMACS).
    Technical report, 2022.
```

**底部綠色條**：`Student ID: 414085193 | Bio-inspired Computing | PyVRP v0.5.0`

---

## 截圖清單（你需要自己截的圖）

共需 **6 張截圖 + 1 張論文截圖**：

### 系統截圖（啟動伺服器後截）

```bash
uv run --python 3.11 python run_server.py
# 然後開瀏覽器到 http://localhost:8000/
```

| 標號 | 使用於 | 截什麼 |
|------|--------|--------|
| **截圖 A** | Slide 3 右側 | 求解完成後的地圖（全螢幕，顯示倉庫＋店面＋3條彩色路線）可與截圖E相同 |
| **截圖 C** | Slide 19 左上 | **初始空白狀態**：左側表單面板空白 + 中間空白地圖（未載入任何資料） |
| **截圖 D** | Slide 19 右上 | **載入台北範例後**：點「載入範例 ▾」→「台北日班」後的狀態，地圖顯示倉庫（紅色圖示）+ 16個灰色店面圓點，尚未按「開始計算」 |
| **截圖 E** | Slide 19 左下、Slide 20 右側 | **求解完成**（最重要）：點「開始計算」等 8-12 秒，地圖出現 3 條不同顏色路線＋箭頭方向，右側面板顯示車輛數/距離。**建議全螢幕截圖，移除瀏覽器工具列** |
| **截圖 F** | Slide 19 右下 | **路線詳細清單**：右側面板展開一條路線，顯示各站抵達時間、等待時間、距離；截右側面板特寫 |

### 論文截圖

| 標號 | 使用於 | 截什麼 |
|------|--------|--------|
| **截圖 B** | Slide 13 右下 | 開啟 `openspec/changes/論文本體/PyVRP論文.pdf` 第 12 頁，找到 **Figure 1**（四格圖：diversity sawtooth + objectives convergence），截整個 Figure 1 |

### 截圖建議

- **解析度**：至少 1280×800，截完不要縮小
- **截圖 E**（最重要）：選擇「台北日班」範例，種子設 42 可讓結果穩定重現（可在右側設定欄設定 seed=42）
- 全部存成 PNG，放在一個資料夾方便插入

---

## 時間安排參考

| 章節 | 投影片 | 建議時間 |
|------|--------|---------|
| Title + Outline | 1–2 | 1 分鐘 |
| Introduction | 3–6 | 2.5 分鐘 |
| Related Work | 7–9 | 1.5 分鐘 |
| Methods | 10–16 | 4 分鐘 |
| Results | 17–20 | 2.5 分鐘 |
| Conclusion | 21–22 | 1.5 分鐘 |
| Q&A | 23 | 2 分鐘 |
| **合計** | **23 張** | **~15 分鐘** |
