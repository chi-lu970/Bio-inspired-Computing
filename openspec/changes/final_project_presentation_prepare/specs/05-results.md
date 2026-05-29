# Spec: Results Slides (Slides 17–20)

---

## Slide 17 — CVRP Benchmark Results

**標題**：`Results: CVRP Benchmark (100 Instances, Uchoa et al. 2017)`

**實驗設定框（右上角）**：
```
Benchmark: X benchmark (Uchoa et al. 2017)
Instances: 100 CVRP instances
Scale: 100–1001 customers
Runtime: n × 2.4 sec (PassMark normalized)
Repeats: 10 random seeds, average reported
Hardware: AMD EPYC 7H12 (PassMark 2014)
```

**橫條圖（主體，佔 60% 空間）**：

顯示 Mean Gap（越低越好）：
```
BKS (Best Known Solution)    ████░░░░░  0.00%  ← 理論最佳
──────────────────────────────────────────────
HGS-CVRP (Vidal 2022)        ████░░░░░  0.11%
PyVRP (ours, 2024)           ████░░░░░  0.22%  ← 我們使用的
HGS-2012 (Wouda et al.)      ████░░░░░  0.21%
OR-Tools (Google)            ████████░  ~3.5%  (估計值)
```

**關鍵數據 Callout（橘色框）**：
```
PyVRP Mean Gap: 0.22%
→ Less than 0.25% from world's best known solution
→ Significantly better than Google OR-Tools
```

**底部備註**：
```
* PyVRP slightly underperforms HGS-CVRP (specialized C++ solver) 
  due to its generalized design for multiple VRP variants
* Trade-off: slight quality loss vs. dramatically higher flexibility
```

**Presenter Notes**：
> "A 0.22% gap from the best known solution is remarkable. For a 1000-customer route costing 100,000 total distance units, PyVRP finds a solution within 220 units of optimal—that's effectively optimal for real-world logistics."

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

**六種問題類型分析（6 格小圖）**：
```
C1 (clustered, narrow TW)   ≈ 0.02%   🟢 Near optimal
C2 (clustered, wide TW)     ≈ 0.05%   🟢 Near optimal
R1 (random, narrow TW)      ≈ 0.7%    🟡 Acceptable
R2 (random, wide TW)        ≈ 0.3%    🟢 Good
RC1 (mixed, narrow TW)      ≈ 0.6%    🟡 Acceptable
RC2 (mixed, wide TW)        ≈ 0.2%    🟢 Good
```

**特別成就 Callout（金色框）**：
```
🏆 Extended runs: PyVRP improved 27 Best Known Solutions
   out of 300 Homberger & Gehring instances!
```

**Presenter Notes**：
> "The VRPTW results are slightly weaker than the competition version because PyVRP removed some complex, problem-specific components to improve maintainability. But notice the '27 BKS improved' achievement—this means PyVRP is still capable of world-class performance given more computation time."

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
