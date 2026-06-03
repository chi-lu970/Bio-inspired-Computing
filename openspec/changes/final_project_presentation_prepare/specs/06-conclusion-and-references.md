# Spec: Conclusion + Q&A + References (Slides 21–23)

---

## Slide 21 — Summary & Contributions

**標題**：`Summary: What We Learned and Built`

**雙欄貢獻框架**：

**左欄 — Algorithm Understanding（學術層）**：
```
🔬 Bio-inspired Algorithm: HGS

We understood and analyzed:
✓ Hybrid Genetic Search architecture
  • Genetic operators (SREX crossover, BPD diversity)
  • Local search (11 node + 2 route operators)
  • Dynamic penalty management
  • Restart mechanism

✓ Why it works:
  GA explores → LS exploits → Together they find near-optimal solutions

✓ Performance evidence:
  < 0.22% gap from BKS on CVRP (100 instances)
  < 0.40% gap from BKS on VRPTW (60 instances)
  Improved 27 historical best solutions
```

**右欄 — System Implementation（工程層）**：
```
🌐 Full-Stack Web Application: PyVRP-Web

We designed and built:
✓ 4-layer architecture
  • FastAPI REST backend
  • PyVRP HGS solver integration
  • WGS84→UTM coordinate conversion
  • Interactive Leaflet.js map

✓ Real-world features:
  • Zero-code interface
  • Live demo: Taipei 7-ELEVEN scenario
  • 3 vehicles, 16 stores, ~92 km optimized

✓ Engineering challenges solved:
  • sys.path conflict resolution
  • Neighbourhood size tuning (nb_granular=7)
  • Per-stop arrival time reconstruction
```

**底部核心訊息（大字、綠色框）**：
```
We made a research-grade bio-inspired algorithm 
accessible to everyone — 
from theory to working software.
```

---

## Slide 22 — Limitations & Future Work

**標題**：`Limitations and Future Directions`

**左欄 — Current Limitations（紅色圖示）**：
```
⚠️ Algorithm Limitations:
  • Single depot only (PyVRP design constraint)
  • Euclidean distance (not real road network)
  • No traffic/time-of-day variation
  • Heuristic: near-optimal, not guaranteed optimal

⚠️ System Limitations:
  • Desktop-only UI (no mobile responsive)
  • Single concurrent solver (Semaphore=1)
  • No VRPLIB file import
  • No GA convergence animation
```

**右欄 — Future Work（藍色圖示）**：
```
🚀 Algorithm Extensions:
  • Multi-depot VRP support
  • Real road network (OSRM/Google Maps API)
  • Electric vehicle constraints (battery, charging)
  • Prize-collecting VRP (optional customers)

🚀 System Extensions:
  • Real-time GA convergence visualization
  • Solution comparison mode (A/B testing)
  • Export to navigation apps (Google Maps)
  • Cloud deployment with job queue
  • Mobile-responsive layout
```

**Presenter Notes**：
> "The most exciting future direction is integrating with real road networks—currently we use Euclidean distance as a proxy. With OSRM or a traffic API, the system could provide routing plans that account for actual driving times, one-way streets, and real-time traffic."

---

## Slide 23 — Q&A + References

**標題**：`Thank You — Questions Welcome`

**左側 — 核心訊息回顧**：
```
Key Takeaways:
1. VRP is NP-hard → bio-inspired methods are justified
2. HGS = GA (explore) + LS (exploit) = best of both
3. PyVRP achieves near-BKS with Python flexibility
4. We wrapped it into a usable web system
```

**右側 — References（論文引用）**：
```
[1] Wouda, N.A., Lan, L., Kool, W. (2024). PyVRP: A High-Performance 
    VRP Solver Package. INFORMS Journal on Computing, 36(4), 943–955.
    arXiv:2403.13795v2 [cs.NE]

[2] Vidal, T. (2022). Hybrid genetic search for the CVRP: Open-source 
    implementation and SWAP* improvement. Computers & Operations Research, 140, 105643.

[3] Vidal, T., Crainic, T.G., Gendreau, M., Prins, C. (2013). A hybrid 
    genetic algorithm with adaptive diversity management for a large class 
    of VRP with time-windows. Computers & Operations Research, 40(1), 475–489.

[4] Nagata, Y., Kobayashi, S. (2010). A memetic algorithm for the pickup and 
    delivery problem with time windows using SREX crossover. PPSN XI, 536–545.

[5] Toth, P., Vigo, D. (2003). The Granular Tabu Search and Its Application 
    to the Vehicle-Routing Problem. INFORMS J. on Computing, 15(4), 333–346.

[6] Uchoa, E., et al. (2017). New benchmark instances for the Capacitated VRP.
    European Journal of Operational Research, 257(3), 845–858.

[7] Homberger, J., Gehring, H. (1999). Two evolutionary metaheuristics for VRPTW.
    INFOR: Information Systems and Operational Research, 37(3), 297–318.

[8] Kool, W., et al. (2022). Hybrid Genetic Search for the VRPTW: A High-Performance
    Implementation. Technical report (HGS-DIMACS, DIMACS competition winner).
```

**底部聯繫資訊**：
```
Student ID: 414085193
Course: Bio-inspired Computing
Source code: [local repository]
```

**Presenter Notes**：
> "I'm happy to take questions on the algorithm details, system architecture, or the performance results. If anyone is interested in testing the system, it runs locally on Python 3.11 with just a few pip installs."

---

## 附錄：預期提問與回答備稿

### Q1：為什麼選擇 HGS 而不是其他仿生演算法（如螞蟻演算法、粒子群優化）？

**回答**：
HGS 在 VRP 標準 Benchmark 上的表現明顯優於螞蟻演算法（ACO）和粒子群優化（PSO）。ACO 和 PSO 的解質量通常與 HGS 差距 2–5%，而 HGS 已被實驗證明接近精確解的 0.2%。對於 VRP 這個問題，局部搜尋（Local Search）的精細改善能力是關鍵，HGS 的混合架構比純演化算法更適合。

### Q2：你的系統能處理多大規模的問題？

**回答**：
目前 Web 介面的設計適合 5–50 個客戶。PyVRP 本身能處理 1000+ 客戶（論文 Benchmark），但求解時間從數秒增加到數小時。我們的系統設定 `max_runtime_seconds` 上限為 300 秒，對於大問題建議直接使用 PyVRP CLI。

### Q3：結果一定最優嗎？

**回答**：
不，VRP 是 NP-hard 問題，HGS 是啟發式（Heuristic）算法，不保證找到最優解。但 Benchmark 數據顯示，平均差距不到 0.5%，對實際物流場景而言已是高度可用的近最優解。精確解求解器（如 VRPSolver）可以保證最優，但只能處理數百個客戶以內的問題，且需要數小時甚至數天。

### Q4：HGS 的「遺傳」成分到底扮演多重要的角色？

**回答**：
這是個好問題。根據論文，局部搜尋（LS）佔了 **80–90% 的運行時間**（論文 p.7："Software profiling suggests that in PyVRP it accounts for 80-90% of the runtime"），也貢獻了大部分的解質量提升。遺傳操作（交叉）的核心價值是「多樣性維護」——確保搜尋不會困在局部最優。單純的局部搜尋（如模擬退火）容易陷入局部最優，而 GA 的族群機制提供了多個不同的搜尋起點，讓算法能夠逃脫局部陷阱。論文 Figure 1 的多樣性圖（鋸齒狀曲線）直接驗證了族群管理機制的有效性。

### Q5：為什麼要自己實作前端，不直接用 PyVRP 的 CLI？

**回答**：
CLI 只能由工程師使用，需要手動寫 Python 或 VRPLIB 格式文件。我們的目標是讓「物流規劃師」這類非技術人員也能使用這個求解器。Web 介面將輸入門檻從「需要寫程式」降到「填表單點按鈕」，也能直觀展示路線圖，是演算法視覺化的重要橋樑。
