# Spec: Title + Introduction Slides (Slides 1–6)

---

## Slide 1 — Title Page

**標題（大字）**
```
PyVRP-Web: A Bio-inspired Vehicle Routing Solver
with Interactive Visualization
```

**副標題**
```
Applying Hybrid Genetic Search (HGS) to Real-World Logistics Optimization
```

**作者/課程資訊**
```
Bio-inspired Computing — Final Project
Student ID: 414085193
```

**視覺元素**：
- 背景：台北市地圖（淺色，模糊處理）
- 前景：3–4 條不同顏色的路線疊加其上
- 右下角：PyVRP logo 或遺傳演算法 DNA 圖示

**Presenter Notes**：
> 直接開始："Good [morning/afternoon]. Today I'd like to share a project that applies bio-inspired computing—specifically genetic algorithms—to solve one of the classic challenges in logistics: the Vehicle Routing Problem."

---

## Slide 2 — Agenda

**標題**：`Outline`

**內容（條列）**：
```
① Introduction      — What is VRP and why it's hard
② Related Work      — Prior solvers and HGS research lineage
③ Methods           — HGS algorithm + our fullstack system
④ Results           — Benchmark performance + live demo
⑤ Conclusion        — Contributions and future directions
```

**視覺元素**：5 個圓圈圖示，依序排成橫向流程

---

## Slide 3 — Problem Definition: What is VRP?

**標題**：`The Vehicle Routing Problem (VRP)`

**左側文字**：
```
Given:
• A depot (warehouse)
• n customers with delivery demands
• k vehicles with capacity constraints

Goal:
Minimize total travel distance
while serving every customer exactly once
```

**右側圖**：
- 台北市地圖截圖（來自我們的系統）
- 倉庫標記（紅色房子）
- 5–6 個客戶點（編號圓圈）
- 2–3 條不同顏色的配送路線

**底部 Takeaway**：
```
VRP = "How to dispatch delivery trucks to minimize cost"
```

**Presenter Notes**：
> "Imagine you manage a convenience store distribution center. Every morning you need to dispatch trucks to restock 20+ locations across Taipei—what's the most efficient routing plan? This is VRP."

---

## Slide 4 — Why VRP is Hard (NP-hard)

**標題**：`Why VRP is Computationally Hard`

**主要內容（並排兩欄）**：

*左欄 — 規模爆炸*：
```
Number of possible routes grows factorially:

  10 customers → 3,628,800 permutations
  20 customers → 2.4 × 10¹⁸ permutations
  50 customers → 3 × 10⁶⁴ permutations

Brute force: impossible even for modern supercomputers
```

*右欄 — NP-hard 說明*：
```
VRP is NP-hard:
• No known polynomial-time algorithm
• Exact solvers limited to ~100 customers
• Real logistics: 500–1000+ customers daily
→ Need heuristic / metaheuristic approaches
```

**底部 Takeaway**：
```
We need smart search strategies — this is where bio-inspired algorithms shine.
```

**Presenter Notes**：
> "If you tried every possible combination for a 50-customer problem, even at one billion operations per second, it would take longer than the age of the universe. We need a smarter approach."

---

## Slide 5 — Why Bio-inspired? The Evolution Analogy

**標題**：`Nature's Solution: Evolutionary Optimization`

**主要類比（大圖 + 對應文字）**：

```
NATURE                           ALGORITHM
──────────────────────────────────────────────────
Population of organisms     →    Population of candidate routes
Fitness (survival ability)  →    Objective: total distance
Crossover (reproduction)    →    SREX: exchange route segments
Mutation                    →    Local Search: move/swap customers
Natural Selection           →    Biased Fitness elimination
Generations                 →    Iterations (20,000+)
Surviving species           →    Near-optimal routing solution
```

**核心洞察（橘色 Callout Box）**：
```
Key Insight:
Pure GA offspring are low quality.
HGS pairs EVERY offspring with Local Search → dramatically better solutions.

"Exploration (GA) + Exploitation (LS) = Best of both worlds"
```

**視覺元素**：
- 左：DNA 雙螺旋或演化樹圖示
- 右：演算法流程符號對應

**Presenter Notes**：
> "Genetic algorithms mimic Darwinian evolution. We maintain a population of solutions, let good ones 'reproduce' by combining their routes, then apply local search to refine each offspring—just like how evolution refines traits across generations."

---

## Slide 6 — Our Contributions

**標題**：`What We Built`

**雙欄結構**：

*左欄 — Layer 1: Algorithm Understanding*
```
🔬 Deep dive into PyVRP (2024 INFORMS paper)
• HGS algorithm (Hybrid Genetic Search)
• 11 node operators + 2 route operators
• SREX crossover, BPD diversity metric
• Dynamic penalty management
```

*右欄 — Layer 2: Full-Stack System*
```
🌐 Web Application (PyVRP-Web)
• FastAPI backend with PyVRP integration
• WGS84 → UTM coordinate conversion
• Interactive map (Leaflet.js)
• Real-time route visualization
• Zero-code interface for non-developers
```

**底部 Takeaway Box（綠色）**：
```
We bridged research-grade bio-inspired optimization 
and real-world usable software — from algorithm to UI.
```

**Presenter Notes**：
> "Our contribution is two-layered: first, we analyzed and understood the PyVRP paper's HGS algorithm in depth; second, we wrapped it into a web application that anyone can use without writing a single line of code."
