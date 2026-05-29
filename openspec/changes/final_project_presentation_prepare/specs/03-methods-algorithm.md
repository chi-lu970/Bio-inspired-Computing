# Spec: Methods — HGS Algorithm Slides (Slides 10–14)

---

## Slide 10 — HGS Algorithm Overview

**標題**：`Hybrid Genetic Search (HGS): The Big Picture`

**主要流程圖（佔投影片 70% 空間）**：

```
┌─────────────────────────────────────────────────────────────────┐
│                         HGS MAIN LOOP                           │
│                                                                 │
│  Population (25 solutions)                                      │
│  ┌──────────────────┬──────────────────┐                        │
│  │  Feasible Pool   │ Infeasible Pool  │                        │
│  └──────────────────┴──────────────────┘                        │
│           │                                                     │
│           ▼ Tournament Selection (k=2, biased by BPD)           │
│      Parent A + Parent B                                        │
│           │                                                     │
│           ▼ SREX Crossover                                      │
│        Offspring                                                │
│           │                                                     │
│           ▼ Local Search (C++, 80% of runtime)                  │
│     Refined Offspring                                           │
│           │                                                     │
│    ┌──────┴───────┐                                             │
│    ▼              ▼                                             │
│  feasible?    infeasible? ──► (80% chance) Repair Attempt       │
│    │                                    (penalty × 12)          │
│    ▼                                                            │
│  Add to population → Survival Selection if >65 solutions        │
│           │                                                     │
│           ▼ Every 50 iterations                                 │
│    Update Penalty (maintain 43% feasible)                       │
│           │                                                     │
│           ▼ If 20,000 iterations no improvement                 │
│    Restart: clear population, refill randomly                   │
└─────────────────────────────────────────────────────────────────┘
```

**右側參數框**：
```
Key Parameters:
• Population: 25–65 solutions
• Max iterations: 20,000 before restart
• Repair probability: 80% (VRPTW)
• Target feasible: 43%
```

**Presenter Notes**：
> "The magic of HGS is this combination: genetic operators provide broad exploration across the solution space, while local search provides deep exploitation around each candidate. Neither alone would perform as well—the crossover without local search produces terrible offspring, and local search alone gets stuck in local optima."

---

## Slide 11 — Genetic Algorithm Component: Selection & Crossover

**標題**：`Bio-inspired Core: Selection + SREX Crossover`

**Section A — Tournament Selection（左半）**：
```
Biased Fitness = rank_quality × (1 - elite_ratio)
               + rank_diversity × elite_ratio

→ Good solutions AND diverse solutions both survive
→ Prevents premature convergence
```

```
[Parent A]                [Parent B]
Route 1: 1→3→7→5         Route 1: 2→4→6→8
Route 2: 2→4→8           Route 2: 1→3→9
Route 3: 6→9             Route 3: 5→7
```

**Section B — SREX Crossover（右半）**：

```
Step 1: Pick Route 1 from Parent B → inherit as-is
        Result: {2→4→6→8} ← from B

Step 2: From Parent A, fill missing customers greedily
        Missing: {1, 3, 7, 5, 9}
        Insert into cheapest positions

Step 3: Offspring
        Route 1: 2→4→6→8        (from B)
        Route 2: 1→3→7→5→9      (greedy repair from A)
```

**底部 Takeaway**：
```
SREX inherits the "best parts" of each parent route — not random mixing!
```

**Presenter Notes**：
> "The SREX crossover is clever: instead of randomly mixing routes, it selects complete good routes from one parent and fills missing customers using the other parent's structure. This preserves good sub-route structures that evolved over many iterations."

---

## Slide 12 — Local Search: Node & Route Operators

**標題**：`Exploitation Engine: 11 Node + 2 Route Operators`

**Section A — Node Operators（左欄，表格）**：

```
Operator         What it does
──────────────────────────────────────────
Exchange(1,0)    Relocate: move 1 customer
Exchange(2,0)    Move 2 consecutive customers
Exchange(3,0)    Move 3 consecutive customers
Exchange(1,1)    Swap 2 customers
Exchange(2,1)    Swap seq-of-2 with 1 customer
Exchange(2,2)    Swap two 2-customer sequences
Exchange(3,1)    Swap seq-of-3 with 1 customer
Exchange(3,2)    Swap seq-of-3 with seq-of-2
Exchange(3,3)    Swap two 3-customer sequences
2-Opt            Reverse a route segment
2-Opt*           Reconnect two routes' tails
```

**Section B — Route Operators（右欄）**：

```
RELOCATE*   Find best single-customer move 
            across ALL route pairs

SWAP*       Find best customer swap between 
            two routes (not position-bound)
            → PyVRP adds: time-window caching,
              early termination
```

**稀疏鄰域說明（底部）**：
```
Granular Neighbourhood: each customer only checks k=40 nearest neighbors
Reduces complexity from O(n²) to O(k×n) — makes large instances feasible
```

**Presenter Notes**：
> "The local search is where C++ earns its keep—these 13 operators run thousands of times per iteration. The granular neighbourhood trick is key: instead of checking all possible moves, each customer only considers its 40 nearest neighbors, reducing search time dramatically."

---

## Slide 13 — Population Management & Diversity

**標題**：`Population Dynamics: Quality + Diversity Balance`

**雙子群示意圖（中央）**：

```
             POPULATION
    ┌──────────────────────────────┐
    │   Feasible Subpopulation     │  (solutions satisfying all constraints)
    │   [■] [■] [□] [■] [□]...    │  
    ├──────────────────────────────┤
    │  Infeasible Subpopulation    │  (constraint violations tolerated)
    │   [●] [●] [●] [□] [●]...    │  
    └──────────────────────────────┘
    max size = 65  →  trimmed to 25 periodically
```

**BPD 多樣性指標說明**：
```
BPD (Broken Pairs Distance):
  Count edge-pairs that appear in A but not B (and vice versa)
  Normalized to [0, 1]

BPD = 0 → identical solutions
BPD = 1 → completely different solutions

Used in: parent selection (ensure parents are "different enough")
         survival selection (protect diverse solutions)
```

**Biased Fitness 公式**：
```
biased_fitness(s) = rank_quality(s) × (1 - elite_ratio)
                  + rank_diversity(s) × elite_ratio

Both quality AND diversity matter for survival.
```

**Presenter Notes**：
> "Why keep infeasible solutions? Because they might contain excellent route structures—just slightly violating a capacity constraint. The dynamic penalty system converts hard constraints into soft ones, allowing the algorithm to explore a larger solution space and escape local optima."

---

## Slide 14 — Penalty Management: Dynamic Constraint Handling

**標題**：`Soft Constraints via Dynamic Penalty`

**懲罰目標函數（公式框）**：

```
Penalized Cost = total_distance
               + capacity_penalty    × total_excess_load
               + time_warp_penalty   × total_time_warp

capacity_penalty and time_warp_penalty are DYNAMIC
```

**動態調整邏輯（流程圖）**：

```
Every 50 iterations: measure feasible_ratio

         feasible_ratio < 38%?
         ┌──── YES ──── penalty × 1.34  (make constraints harder to violate)
         │
         feasible_ratio > 48%?
         └──── YES ──── penalty × 0.32  (relax constraints, explore more)

         38% ≤ ratio ≤ 48%? → no change

Target: maintain ~43% feasible solutions in population
```

**修復機制（Repair Booster）**：
```
Infeasible offspring:
  80% chance → re-run local search with penalty × 12
  This aggressively pushes solution toward feasibility
  "Temporary super-penalty" trick
```

**底部 Takeaway**：
```
Dynamic penalties let the algorithm "breathe" — 
exploring freely, then tightening constraints to find feasible solutions.
```

**Presenter Notes**：
> "This is one of the most elegant parts of HGS: instead of hard-rejecting infeasible solutions, it uses dynamic penalty weights to steer the search. When too few solutions are feasible, it tightens penalties; when too many are feasible (meaning the search isn't exploring enough), it relaxes them."
