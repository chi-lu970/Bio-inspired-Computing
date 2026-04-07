# PyVRP 完整解析文件

> **論文來源**：*PyVRP: A High-Performance VRP Solver Package*
> **作者**：Niels A. Wouda（格羅寧根大學）、Leon Lan（阿姆斯特丹自由大學）、Wouter Kool（ORTEC）
> **發表**：INFORMS Journal on Computing, 2024, Vol.36(4), pp.943–955
> **版本**：PyVRP v0.5.0（論文對應版本）

---

> **掃描狀態**：論文 PDF 全文（55,947 字元）+ 完整原始碼（所有 `.py` 模組）均已讀取。
> 涵蓋：正文 7 節（含 Listing 1/2 程式範例）、附錄 A（參數表 Table 3）、附錄 B（100 個 CVRP 實驗數據 Table 4）、附錄 C（60 個 VRPTW 實驗數據 Table 5）、所有參考文獻。

---

## 目錄

1. [PyVRP 是什麼？](#1-pyvrp-是什麼)
   - 1.1 一句話定義
   - 1.2 解的是什麼問題
   - 1.3 PyVRP 的設計哲學
   - 1.4 歷史成就
   - 1.5 作者核心貢獻分析
2. [問題數學定義](#2-問題數學定義)
3. [核心演算法 HGS](#3-核心演算法hgs)
4. [演算法完整流程](#4-演算法完整流程)
5. [技術實作詳解](#5-技術實作詳解)
   - 5.1 遺傳演算法主迴圈
   - 5.2 局部搜尋
   - 5.3 族群管理
   - 5.4 懲罰管理
   - 5.5 SREX 交叉算子
   - 5.6 多樣性指標 BPD
6. [程式碼架構](#6-程式碼架構)
7. [輸入參數速查表](#7-輸入參數速查表)
   - 7.1 倉庫參數
   - 7.2 客戶（店面）參數
   - 7.3 車輛參數
   - 7.4 邊（路段）參數
   - 7.5 求解控制參數
   - 7.6 座標說明
8. [完整 API 使用方式](#8-完整-api-使用方式)
   - 8.1 Model 高層介面（最簡單）
   - 8.2 底層完整組裝方式
   - 8.3 從檔案讀取 VRPLIB / Solomon 格式
   - 8.4 命令列介面（CLI）
   - 8.5 停止條件
   - 8.6 讀取與視覺化結果
9. [所有可調整的超參數](#9-所有可調整的超參數)
10. [效能表現](#10-效能表現)
11. [與其他求解器比較](#11-與其他求解器比較)
12. [如何延伸 PyVRP](#12-如何延伸-pyvrp)
13. [參考文獻](#13-參考文獻)

---

## 1. PyVRP 是什麼？

### 1.1 一句話定義

**PyVRP 是一個高效能的開源 VRP（車輛路徑問題）求解器。你輸入地圖和限制，它告訴你怎麼派車最省距離。**

### 1.2 解的是什麼問題

**VRP（Vehicle Routing Problem，車輛路徑問題）**：快遞公司有幾輛卡車、一個倉庫、若干客戶需要送貨，如何規劃每輛車的路線使總行駛距離最短？

PyVRP 目前支援兩種主要 VRP 變型：

| 問題 | 說明 | 限制 |
|------|------|------|
| **CVRP**（Capacitated VRP） | 每輛車有載重上限 | 容量限制 |
| **VRPTW**（VRP with Time Windows） | 每個客戶有時間窗，必須在指定時間段內服務 | 容量 + 時間窗 |

PyVRP 的設計同時支援更廣的 VRP 變型，包含：
- **獎賞型 VRP（Prize-collecting）**：客戶有 prize，不一定全部要訪問
- **釋放時間（Release times）**：貨物最早可以出發的時間
- **多車型**：不同容量的車輛混合使用

### 1.3 PyVRP 的設計哲學（論文核心主張）

> *"PyVRP combines the flexibility of Python with the performance of C++, by implementing (only) performance critical parts of the algorithm in C++, while being fully customisable at the Python level."*

- **只有效能瓶頸部分**（局部搜尋操作符、解的資料結構、BPD 計算）才用 C++ 實作
- **所有邏輯控制**（GA 主迴圈、族群管理、懲罰管理）用 Python 實作，使用者可輕鬆替換任何組件
- 靈活性帶來的效能損失可忽略不計

### 1.4 歷史成就

- **2021 DIMACS VRPTW 競賽：第一名**（HGS-DIMACS 版本）
- **EURO meets NeurIPS 2022 VRP 競賽靜態組：第一名**
- 延長運算後改善了 Homberger & Gehring 300 個實例中 **27 個歷史最佳解（BKS）**

---

### 1.5 作者核心貢獻分析

> **重要釐清**：這篇論文的作者（Niels A. Wouda、Leon Lan、Wouter Kool）**並非從零發明新演算法**，而是對現有 HGS 演算法進行深度優化與重新架構，並開發出 PyVRP 這個高效能開源工具。

#### 貢獻一：創立 PyVRP 軟體框架

**混合語言架構設計**
- 將最耗費運算資源的部分（局部搜尋，佔運行時間 80–90%）用 **C++** 撰寫
- 將演算法邏輯控管（遺傳演算法迴圈、族群管理、懲罰管理）用 **Python** 處理
- 結果：使用者享有 C++ 的速度，同時能像寫 Python 一樣輕鬆自定義規則

**高度可自定義性**
- 演算法完全模組化：交叉算子、族群管理、鄰域定義皆可獨立替換
- 這在過去的 VRP 工具中極難做到，對學術研究尤其重要

#### 貢獻二：對現有 HGS 演算法的優化與功能擴展

| 優化項目 | 說明 |
|----------|------|
| **新增 VRPTW 支援** | 原始 HGS-CVRP（Vidal 2022）僅支援載重限制，作者擴展並重設計使其高效處理時間窗約束 |
| **SWAP* 算子優化** | 加入時間窗支援、快取機制（Caching）與提前終止邏輯，顯著提升搜尋效率 |
| **程式碼精簡重構** | 將競賽用的「複雜且特定優化」程式碼，重構為更通用、更穩健的開源版本 |

#### 貢獻三：實驗證明達到頂尖效能

- 在標準 Benchmark（CVRP / VRPTW）上的表現與世界最強專門演算法並駕齊驅
- 明顯超越 Google OR-Tools 等知名商業工具
- 透過大量實驗（100 個 CVRP 實例 + 60 個 VRPTW 實例）提供完整比較數據

#### 一句話總結

> **作者「發明」了一個現代化開發工具（PyVRP），並「優化」了 HGS 演算法的實作效率與適用範圍，使其從專門的學術競賽程式碼，變成全球開發者都能使用的開源高效能引擎。**

---

## 2. 問題數學定義

### 2.1 CVRP

**輸入**：
- 客戶 $i = 1, \ldots, n$，各有需求量 $q_i \geq 0$
- 倉庫 $0$（路線的出發點和終點）
- 邊距離 $d_{ij} \geq 0$（客戶 $i$ 到客戶 $j$ 的距離）
- 車輛容量 $Q > 0$

**目標**：最小化所有路線的總行駛距離

**限制**：每台車的客戶總需求量 $\leq Q$；每個客戶恰好被一台車服務

### 2.2 VRPTW

在 CVRP 基礎上增加：
- 每個客戶 $i$ 有服務時間 $s_i \geq 0$
- 每個客戶 $i$ 有時間窗 $[e_i, l_i]$（$e_i \leq l_i$）：必須在此區間內開始服務
- 車輛可以「等待」（早到）但不能遲到
- 從 $i$ 到 $j$ 的行駛時間 $t_{ij} \geq 0$（PyVRP 支援距離矩陣和時間矩陣分開設定）

### 2.3 資料格式約定

PyVRP 內部使用**整數**距離和時間（效能考量，浮點數略慢）。
讀取 benchmark 實例時提供 helper function 處理四捨五入或截斷，支援：
- `round`：四捨五入到最近整數
- `trunc`：截斷為整數
- `trunc1` / `dimacs`：乘以 10 後截斷（保留一位小數精度，DIMACS 競賽用）
- `none`：不處理（預設）

---

## 3. 核心演算法 HGS

### 3.1 全名與起源

**HGS = Hybrid Genetic Search（混合遺傳搜尋）**

由法國學者 Thibaut Vidal 在 2013 年提出（論文：Vidal et al. 2013）。
PyVRP 在 HGS-CVRP（Vidal 2022）開源實作的基礎上：
- 新增時間窗支援（VRPTW）
- 用 Python 重寫外層邏輯
- 改善 SWAP* 算子加入時間窗 caching
- 簡化並移除對效能貢獻有限的複雜組件

### 3.2 為什麼叫「混合」？

```
HGS = 遺傳演算法（Genetic Algorithm）+ 局部搜尋（Local Search）
```

- **GA 負責廣泛探索（Exploration）**：維持多解族群，透過交配產生新後代，避免陷入局部最優
- **局部搜尋負責深度改善（Exploitation）**：對每個後代做精細調整，快速收斂到局部最優
- 關鍵洞察：純 GA 交配後的後代品質很差；每代緊接著跑局部搜尋能大幅提升效率

### 3.3 允許不可行解

HGS 的一個重要特性：族群中同時維持**可行解**與**不可行解**。
不可行解雖然違反容量或時間窗限制，但可能包含很好的路線結構。
透過**動態懲罰機制**，把硬限制轉成軟約束，讓局部搜尋探索更廣的解空間。

---

## 4. 演算法完整流程

### 4.1 主迴圈流程

```
初始化
├── 隨機生成 min_pop_size（預設 25）個解（不要求可行）
├── 設定懲罰初始值（容量懲罰 20，時間窗懲罰 6）
└── 族群分成兩個子群：可行解子群 & 不可行解子群

↓

主迴圈（重複直到停止條件）
├── [Step 1] 選親本
│   └── 從族群用二元競賽（k=2）選兩個解（父母）
│       同時考慮解的品質（objective）和多樣性（BPD）
│
├── [Step 2] 交叉（Crossover）
│   └── SREX 算子：從兩親本各取幾條路線，
│       合併後用貪心修復缺漏的客戶，產生後代解
│
├── [Step 3] 局部搜尋改善後代
│   ├── Phase 1 - search()：節點操作（11 種，按鄰域掃描）
│   ├── Phase 2 - intensify()：路線操作（2 種，跨路線）
│   └── 重複直到無法再改善
│
├── [Step 4] 修復不可行解（repair_probability 機率，CVRP=50%，VRPTW=80%）
│   └── 若後代不可行 → 把懲罰暫時乘以 12 倍 → 再跑一次局部搜尋
│
├── [Step 5] 加入族群
│   ├── 可行解加入可行子群，不可行解加入不可行子群
│   └── 若子群超過 max_size（min_pop_size + generation_size = 25+40=65）
│       → 淘汰（先刪重複解，再按 biased fitness 淘汰）
│       → 縮回至 min_pop_size（25）
│
├── [Step 6] 更新懲罰值（每 50/100 次記錄更新一次）
│   └── 目標：維持 43% 的解是可行的
│       可行 < 43% → 懲罰 × penalty_increase（1.25 or 1.34）
│       可行 > 43% → 懲罰 × penalty_decrease（0.85 or 0.32）
│
└── [Step 7] 重啟機制
    └── 若連續 nb_iter_no_improvement（20,000）次迭代無進展
        → 清空族群，重新用初始解填充

↓

輸出：Result 物件（最佳解 + 詳細統計數據）
```

### 4.2 停止條件

| 類型 | 說明 | 實作位置 |
|------|------|----------|
| `MaxRuntime(t)` | 超過 `t` 秒就停 | `stop/MaxRuntime.py` |
| `MaxIterations(n)` | 超過 `n` 次迭代就停 | `stop/MaxIterations.py` |
| `NoImprovement(n)` | 連續 `n` 次無改善就停 | `stop/NoImprovement.py` |
| `TimedNoImprovement` | 時間 + 無改善的組合條件 | `stop/TimedNoImprovement.py` |

---

## 5. 技術實作詳解

### 5.1 遺傳演算法主迴圈（`GeneticAlgorithm.py`）

**語言：Python**（邏輯協調，不是效能瓶頸）

核心參數（`GeneticAlgorithmParams`）：

| 參數 | 預設值 | 說明 |
|------|--------|------|
| `repair_probability` | 0.80 (VRPTW) / 0.50 (CVRP) | 對不可行後代嘗試修復的機率 |
| `nb_iter_no_improvement` | 20,000 | 連續無改善幾次後重啟族群 |

重啟機制（論文 Section 4.2）：
> 每次迭代記錄當前最佳 cost。若連續 20,000 次迭代最佳 cost 沒有改善，清空族群並用初始解重新填充，重新開始搜尋。

---

### 5.2 局部搜尋（`search/LocalSearch.py` + `search/_search.so`）

**Python 部分**：協調搜尋流程
**C++ 部分**：實際執行每個操作（效能關鍵，佔 80–90% 運行時間）

#### 5.2.1 兩階段搜尋

**Phase 1 — `search()`（節點操作）**：在稀疏鄰域內對客戶對掃描，找到第一個改善就立刻套用，持續至無改善。

**Phase 2 — `intensify()`（路線操作）**：對所有非空路線對進行更昂貴的跨路線操作。

#### 5.2.2 稀疏鄰域（Granular Neighbourhood）

**問題**：$n$ 個客戶有 $O(n^2)$ 種配對，全部評估太慢。
**解法**：每個客戶只看最近的 $k$（預設 40）個鄰居，把複雜度從 $O(n^2)$ 降到 $O(kn)$。

**近度計算公式**（Vidal et al. 2013）：
```
proximity(i, j) = distance(i, j)
                + weight_wait_time × max(e_j - t_ij - s_i - l_i, 0)
                + weight_time_warp × max(e_i + s_i + t_ij - l_j, 0)
                - prize(j)
```

其中 `weight_wait_time = 0.2`，`weight_time_warp = 1.0`（VRPTW 預設）。
CVRP 不使用時間相關項（全設為 0）。

使用者可以完全替換鄰域結構，或透過 `NeighbourhoodParams` 調整。

#### 5.2.3 節點操作（Node Operators，11 種）

> **共同特性**：每次只考慮客戶 $u$ 和其鄰域 $N(u)$ 中的客戶 $v$。

**(N, M)-exchange 系列**（論文 Section 4.3.1）：

| 算子 | 說明 |
|------|------|
| `Exchange(1,0)` | Relocate：把客戶 $u$ 插入到 $v$ 之後（移動） |
| `Exchange(2,0)` | 把 $u$ 及其後繼客戶一起移動 |
| `Exchange(3,0)` | 把 $u$ 及其後兩個客戶一起移動 |
| `Exchange(1,1)` | Swap：$u$ 和 $v$ 互換位置 |
| `Exchange(2,1)` | 兩客戶序列和一個客戶互換 |
| `Exchange(2,2)` | 兩客戶序列互換 |
| `Exchange(3,1)` | 三客戶序列和一個客戶互換 |
| `Exchange(3,2)` | 三客戶序列和兩客戶序列互換 |
| `Exchange(3,3)` | 三客戶序列互換 |

C++ 用 **template 機制**針對每種 (N,M) 組合生成高效的特化實作。

**MoveTwoClientsReversed**：
(2,0)-exchange 的變形，移動 $u$ 及其後繼客戶時，**反轉其順序**後插入 $v$ 之後。

**TwoOpt**（論文 Section 4.3.1，精確定義）：
把路線看成有向圖（弧 $u \to x$ 表示 $x$ 在 $u$ 之後）。
- **跨路線**：把 $u \to x$ 和 $v \to y$ 替換為 $u \to y$ 和 $v \to x$（重組兩條路線的首尾）
- **同一路線**（$u$ 在 $v$ 之前）：把 $u \to x$ 和 $v \to y$ 替換為 $u \to v$ 和 $x \to y$（反轉 $x$ 到 $v$ 這段）

#### 5.2.4 路線操作（Route Operators，2 種）

> **共同特性**：對路線對操作，不受鄰域限制，利用 caching 保持效率。

**RELOCATE\***（論文 Section 4.3.2）：
在兩條路線之間找並套用最佳的 (1,0)-exchange（即最佳的單客戶移動）。

**SWAP\***（論文 Section 4.3.2，Vidal 2022 原創，PyVRP 加強版）：
考慮兩條路線之間最佳的客戶互換，**但不要求互換的客戶插入對方原本的位置**，而是各自插入另一條路線中最佳的位置。
PyVRP 相對 Vidal (2022) 的加強：
1. 加入時間窗支援
2. 更多 caching 機會
3. 提早停止評估「已知不好的」移動

#### 5.2.5 空路線處理

節點操作也可以把客戶插入「空車輛的空路線」（unassigned vehicle）。
為了**不浪費車輛**（最小化使用車輛數），這類插入只在**所有客戶對之間的移動都已窮盡後才評估**。

---

### 5.3 族群管理（`Population.py` + `_pyvrp.so` 中的 `SubPopulation`）

**Python 部分**：族群邏輯（選親本、加入、清空）
**C++ 部分**：`SubPopulation`（高效存儲和 fitness 計算）

#### 5.3.1 雙子群結構

```
Population
├── SubPopulation（可行解子群）
└── SubPopulation（不可行解子群）
```

新解加入時，根據是否可行分別放入對應子群。

#### 5.3.2 Biased Fitness（偏置適應度）

每個解的 fitness 綜合考慮**品質**和**多樣性**：

```
biased_fitness(solution) = rank_quality × (1 - elite_ratio)
                         + rank_diversity × elite_ratio
```

- `rank_quality`：按 objective 值排名（越小越好）
- `rank_diversity`：按與其他解的平均距離排名（越大越好，越孤立越稀有）
- `elite_ratio = nb_elite / min_pop_size`

「精英解」（elite solutions）在存活者選擇中受到保護。

#### 5.3.3 存活者選擇

當子群超過 `min_pop_size + generation_size`（= 65）時觸發：
1. 先移除**完全重複**的解
2. 按 biased fitness 從最差開始淘汰
3. 縮回至 `min_pop_size`（= 25）

定期的淘汰**提升族群多樣性**（可從論文 Figure 1 的多樣性走勢圖中觀察到）。

#### 5.3.4 親本選擇（k-way Tournament，Kwon et al. 2022）

從族群中隨機抽 $k = 2$ 個解，選 biased fitness 較好的那個。
選兩次得到兩個親本，同時有多樣性限制：

```python
# 確保兩個親本的 BPD 多樣性在 [lb_diversity, ub_diversity] 之間
# 若不符合，最多重試 10 次
while not (lb_diversity <= bpd(first, second) <= ub_diversity) and tries <= 10:
    second = tournament_select()
```

---

### 5.4 懲罰管理（`PenaltyManager.py`）

**功能**：動態調整「違反容量」和「違反時間窗」的懲罰係數，讓可行解比例維持在目標值（43%）附近。

#### 5.4.1 目標函數（penalized objective）

```
penalized_cost = total_distance
               + capacity_penalty × total_excess_load
               + time_warp_penalty × total_time_warp
```

`time_warp`：到達客戶的時間超過 $l_i$ 的總超出量。

#### 5.4.2 懲罰更新邏輯

每收集 `num_registrations_between_penalty_updates` 筆記錄後更新：

```python
diff = target_feasible - feas_percentage  # 0.43 - 實際可行比例

if -0.05 < diff < 0.05:
    return penalty  # 在目標附近，不更新

if diff > 0:  # 可行解太少，加大懲罰
    return min(penalty_increase × penalty + 1, 1000)

else:  # 可行解太多，減少懲罰
    return max(penalty_decrease × penalty - 1, 1)
```

懲罰值被限制在 `[1, 1000]` 以避免數值溢位。

#### 5.4.3 修復 Booster

嘗試修復不可行解時，臨時使用更高懲罰（× `repair_booster` = 12 倍），讓局部搜尋更積極地修正約束違反。

---

### 5.5 SREX 交叉算子（`crossover/selective_route_exchange.py` + `_crossover.so`）

**SREX（Selective Route Exchange）**，由 Nagata & Kobayashi (2010) 提出。

**核心思想**：讓後代繼承父母各自「擅長的部分路線」，而非隨機混合。

**詳細步驟**（Python 包裝 + C++ 執行）：

```
1. 從親本 A 的路線中，隨機選一個起始路線索引 idx1
2. 從親本 B 的路線中，選對應索引 idx2（若 A 路線數 < B，idx2 = 0）
3. 決定要移動幾條路線：randint(min(A路線數, B路線數)) + 1
4. 把 B 選定的幾條路線「插入」後代（繼承 B 的這些路線）
5. 用 A 的路線補上後代中「尚未被服務的客戶」（greedy repair）
6. 輸出後代解
```

若親本之一有空解（num_clients=0），直接返回另一個親本。

---

### 5.6 多樣性指標 BPD（`diversity/_diversity.so`）

**BPD（Broken Pairs Distance，斷裂配對距離）**：量化兩個解有多不一樣。

**定義**：
```
對解 A，定義其「配對集合」PA = {(u, v) | v 緊接在 u 之後出現在某路線中}

BPD(A, B) = |PA △ PB| / (2n)
           = 在 A 中有、但 B 中沒有的配對數（含逆向）/ (2 × 客戶數)
```

直觀理解：兩個解共享越多「相鄰的客戶對」，距離越小；差異越大，距離越大，值域 $[0, 1]$。
使用者可以替換為自己實作的多樣性函數（只要符合相同介面）。

---

## 6. 程式碼架構

### 6.1 目錄結構

```
pyvrp/
│
├── Model.py              ← 使用者高層入口（建立問題 + 一鍵求解）
├── GeneticAlgorithm.py   ← HGS 主迴圈（Python）
├── Population.py         ← 族群管理邏輯（Python）
├── PenaltyManager.py     ← 動態懲罰管理（Python）
├── Statistics.py         ← 每次迭代統計收集（Python）
├── Result.py             ← 結果封裝（Python）
├── read.py               ← 讀取 VRPLIB/Solomon 格式（Python）
├── cli.py                ← 命令列介面（Python）
├── constants.py          ← 全域常數（MAX_VALUE 等）
│
├── _pyvrp.so             ← C++ 核心擴充
│   包含：ProblemData, Solution, Client, VehicleType,
│          CostEvaluator, RandomNumberGenerator,
│          PopulationParams, SubPopulation
│
├── search/
│   ├── LocalSearch.py    ← 局部搜尋流程（Python）
│   ├── SearchMethod.py   ← 搜尋方法介面定義（Python）
│   ├── neighbourhood.py  ← 稀疏鄰域計算（Python）
│   └── _search.so        ← C++ 操作符（Exchange系列, TwoOpt,
│                              MoveTwoClientsReversed, RELOCATE*, SWAP*）
│
├── crossover/
│   ├── selective_route_exchange.py  ← SREX Python 包裝
│   └── _crossover.so                ← C++ SREX 實作
│
├── diversity/
│   ├── __init__.py       ← BPD Python 介面
│   └── _diversity.so     ← C++ BPD 計算
│
├── stop/
│   ├── MaxRuntime.py          ← 時間限制停止條件
│   ├── MaxIterations.py       ← 迭代次數限制
│   ├── NoImprovement.py       ← 無改善停止
│   ├── TimedNoImprovement.py  ← 組合條件
│   └── StoppingCriterion.py   ← 停止條件介面定義
│
└── plotting/
    ├── plot_solution.py       ← 繪製最佳解路線圖
    ├── plot_result.py         ← 繪製完整結果（路線+統計）
    ├── plot_objectives.py     ← 繪製目標值收斂曲線
    ├── plot_diversity.py      ← 繪製多樣性走勢
    ├── plot_runtimes.py       ← 繪製迭代耗時
    ├── plot_coordinates.py    ← 繪製座標分布
    ├── plot_demands.py        ← 繪製需求量分布
    ├── plot_time_windows.py   ← 繪製時間窗分布
    ├── plot_route_schedule.py ← 繪製路線時間排程
    └── plot_instance.py       ← 繪製問題實例概覽
```

### 6.2 Python vs C++ 分工

| 模組 | 語言 | 理由 |
|------|------|------|
| GA 主迴圈 | Python | 邏輯複雜但呼叫頻率低，需要易於使用者替換 |
| 族群管理（Population） | Python（邏輯） + C++（SubPopulation） | 混合：邏輯在 Python，存取頻繁的資料在 C++ |
| 懲罰管理 | Python | 每 50/100 次才更新一次，不是瓶頸 |
| 局部搜尋操作符 | C++ | 每次迭代呼叫數萬次，是主要瓶頸（80–90% 時間） |
| Solution 資料結構 | C++ | 頻繁讀寫，需低記憶體開銷 |
| SREX 交叉算子核心 | C++ | 計算密集 |
| BPD 多樣性計算 | C++ | 需快速比較大量解對 |
| 鄰域計算（`compute_neighbours`） | Python + NumPy | 只在初始化時執行一次 |

---

## 7. 輸入參數速查表

> 這一節整合 `Model.py`、`_pyvrp.pyi`、`cli.py` 的參數定義，讓你一眼看清楚 PyVRP 需要哪些輸入。

### 7.1 倉庫參數 `add_depot()`

| 參數 | 型別 | 預設 | 說明 |
|------|------|------|------|
| `x` | int | 必填 | 倉庫 X 座標（平面座標） |
| `y` | int | 必填 | 倉庫 Y 座標（平面座標） |
| `tw_early` | int | 0 | 倉庫最早開放時間 |
| `tw_late` | int | 0 | 倉庫最晚關閉時間 |

> 目前只支援**單一倉庫**，傳入兩個以上會拋出 ValueError。

---

### 7.2 客戶（店面）參數 `add_client()`

| 參數 | 型別 | 預設 | 說明 |
|------|------|------|------|
| `x` | int | 必填 | 客戶 X 座標 |
| `y` | int | 必填 | 客戶 Y 座標 |
| `demand` | int | 0 | 需求量（貨物重量或件數） |
| `service_duration` | int | 0 | 在此店面的服務時間（卸貨等待） |
| `tw_early` | int | 0 | 時間窗開始：最早可開始服務的時間 |
| `tw_late` | int | 0 | 時間窗結束：最晚必須開始服務的時間 |
| `release_time` | int | 0 | 貨物最早可從倉庫出發的時間 |
| `prize` | int | 0 | 獎賞值（Prize-collecting VRP 用，不訪問可獲得懲罰） |
| `required` | bool | True | 是否一定要訪問此客戶（False 表示可選） |

> 車輛可以**提早抵達等待**（等到 `tw_early`），但不可**超過 `tw_late`** 才開始服務。

---

### 7.3 車輛參數 `add_vehicle_type()`

| 參數 | 型別 | 預設 | 說明 |
|------|------|------|------|
| `capacity` | int | 必填 | 每台車的最大載重上限 |
| `num_available` | int | 必填 | 此車型的可用數量（即最多幾台卡車） |

> 可多次呼叫 `add_vehicle_type()` 加入不同車型，組成**混合車隊**。

---

### 7.4 邊（路段）參數 `add_edge()`

| 參數 | 型別 | 預設 | 說明 |
|------|------|------|------|
| `frm` | Client/Depot | 必填 | 出發地點 |
| `to` | Client/Depot | 必填 | 目的地點 |
| `distance` | int | 必填 | 兩點間距離（整數，不可為負） |
| `duration` | int | 0 | 兩點間行駛時間（整數，可與距離不同單位） |

> 距離矩陣與時間矩陣**可以分開設定**，例如距離用公里、時間用分鐘。
> 未設定的邊預設為極大值，等同於禁止通行。

---

### 7.5 求解控制參數（CLI / `model.solve()`）

| 參數 | 型別 | 說明 |
|------|------|------|
| `--max_runtime` | float | 最多執行幾秒停止（與 `max_iterations` 二擇一） |
| `--max_iterations` | int | 最多跑幾次迭代停止（與 `max_runtime` 二擇一） |
| `--seed` | int | 隨機種子，設相同值可重現結果 |
| `--instance_format` | str | 輸入檔格式，預設 `vrplib`，也支援 `solomon` |
| `--round_func` | str | 非整數距離的四捨五入方式：`none`/`round`/`trunc`/`trunc1`/`dimacs` |
| `--config_loc` | str | TOML 格式的演算法超參數設定檔路徑（選填） |
| `--num_procs` | int | 平行求解時使用的處理器數量，預設 1 |
| `--stats_dir` | str | 輸出每次迭代統計 CSV 的目錄（選填） |
| `--sol_dir` | str | 輸出最佳解文字檔的目錄（選填） |

---

### 7.6 座標說明

PyVRP **不直接接受經緯度**，內部使用**整數平面座標**（效能考量）。

若有真實地理資料，建議轉換流程：
1. 將經緯度轉為 UTM 或 TWD97 平面座標（單位：公尺）
2. 依需要縮放（如除以 1000 換成公里）
3. 乘以適當倍數轉為整數（如乘以 10 保留一位小數精度）

距離矩陣同理，可用 Haversine 公式計算後轉整數輸入。

---

## 8. 完整 API 使用方式

### 8.1 Model 高層介面（最簡單，對應論文 Listing 1）

**適合**：直接想用 PyVRP 求解，不需要客製化演算法。

```python
import numpy as np
from pyvrp import Model
from pyvrp.stop import MaxRuntime

# ── 建立問題實例 ──────────────────────────────────────

m = Model()

# 新增車型：capacity（容量）必填，num_available（車輛數）必填
m.add_vehicle_type(capacity=15, num_available=4)

# 新增倉庫（只能有一個）
# x, y：座標（整數）
# tw_early, tw_late：倉庫時間窗（選填，預設 0/0）
depot = m.add_depot(x=456, y=320)

# 新增客戶（所有參數除 x, y 外均有預設值）
# x, y             : 座標（整數，必填）
# demand           : 需求量（預設 0）
# service_duration : 服務時間（預設 0）
# tw_early         : 時間窗最早（預設 0）
# tw_late          : 時間窗最晚（預設 0，= 無限制）
# release_time     : 最早可出發時間（預設 0）
# prize            : 訪問獎賞值（預設 0，= 非獎賞型）
# required         : 是否必須訪問（預設 True）
c1 = m.add_client(x=228, y=0, demand=3, service_duration=10,
                  tw_early=100, tw_late=200)
c2 = m.add_client(x=912, y=500, demand=5)

# 新增邊：distance（距離）必填，duration（時間）選填（預設 0）
# 若不設邊，預設距離 = MAX_VALUE（等同不可通行）
m.add_edge(depot, c1, distance=100, duration=100)
m.add_edge(depot, c2, distance=200, duration=200)
m.add_edge(c1, c2, distance=120, duration=120)
# 注意：需要設定所有你想讓車走的方向（有向圖）

# ── 求解 ──────────────────────────────────────────────

# stop：停止條件（必填）
# seed：隨機種子（選填，預設 0，影響可重複性）
result = m.solve(stop=MaxRuntime(5.0), seed=42)
print(result)
```

**`m.solve()` 內部自動完成**：
1. 建立 `ProblemData`
2. 建立 `RandomNumberGenerator`
3. 建立 `LocalSearch` + 加入所有預設操作符
4. 建立 `PenaltyManager`
5. 建立 `Population`
6. 生成初始隨機解
7. 建立 `GeneticAlgorithm` 並 `run(stop)`
8. 返回 `Result`

### 8.2 底層完整組裝方式（對應論文 Listing 2）

**適合**：想客製化各個組件（替換交叉算子、修改操作符等）。

```python
from pyvrp import (
    GeneticAlgorithm, GeneticAlgorithmParams,
    PenaltyManager, PenaltyParams,
    Population, PopulationParams,
    RandomNumberGenerator, Solution
)
from pyvrp.crossover import selective_route_exchange as srex
from pyvrp.diversity import broken_pairs_distance as bpd
from pyvrp.search import (
    NODE_OPERATORS, ROUTE_OPERATORS,
    LocalSearch, NeighbourhoodParams, compute_neighbours
)
from pyvrp.stop import MaxRuntime
from pyvrp.read import read

# 1. 讀取問題資料
data = read("RC2_10_5.txt", instance_format="solomon", round_func="dimacs")

# 2. 建立隨機數生成器
rng = RandomNumberGenerator(seed=42)

# 3. 建立局部搜尋
nb_params = NeighbourhoodParams(
    weight_wait_time=0.2,       # 等待時間的近度權重
    weight_time_warp=1.0,       # 時間窗違反的近度權重
    nb_granular=40,             # 每個客戶的鄰居數
    symmetric_proximity=True,   # 對稱化 proximity 矩陣
    symmetric_neighbours=False, # 是否對稱化鄰域結構
)
neighbours = compute_neighbours(data, nb_params)
ls = LocalSearch(data, rng, neighbours)

# 加入節點操作符（可以只加你需要的）
for op in NODE_OPERATORS:
    ls.add_node_operator(op(data))

# 加入路線操作符
for op in ROUTE_OPERATORS:
    ls.add_route_operator(op(data))

# 4. 建立懲罰管理器
pen_params = PenaltyParams(
    init_capacity_penalty=20,
    init_time_warp_penalty=6,
    repair_booster=12,
    num_registrations_between_penalty_updates=50,
    penalty_increase=1.34,
    penalty_decrease=0.32,
    target_feasible=0.43,
)
pen_manager = PenaltyManager(pen_params)

# 5. 建立族群
pop_params = PopulationParams(
    min_pop_size=25,
    generation_size=40,
    nb_elite=4,
    nb_close=5,
    lb_diversity=0.1,
    ub_diversity=0.5,
)
pop = Population(bpd, pop_params)  # bpd 可以替換為自己的多樣性函數

# 6. 生成初始解
init_pop = [Solution.make_random(data, rng) for _ in range(pop_params.min_pop_size)]

# 7. 建立並執行 GA
gen_params = GeneticAlgorithmParams(
    repair_probability=0.80,
    nb_iter_no_improvement=20_000,
)
algo = GeneticAlgorithm(data, pen_manager, rng, pop, ls, srex, init_pop, gen_params)
result = algo.run(stop=MaxRuntime(60))

# 8. 視覺化（需要 matplotlib）
from pyvrp.plotting import plot_result
plot_result(result, data)
```

### 8.3 從檔案讀取問題實例

```python
from pyvrp.read import read

# VRPLIB 格式（CVRP 標準格式，如 CVRPLIB 網站的 .vrp 檔）
data = read("instance.vrp",
            instance_format="vrplib",  # "vrplib" 或 "solomon"
            round_func="round")        # "round", "trunc", "trunc1"/"dimacs", "none"

# Solomon 格式（VRPTW 標準格式，如 C101.txt）
data = read("C101.txt", instance_format="solomon", round_func="trunc1")

# 從 ProblemData 重建 Model（可進一步修改再求解）
from pyvrp import Model
m = Model.from_data(data)
result = m.solve(stop=MaxRuntime(10))
```

### 8.4 命令列介面（CLI）

```bash
# 啟動虛擬環境
source .venv/bin/activate

# 基本使用（必填：instances路徑、--seed、--max_runtime 或 --max_iterations）
python -m pyvrp instance.vrp --seed 42 --max_runtime 10

# Solomon 格式 + DIMACS 精度
python -m pyvrp C101.txt --seed 42 --max_runtime 60 \
    --instance_format solomon --round_func dimacs

# 儲存結果（--stats_dir 存 CSV 統計；--sol_dir 存最佳解）
python -m pyvrp instance.vrp --seed 42 --max_runtime 10 \
    --stats_dir ./stats/ --sol_dir ./solutions/

# 使用 TOML 設定檔覆蓋超參數
python -m pyvrp instance.vrp --seed 42 --max_runtime 10 \
    --config_loc config.toml

# 批次求解多個實例（多核心）
python -m pyvrp data/*.vrp --seed 42 --max_runtime 60 --num_procs 4
```

**TOML 設定檔範例（`config.toml`）**：
```toml
[genetic]
repair_probability = 0.80
nb_iter_no_improvement = 20000

[penalty]
init_capacity_penalty = 20
init_time_warp_penalty = 6
repair_booster = 12
num_registrations_between_penalty_updates = 50
penalty_increase = 1.34
penalty_decrease = 0.32
target_feasible = 0.43

[population]
min_pop_size = 25
generation_size = 40
nb_elite = 4
nb_close = 5
lb_diversity = 0.1
ub_diversity = 0.5

[neighbourhood]
weight_wait_time = 0.2
weight_time_warp = 1.0
nb_granular = 40
symmetric_proximity = true
symmetric_neighbours = false

# 可選：自訂要使用的操作符（預設全開）
# [node_ops]  → 列出想要的，如 ["Exchange10", "TwoOpt"]
# [route_ops] → 列出想要的，如 ["SwapStar"]
```

### 8.5 停止條件

```python
from pyvrp.stop import MaxRuntime, MaxIterations, NoImprovement, TimedNoImprovement

# 最多跑 5 秒
stop = MaxRuntime(5.0)

# 最多跑 10,000 次迭代
stop = MaxIterations(10_000)

# 連續 5,000 次無改善就停
stop = NoImprovement(5_000)

# 組合：最多跑 60 秒，且最多無改善 5,000 次（先到先停）
stop = TimedNoImprovement(max_runtime=60, max_no_improvement=5_000)
```

### 8.6 讀取與視覺化結果

```python
result = m.solve(stop=MaxRuntime(5))

# ── 基本資訊 ──
print(result)                       # 完整摘要
print(result.cost())                # 最佳解總距離（不可行時回傳 inf）
print(result.is_feasible())         # 是否可行
print(result.num_iterations)        # 總迭代次數
print(result.runtime)               # 執行秒數

# ── 最佳解內容 ──
sol = result.best
print(sol.num_routes())             # 使用幾條路線（幾台車）
print(sol.num_clients())            # 服務了幾個客戶
print(sol.has_excess_load())        # 是否超載
print(sol.has_time_warp())          # 是否有時間窗違反

for route in sol.get_routes():
    print(route.visits())           # 該路線訪問的客戶 index 列表

# ── 統計數據 ──
stats = result.stats
# stats 包含每次迭代的：時間、可行/不可行子群大小、最佳/平均成本、多樣性、路線數

# ── 視覺化（需要 matplotlib）──
import matplotlib.pyplot as plt
from pyvrp.plotting import plot_result, plot_solution, plot_objectives, plot_diversity

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
plot_result(result, data)           # 完整四圖（多樣性+目標值+迭代耗時+路線）
plt.show()
```

**`print(result)` 輸出範例**：
```
Solution results
================
    # routes: 3
   # clients: 9
   objective: 1234.56
# iterations: 15234
    run-time: 5.00 seconds

Routes
------
Route #1: 1 4 7
Route #2: 2 5 8
Route #3: 3 6 9
```

---

## 9. 所有可調整的超參數

> 整合論文附錄 A（Table 3）+ 程式碼預設值 + CVRP/VRPTW 差異

### 8.1 `GeneticAlgorithmParams`

| 參數 | CVRP | VRPTW | 說明 |
|------|------|-------|------|
| `repair_probability` | 0.50 | **0.80** | 不可行後代嘗試修復的機率 |
| `nb_iter_no_improvement` | 20,000 | 20,000 | 連續無改善次數後重啟族群 |

### 8.2 `PopulationParams`

| 參數 | 值（CVRP = VRPTW） | 說明 |
|------|---------------------|------|
| `min_pop_size` | 25 | 最小族群大小（每代保留的解數） |
| `generation_size` | 40 | 每代可額外容納的解數（超過觸發淘汰） |
| `nb_elite` | 4 | 精英解數量（biased fitness 計算用） |
| `nb_close` | 5 | 計算多樣性排名時考慮最近幾個解 |
| `lb_diversity` | 0.1 | 選親本時多樣性下界（BPD ≥ 0.1） |
| `ub_diversity` | 0.5 | 選親本時多樣性上界（BPD ≤ 0.5） |

最大族群大小 = `min_pop_size + generation_size` = 65

### 8.3 `PenaltyParams`

| 參數 | CVRP | VRPTW | 說明 |
|------|------|-------|------|
| `init_capacity_penalty` | 20 | 20 | 超載懲罰初始值（每單位超量加幾分） |
| `init_time_warp_penalty` | — | **6** | 時間違反懲罰初始值 |
| `repair_booster` | 12 | 12 | 修復時懲罰暫時放大的倍數 |
| `num_registrations_between_penalty_updates` | **100** | **50** | 多少次記錄後更新懲罰 |
| `penalty_increase` | **1.25** | **1.34** | 可行解太少時懲罰增加倍率（≥ 1） |
| `penalty_decrease` | **0.85** | **0.32** | 可行解太多時懲罰減少倍率（∈ [0,1]） |
| `target_feasible` | 0.43 | 0.43 | 目標可行解比例（43%） |

**CVRP vs VRPTW 差異說明**：
- VRPTW 懲罰調整**更激進**（increase 1.34 vs 1.25；decrease 0.32 vs 0.85）
- VRPTW 更新**更頻繁**（每 50 次 vs 100 次），需要對快速變化的可行性更敏感

### 8.4 `NeighbourhoodParams`

| 參數 | CVRP | VRPTW | 說明 |
|------|------|-------|------|
| `nb_granular` | **20** | **40** | 每個客戶的鄰居數（鄰域大小） |
| `weight_wait_time` | — | 0.2 | 等待時間在近度計算的權重 |
| `weight_time_warp` | — | 1.0 | 時間窗衝突在近度計算的權重 |
| `symmetric_proximity` | True | True | 是否對稱化 proximity 矩陣 |
| `symmetric_neighbours` | **True** | **False** | 是否對稱化鄰域結構 |

**CVRP vs VRPTW 差異說明**：
- VRPTW 鄰域更大（40 vs 20）：時間窗使得空間近的客戶不一定時間兼容，需要更大的候選集合
- VRPTW 鄰域不對稱：時間窗的方向性使得 $i$ 到 $j$ 的訪問可行性不等於 $j$ 到 $i$

### 8.5 Model API 中的客戶/倉庫參數

**`add_client()` 完整參數**：

| 參數 | 型別 | 預設 | 說明 |
|------|------|------|------|
| `x` | int | 必填 | X 座標 |
| `y` | int | 必填 | Y 座標 |
| `demand` | int | 0 | 需求量（≥ 0） |
| `service_duration` | int | 0 | 服務時間（≥ 0） |
| `tw_early` | int | 0 | 時間窗最早（最早可以開始服務） |
| `tw_late` | int | 0 | 時間窗最晚（不可遲到） |
| `release_time` | int | 0 | 貨物最早可出發的時間 |
| `prize` | int | 0 | 訪問獎賞（非零時客戶變成非必訪） |
| `required` | bool | True | 是否必須被訪問（prize=0 時預設 True） |

**`add_depot()` 完整參數**：

| 參數 | 型別 | 預設 | 說明 |
|------|------|------|------|
| `x` | int | 必填 | X 座標 |
| `y` | int | 必填 | Y 座標 |
| `tw_early` | int | 0 | 倉庫可出發的最早時間 |
| `tw_late` | int | 0 | 所有路線必須在此時間前回到倉庫 |

**`add_edge()` 完整參數**：

| 參數 | 型別 | 預設 | 說明 |
|------|------|------|------|
| `frm` | Client/Depot | 必填 | 起點（必須是 `add_client`/`add_depot` 的返回值） |
| `to` | Client/Depot | 必填 | 終點 |
| `distance` | int | 必填 | 行駛距離（≥ 0） |
| `duration` | int | 0 | 行駛時間（≥ 0，不設則不考慮時間） |

**`add_vehicle_type()` 完整參數**：

| 參數 | 型別 | 預設 | 說明 |
|------|------|------|------|
| `capacity` | int | 必填 | 單台車的容量上限（≥ 0） |
| `num_available` | int | 必填 | 可使用的車輛數量（> 0） |

### 8.6 完整參數速查表

| 分類 | 參數 | CVRP 預設 | VRPTW 預設 |
|------|------|-----------|------------|
| **GA** | `repair_probability` | 0.50 | 0.80 |
| | `nb_iter_no_improvement` | 20,000 | 20,000 |
| **族群** | `min_pop_size` | 25 | 25 |
| | `generation_size` | 40 | 40 |
| | `nb_elite` | 4 | 4 |
| | `nb_close` | 5 | 5 |
| | `lb_diversity` | 0.1 | 0.1 |
| | `ub_diversity` | 0.5 | 0.5 |
| **懲罰** | `init_capacity_penalty` | 20 | 20 |
| | `init_time_warp_penalty` | — | 6 |
| | `repair_booster` | 12 | 12 |
| | `num_reg_between_updates` | 100 | 50 |
| | `penalty_increase` | 1.25 | 1.34 |
| | `penalty_decrease` | 0.85 | 0.32 |
| | `target_feasible` | 0.43 | 0.43 |
| **鄰域** | `nb_granular` | 20 | 40 |
| | `weight_wait_time` | 0 | 0.2 |
| | `weight_time_warp` | 0 | 1.0 |
| | `symmetric_proximity` | True | True |
| | `symmetric_neighbours` | True | False |
| **停止** | `MaxRuntime(t)` | 論文用 n×240/100 秒 | 論文用 2 小時 |

---

## 10. 效能表現

### 9.1 實驗設定（論文 Section 6）

**硬體**：AMD EPYC 7H12 CPU，PassMark 單核效能 2014 分
**方法**：每個實例 10 個不同隨機種子，報告平均結果
**比較基準**：以 PassMark 分數正規化時間限制（補償 CPU 速度差異）

**CVRP 時間限制**：
```
T_max = n × 240/100 秒
（100 客戶 → 4 分鐘；1000 客戶 → 40 分鐘）
```
**VRPTW 時間限制**：2 小時（1000 客戶實例，DIMACS 競賽慣例）

### 9.2 CVRP 結果（Table 1 & 4，Uchoa et al. 2017 X benchmark，100 個實例）

| 求解器 | 平均成本 | Mean Gap | Gap of Mean |
|--------|---------|----------|-------------|
| **PyVRP** | **63,275.5** | **0.22%** | **0.27%** |
| HGS-2012 | 63,285.8 | 0.21% | 0.28% |
| HGS-CVRP | 63,206.1 | 0.11% | 0.16% |
| BKS（最佳已知解） | 63,106.7 | 0.00% | 0.00% |

按實例規模分析（Table 4 摘要）：

| 規模 | PyVRP 平均 Gap | 觀察 |
|------|---------------|------|
| 小型（100–200 客戶） | ≈ 0.0–0.1% | 多數直接找到最優解 |
| 中型（200–500 客戶） | ≈ 0.1–0.3% | 偶爾比 HGS-CVRP 略差 |
| 大型（500–1001 客戶） | ≈ 0.3–0.9% | 差距隨規模增大，但仍具競爭力 |

結論（論文原文）：
> *"Despite the fact that PyVRP has not been specifically designed for the CVRP, these gaps are only slightly higher than the gaps of specialised CVRP solvers."*

### 9.3 VRPTW 結果（Table 2 & 5，Homberger & Gehring 1999，1000 客戶，60 個實例）

| 求解器 | 平均成本 | Mean Gap | Gap of Mean |
|--------|---------|----------|-------------|
| **PyVRP** | **33,296.4** | **0.40%** | **0.46%** |
| HGS-DIMACS | 33,265.5 | 0.32% | 0.37% |
| DIMACS 參考解 | 33,245.1 | 0.29% | 0.31% |
| BKS | 33,143.8 | 0.00% | 0.00% |

按問題類型分析（Table 5 摘要）：

| 類型 | 說明 | PyVRP 平均 Gap |
|------|------|---------------|
| C1 | 客戶分群，窄時間窗 | ≈ 0.0–0.05% |
| C2 | 客戶分群，寬時間窗 | ≈ 0.0–0.1% |
| R1 | 客戶隨機分布，窄時間窗 | ≈ 0.4–0.9% |
| R2 | 客戶隨機分布，寬時間窗 | ≈ 0.1–0.5% |
| RC1 | 混合型，窄時間窗 | ≈ 0.3–1.0% |
| RC2 | 混合型，寬時間窗 | ≈ 0.1–0.5% |

**與競賽版本的差距原因**（論文原文）：
> *"The difference in performance can be explained by the simplified implementation of PyVRP."*
PyVRP 移除了一些複雜組件（這些組件對競賽特定題組有用但難以維護），因此略差於競賽版本，但更簡潔、通用、可維護。

**延長運算的成果**：
> PyVRP 在延長運算下改善了 300 個 H&G 實例中的 **27 個 BKS（歷史最佳解）**。

---

## 11. 與其他求解器比較

（對應論文 Section 3，Related Projects）

| 求解器 | 語言 | 效能 | 易用性 | 可擴充 | 授權 | 特點 |
|--------|------|------|--------|--------|------|------|
| **PyVRP** | Python+C++ | ★★★★★ | ★★★★★ | ★★★★★ | MIT | 效能+易用+可擴充三者兼顧 |
| HGS-CVRP | 純 C++ | ★★★★★ | ★★☆☆☆ | ★★☆☆☆ | MIT | 純 CVRP 最快，但客製化需改 C++ |
| LKH-3 | C | ★★★★☆ | ★★☆☆☆ | ★☆☆☆☆ | 僅學術 | 把 VRP 轉成 TSP 求解；不可商用 |
| VROOM | C++ | ★★★☆☆ | ★★★☆☆ | ★★★☆☆ | 開源 | 整合真實地圖路由；效能不頂尖 |
| OR-Tools | C++/Python | ★★★☆☆ | ★★★★☆ | ★★★★☆ | Apache | Google 出品；constraint programming；效能差頂尖甚遠 |
| VRPSolver | C++/Julia/Python | ★★★★★（精確解） | ★★★☆☆ | ★★★☆☆ | 僅學術 | 精確解；只能處理數百客戶以內 |
| A VRP Solver | Rust | 不明 | ★★★☆☆ | ★★★☆☆ | Apache 2.0 | 多變型支援；缺乏標準 benchmark 數據 |

PyVRP 的獨特之處：**頂尖效能 + Python 易用性 + MIT 開放授權 + 完整測試/文件**，四者同時兼顧。

---

## 12. 如何延伸 PyVRP

（對應論文 Section 5.3，Extending PyVRP）

### 11.1 延伸流程

若要支援新的 VRP 變型（例如加入電動車充電限制），大致步驟：

1. **確定是硬限制還是軟限制**
   - 硬限制：可能需要修改 C++ 資料結構（`ProblemData`、`Solution`）
   - 軟限制：通常只需修改成本評估函數（`CostEvaluator`）

2. **新增資料屬性**：在 `Client` 或 `VehicleType` 加入新欄位（C++ 層）

3. **更新成本 delta 計算**：讓局部搜尋的每個操作符能正確計算「套用此移動後成本的變化量」

4. **加入 caching**（視需要）：時間相關的成本計算需要 caching（PyVRP 已有 `TimeWindowSegment` 作為範例）

5. **Python 層**：更新 `Model.add_client()` 等介面接受新參數

官方延伸指南：https://pyvrp.org/dev/new_vrp_variants.html

### 11.2 可在 Python 層客製化的部分

不需碰 C++，可直接在 Python 替換：

| 可替換的部分 | 替換方式 |
|------------|---------|
| 交叉算子 | 傳入自訂函數給 `GeneticAlgorithm` 的 `crossover_op` 參數 |
| 多樣性指標 | 傳入自訂函數給 `Population` 的 `diversity_op` 參數 |
| 鄰域結構 | 傳入自訂鄰域列表給 `LocalSearch` |
| 初始解生成方式 | 傳入自訂 `initial_solutions` 給 `GeneticAlgorithm` |
| 操作符選擇 | 只加入你需要的 `node_operator` 和 `route_operator` |
| 停止條件 | 實作 `StoppingCriterion` 介面 |
| 統計收集 | 繼承或替換 `Statistics` 類 |

---

## 13. 參考文獻

| 引用 | 完整資訊 | 在 PyVRP 中的角色 |
|------|---------|-----------------|
| **Vidal et al. 2013** | Vidal, T., Crainic, T.G., Gendreau, M., Prins, C. *A hybrid genetic algorithm with adaptive diversity management for a large class of vehicle routing problems with time-windows.* Computers & Operations Research, 40(1), 475–489. | **HGS 原始論文**，PyVRP 的演算法基礎；proximity 公式來源 |
| **Vidal 2022** | Vidal, T. *Hybrid genetic search for the CVRP: Open-source implementation and SWAP* improvement.* Computers & Operations Research, 140, 105643. | HGS-CVRP 開源實作；biased fitness、SWAP* 算子來源 |
| **Nagata & Kobayashi 2010** | Nagata, Y., Kobayashi, S. *A Memetic Algorithm for the Pickup and Delivery Problem with Time Windows Using Selective Route Exchange Crossover.* PPSN XI, 536–545. | **SREX 交叉算子**原始論文 |
| **Toth & Vigo 2003** | Toth, P., Vigo, D. *The granular tabu search and its application to the vehicle-routing problem.* INFORMS J. Comput., 15(4), 333–346. | **稀疏鄰域（Granular Neighbourhood）**概念來源 |
| **Toth & Vigo 2014** | Toth, P., Vigo, D. (Eds.). *Vehicle Routing: Problems, Methods, and Applications.* SIAM. | CVRP/VRPTW 標準定義教科書 |
| **Uchoa et al. 2017** | Uchoa, E., et al. *New benchmark instances for the capacitated vehicle routing problem.* European J. Oper. Res., 257(3), 845–858. | **X benchmark**（100 個 CVRP 測試實例） |
| **Homberger & Gehring 1999** | Homberger, J., Gehring, H. *Two evolutionary metaheuristics for the vehicle routing problem with time windows.* INFORMS J. Comput., 37(3), 297–318. | **H&G benchmark**（VRPTW 測試實例集，最大 1000 客戶） |
| **Kool et al. 2022** | Kool, W., et al. *Deep Policy Dynamic Programming for Vehicle Routing Problems.* CPAIOR. | HGS-DIMACS（2021 DIMACS 競賽第一名）；VRPTW 參數設定來源 |
| **Kwon et al. 2022** | Kwon, B., et al. *POMO: Policy Optimization with Multiple Optima for Reinforcement Learning.* NeurIPS. | 改進的 k-way tournament 選擇方法 |
| **Lan 2023** | Lan, L. *VRPLIB: A Python package for reading VRP instances.* | 讀取 VRPLIB/Solomon 格式的工具套件 |
| **Helsgaun 2017** | Helsgaun, K. *An extension of the Lin-Kernighan-Helsgaun TSP solver for constrained traveling salesman and vehicle routing problems.* | LKH-3；另一個常用 VRP 基準求解器（ML 研究常用） |
| **Perron & Furnon 2022** | Google LLC. *OR-Tools.* | Google 最佳化工具組 |
| **Pessoa et al. 2020** | Pessoa, A., et al. *A generic exact solver for vehicle routing and related problems.* Mathematical Programming, 183(1), 483–523. | VRPSolver；精確解求解器 |
| **Coupey et al. 2023** | Coupey, T., et al. *VROOM.* GitHub. | VROOM；開源 VRP 求解器，整合地圖路由 |
| **Van Doorn et al. 2022** | Van Doorn, J., et al. *EURO meets NeurIPS 2022 Vehicle Routing Competition.* | EURO meets NeurIPS 競賽；PyVRP 靜態組第一名 |

---

## 附錄：PyVRP 運作圖

```
使用者輸入
│  倉庫座標、客戶座標、需求量、時間窗
│  車輛數量、容量
│  停止條件
↓
Model.solve() / GeneticAlgorithm.run()
│
├── 初始化
│   ├── ProblemData（C++）：組裝距離/時間矩陣
│   ├── compute_neighbours：計算稀疏鄰域（O(kn)）
│   ├── LocalSearch（C++ 操作符）
│   ├── PenaltyManager（初始懲罰值）
│   ├── Population（空族群）
│   └── 生成 25 個隨機初始解 → 加入族群
│
└── 主迴圈
    ├── tournament_select()×2 → 兩個親本
    ├── srex(parents) → 後代解（C++）
    ├── ls.search(offspring) → 節點操作改善（C++，~80%時間）
    ├── ls.intensify(offspring) → 路線操作改善（C++）
    ├── [80%機率] 修復：懲罰×12 → 再次 ls.search()
    ├── pop.add(offspring) → 可能觸發淘汰
    ├── pm.register_*() → 更新懲罰值（每50次）
    └── [若無改善達20000次] → pop.clear() + 重新填充
│
└── 輸出 Result
    ├── best：最佳解（路線列表）
    ├── cost()：總距離
    ├── num_iterations：迭代次數
    ├── runtime：執行秒數
    └── stats：每次迭代的詳細統計
```

---

*文件整理時間：2026-04-06*
*整合來源：PyVRP 論文 PDF 全文（55,947 字元）正文 7 節 + 附錄 A/B/C + 所有 Python 原始碼模組*
*PyVRP 版本：v0.5.0*
