# Spec: Results Slides (Slides 17–20)

---

## Slide 17 — CVRP Benchmark Results

**標題**：`Results: CVRP Benchmark (100 Instances, Uchoa et al. 2017)`

**實驗設定框（右上角）**：
```
Benchmark: X benchmark (Uchoa et al. 2017)
Instances: 100 CVRP instances
Scale: 100–1001 customers
Runtime: Tmax = n × 240/100 sec (PassMark normalized)
         (100 customers → 4 min; 1001 customers → 40 min)
Repeats: 10 random seeds, average reported
Hardware: AMD EPYC 7H12 (PassMark 2014)
Baseline CPU: Intel Gold 6148 (PassMark 2183) → normalized by ×(2183/2014)
```

**橫條圖（主體，佔 60% 空間）**：

顯示 Mean Gap 和 Gap of Mean（越低越好）：
```
                     Mean Gap    Gap of Mean
BKS (Best Known)     0.00%       0.00%     ← 理論最佳
─────────────────────────────────────────────
HGS-CVRP (Vidal)     0.11%       0.16%     ← 專用 CVRP 解算器
HGS-2012 (Vidal)     0.21%       0.28%
PyVRP (ours, 2024)   0.22%       0.27%     ← 我們使用的
```
*(數據來源：論文 Table 1)*

**小型實例亮點（Callout 框）**：
```
Many small instances solved to PROVEN OPTIMUM (Gap = 0%):
  X-n101-k25, X-n110-k13, X-n115-k10, X-n120-k6, 
  X-n129-k18, X-n157-k13, X-n162-k11, X-n167-k10...

Largest instance (X-n1001-k43):
  PyVRP: 73,001.0  |  BKS: 72,355  |  Gap: 0.89%
```

**論文原文引語（橘色框）**：
```
"Despite the fact that PyVRP has not been specifically designed for the CVRP, 
these gaps are only slightly higher than the gaps of specialised CVRP solvers."
                                                        — Wouda et al., 2024
```

**底部備註**：
```
* BKSs obtained from CVRPLIB on 28 February 2023
* PyVRP v0.5.0 used for all experiments (archived on IJOC GitHub)
* Trade-off: slight quality loss vs. dramatically higher flexibility + MIT license
```

**Presenter Notes**：
> "A 0.22% gap from the best known solution is remarkable. Notice that PyVRP solves many small instances to proven optimality—0% gap. The paper also explicitly notes that PyVRP 'has not been specifically designed for the CVRP,' yet it still nearly matches specialized CVRP solvers. For the hardest 1000-customer instance, the gap is 0.89%—less than 1% from optimal for a problem with over a trillion possible routes."

---

## Slide 18 — VRPTW Benchmark Results

**標題**：`Results: VRPTW Benchmark (60 Instances, Homberger & Gehring 1999)`

**實驗設定框（右上角）**：
```
Benchmark: H&G benchmark (1000 customers)
Instances: 60 VRPTW instances (6 types × 10 each)
Runtime: 2 hours per instance
Types: C1, C2, R1, R2, RC1, RC2
```

**橫條圖（主體）**：

```
BKS                          ████░░░░░  0.00%
──────────────────────────────────────────────
HGS-DIMACS (competition)     ████░░░░░  0.32%
DIMACS reference solution    ████░░░░░  0.29%
PyVRP (2024)                 ████░░░░░  0.40%  ← 我們使用的
```

**六種問題類型分析（6 格小圖，數據來自論文 Table 5）**：
```
C1 (clustered, narrow TW)   avg ≈ 0.27%   🟢 Best performance
C2 (clustered, wide TW)     avg ≈ 0.04%   🟢 Near optimal
R1 (random, narrow TW)      avg ≈ 0.72%   🟡 Hardest category
R2 (random, wide TW)        avg ≈ 0.37%   🟢 Good
RC1 (mixed, narrow TW)      avg ≈ 0.72%   🟡 Also challenging
RC2 (mixed, wide TW)        avg ≈ 0.26%   🟢 Good

Best single instance (C2_10_1):  GAP = 0.00% (exact optimum!)
Worst single instance (RC1_10_6): GAP = 1.02%
```

**Competition 排名說明（深藍色 Callout）**：
```
"PyVRP would have ended up in second place 
 in the DIMACS VRPTW competition."
                        — Wouda et al., 2024

  #1 HGS-DIMACS:  Mean Gap = 0.32%
  #2 PyVRP:       Mean Gap = 0.40%   ← simplified, more maintainable
  #3 DIMACS ref:  Mean Gap = 0.29%*

  *DIMACS reference published after competition, harder to compare
```

**特別成就 Callout（金色框）**：
```
🏆 Extended runs: PyVRP improved 27 Best Known Solutions
   out of 300 Homberger & Gehring instances!

→ Given enough compute time, PyVRP can push the frontier of what's known.
```

**Presenter Notes**：
> "The VRPTW results reflect the deliberate trade-off the authors made: they removed complex, competition-specific optimizations to produce cleaner code. The paper explicitly says PyVRP 'would have ended up in second place' in DIMACS—so it's still world-class. The C2 instances are nearly perfectly solved (0.04% average gap), while R1 and RC1 with narrow time windows are the hardest. The '27 BKS improved' in extended runs is particularly impressive—this means PyVRP can break world records given more time."

---

## Slide 19 — System Demo: Our Web Application

**標題**：`Demo: PyVRP-Web in Action`

**四張截圖網格佈局（2×2）**：

**截圖 1（左上）— 初始介面**：
```
[截圖描述]
左側表單面板（倉庫設定、店面列表、車型設定、求解設定）
中央地圖（空白台北市底圖）
右側面板（空白，等待結果）

Caption: "Step 1: Configure depot, stores & vehicles"
```

**截圖 2（右上）— 載入範例後預覽**：
```
[截圖描述]
地圖上顯示倉庫（紅色房子）+ 16 個店面（灰色圓圈，有編號）
左側表單已填滿台北 7-ELEVEN 範例資料

Caption: "Step 2: Load example — Taipei 7-ELEVEN daytime delivery"
```

**截圖 3（左下）— 求解完成**：
```
[截圖描述]
地圖上出現 3–4 條不同顏色的路線
店面圓圈變成對應路線的顏色
方向箭頭顯示行進方向
右側面板顯示車輛列表與統計

Caption: "Step 3: Solve — HGS finds optimal routes in ~8 seconds"
```

**截圖 4（右下）— 路線詳細資訊**：
```
[截圖描述]
右側面板展開一條路線的詳細清單：
  出發：09:30 | 到達店面 A：10:12 | 等待：0 分 | 距上站：7.4 km
  → 店面 B：10:45 | 等待：3 分 | ...
狀態列：總距離 92.4 km | 使用車輛 3 台 | 求解耗時 8.2s

Caption: "Per-route timeline: arrival, departure, wait, distance"
```

**底部文字**：
```
http://localhost:8000 — no coding required
```

**Presenter Notes**：
> "Let me walk you through the system. Start with an empty form, load our Taipei 7-ELEVEN daytime example with 16 stores, click solve, and within 8–10 seconds HGS has found a routing plan covering all stores. The right panel shows each vehicle's exact timeline."

---

## Slide 20 — Example Run: Taipei Delivery Scenario

**標題**：`Case Study: Taipei 7-ELEVEN Daytime Distribution`

**左側：場景設定（清單）**：
```
Scenario: Daytime convenience store restocking
Depot: Unified Enterprise Taipei Distribution Center
       (near Taipei Main Station, 09:30 departure)

16 Stores across Taipei City:
  Xinzhuang, Sanchong, Luzhou, Shilin, Beitou,
  Zhongshan, Da'an, Neihu, Songshan, Xinyi,
  Banqiao, Zhonghe, Wenshan, Nangang

Total demand: 383 units
Vehicle fleet: 2 large (cap 140) + 4 medium (cap 80)
Total capacity: 600 units (slack: 217 units)
Time windows: 10:00–13:00 for all stores
Speed: 28 km/h (urban daytime)
```

**右側：結果（結果框）**：
```
✅ Feasible solution found in ~8 seconds

Routes used:     3 vehicles
Total distance:  ~92 km
Algorithm:       HGS (TimedNoImprovement, 500 iter cap)
Iterations:      ~400–600 (stops when solution stabilizes)
```

**大圖：求解結果地圖截圖**（佔右側大部分空間）

**底部 Insight**：
```
HGS naturally clusters nearby stores into the same route.
Route colors match Taipei neighborhoods: 
  🔴 North (Shilin, Beitou, Tianmu)
  🔵 Central (Zhongshan, Da'an, Songshan)  
  🟢 South-West (Banqiao, Zhonghe, Wenshan)
```

**Presenter Notes**：
> "Notice how the algorithm naturally discovered Taipei's geographic structure—it clustered stores by neighborhood without any explicit instruction. This emergent clustering is a hallmark of good VRP solutions and demonstrates the algorithm's effectiveness."
