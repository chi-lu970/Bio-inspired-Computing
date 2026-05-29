# PyVRP: A High-Performance VRP Solver Package — 詳細摘要

> **論文資訊**
> - **標題**：PyVRP: a high-performance VRP solver package
> - **作者**：Niels A. Wouda（格羅寧根大學）、Leon Lan（阿姆斯特丹自由大學）、Wouter Kool（ORTEC）
> - **期刊**：INFORMS Journal on Computing（JOC-2023-03-SI-0055.R1）
> - **arXiv**：2403.13795v2 \[cs.NE] 21 Mar 2024
> - **軟體版本**：PyVRP v0.5.0
> - **授權**：MIT（開源）
> - **論文頁數**：24 頁（含附錄）

---

## 目錄

1. [論文摘要（Abstract）](#1-論文摘要)
2. [引言（Introduction）](#2-引言)
3. [問題定義（Problem Description）](#3-問題定義)
4. [相關研究（Related Projects）](#4-相關研究)
5. [技術實作（Technical Implementation）](#5-技術實作)
   - 5.1 HGS 演算法概覽
   - 5.2 遺傳演算法
   - 5.3 局部搜尋
   - 5.4 族群管理
6. [PyVRP 套件（The PyVRP Package）](#6-pyvrp-套件)
   - 6.1 套件結構
   - 6.2 使用範例
   - 6.3 延伸 PyVRP
7. [實驗結果（Experiments）](#7-實驗結果)
   - 7.1 CVRP 結果
   - 7.2 VRPTW 結果
8. [結論（Conclusion）](#8-結論)
9. [完整參數表（Table 3）](#9-完整參數表)
10. [關鍵圖表說明](#10-關鍵圖表說明)
11. [參考文獻](#11-參考文獻)

---

## 1. 論文摘要

PyVRP 是一個 Python 套件，以高效能方式實作 **混合遺傳搜尋（Hybrid Genetic Search, HGS）** 演算法，用於解決車輛路線問題（VRP）。

**核心定位**：
- 設計目標為 VRPTW（含時間窗的 VRP），但可輕鬆延伸支援其他 VRP 變型
- 將效能關鍵部分以 **C++ 實作**，其餘全部以 **Python 實作**，兼顧效能與彈性
- 是 2021 DIMACS VRPTW 挑戰賽第一名版本的精煉開源版本
- 亦在 EURO meets NeurIPS 2022 靜態 VRP 競賽奪得第一名

**關鍵字**：Vehicle Routing Problem, Time Windows, Hybrid Genetic Search, Open-Source, C++, Python

---

## 2. 引言

### 2.1 背景與動機

PyVRP 是 HGS 演算法（Vidal et al. 2013）的高效能 Python 實作，建立在 HGS-CVRP（Vidal 2022）開源版本的基礎上，並做了以下重大改進：

1. 新增時間窗支援（VRPTW）
2. 完整重新設計為高度可自定義的 Python 套件
3. 維持原本的速度與頂尖效能

### 2.2 設計哲學

> *"Only performance-critical parts of the algorithm are implemented in C++, whereas all other parts are implemented in Python."*

這與 HGS-CVRP（純 C++）的哲學截然不同：

| 特性 | HGS-CVRP | PyVRP |
|------|---------|-------|
| 語言架構 | 純 C++ | Python + C++ 混合 |
| 自定義方式 | 需修改 C++ 原始碼 | 直接用 Python 替換 |
| 安裝方式 | 需自行編譯 | `pip install pyvrp` |
| 彈性 | 低 | 極高 |
| 效能損失 | 無 | 可忽略不計 |

### 2.3 目標受眾

1. **實務應用者**：直接用於解決物流路線問題
2. **學術研究者**：作為起點或強力 baseline
3. **機器學習研究者**：作者明確希望 PyVRP 取代 LKH-3 成為 ML+VRP 研究的新基準

> *"We especially hope that PyVRP will help machine learning (ML) researchers interested in vehicle routing to easily build on the state-of-the-art, and move beyond LKH-3 as the most commonly used baseline."*

### 2.4 競賽成績

| 競賽 | 年份 | 成績 |
|------|------|------|
| 12th DIMACS Implementation Challenge（VRPTW track）| 2021 | **第一名** |
| EURO meets NeurIPS 2022 VRP Competition（靜態 VRPTW）| 2022 | **第一名** |

> 注意：實際用於競賽的版本比 PyVRP 更複雜；PyVRP 是簡化後的開源版本，移除了對效能貢獻有限的複雜組件，更簡潔、更健壯，但效能略低於競賽版本。

---

## 3. 問題定義

### 3.1 CVRP（Capacitated Vehicle Routing Problem，容量限制車輛路線問題）

**正式定義**：
- 客戶集合 $i = 1, \ldots, n$，各有需求量 $q_i \geq 0$
- 單一倉庫 $0$，所有車輛從倉庫出發並返回
- 邊距離 $d_{ij} \geq 0$（客戶或倉庫 $i$ 到 $j$ 的距離）
- 車輛容量 $Q > 0$
- **目標**：最小化所有路線的總行駛距離
- **限制**：每台車的客戶總需求量不超過 $Q$

### 3.2 VRPTW（VRP with Time Windows，含時間窗的車輛路線問題）

在 CVRP 基礎上增加：
- 每個客戶 $i$ 有服務時間 $s_i \geq 0$
- 最早抵達時間 $e_i \geq 0$ 和最晚抵達時間 $l_i \geq 0$（$e_i \leq l_i$），服務必須在此區間開始
- 車輛可早到等待，但不可超過 $l_i$ 才開始服務
- 從 $i$ 到 $j$ 的行駛時間 $t_{ij} \geq 0$
- PyVRP 支援距離矩陣和時間矩陣**分開設定**（實務中常見）

### 3.3 資料格式約定

- PyVRP 內部使用**整數距離和時間**（效能考量，整數比浮點數快）
- 可選編譯為雙精度浮點數，但預設不啟用
- 透過 VRPLIB 套件處理 Benchmark 資料的讀取與精度轉換
- 支援多種取整方式：`round`、`trunc`、`trunc1`/`dimacs`（×10 後截斷，保留一位小數）

---

## 4. 相關研究

論文詳細討論了六個相關開源 VRP 求解器，以下為逐一分析：

### 4.1 HGS-CVRP（Vidal 2022）

- **語言**：純 C++
- **效能**：頂尖（CVRP 專用，Mean Gap 0.11%）
- **問題**：
  - Python 介面（PyHygese）不含預編譯二進位，需要自行安裝編譯器工具鏈
  - 所有客製化都需要修改 C++ 原始碼
- **授權**：MIT

### 4.2 LKH-3（Helsgaun 2017）

- **方法**：將 VRP 轉換為對稱旅行商問題（TSP），套用 Lin-Kernighan-Helsgaun 局部搜尋
- **支援**：廣泛的 VRP 變型
- **問題**：
  - 客製化需要修改 C 語言原始碼
  - **僅限學術與非商業用途**
  - 不歡迎社群貢獻
- **現狀**：目前 ML+VRP 研究中最常用的 baseline

### 4.3 VROOM（Coupey et al. 2023）

- **全名**：Vehicle Routing Open-source Optimisation Machine
- **特點**：整合開源路由軟體，適合解決真實世界 VRP（含地圖路由）
- **問題**：
  - 無法與頂尖演算法競爭
  - 缺乏足夠的客製化文件

### 4.4 OR-Tools（Perron & Furnon 2022）

- **開發者**：Google
- **語言**：C++，提供 Python/Java/C# 介面
- **方法**：限制規劃（Constraint Programming）
- **優點**：廣泛文件、直接從 PyPI 安裝、支援多種問題變型
- **問題**：

> *"While this approach allows it to model and solve many problem variants, **its performance is far from the state of the art**."*

### 4.5 VRPSolver（Pessoa et al. 2020）

- **類型**：精確解求解器（Exact Solver）
- **語言**：C++，提供 Julia 和 Python 介面
- **優點**：可證明最優解
- **問題**：

> *"It does not scale to instances with more than a **few hundred customers**."*

- 最強組件的授權僅限學術用途

### 4.6 "A VRP Solver"（Builuk 2023）

- **語言**：Rust
- **授權**：Apache 2.0
- **問題**：缺乏標準 Benchmark 數據，難以評估效能

### 4.7 總結

> *"While each of these projects has their own merit, PyVRP has a unique combination of scope, performance, flexibility and ease-of-use, making it a useful addition to this set of projects."*

---

## 5. 技術實作

### 5.1 HGS 演算法概覽

HGS 是遺傳演算法（GA）與局部搜尋（LS）的混合：

```
初始化：隨機生成族群（不要求可行）
         ↓
主迴圈：
  1. 從族群選兩個親本
  2. 交叉（SREX）→ 產生後代
  3. 局部搜尋改善後代（soft constraints：懲罰違反）
  4. 若後代可行且優於最佳解 → 更新最佳解
  5. 後代加入族群
  6. 族群超過上限 → 存活者選擇（淘汰）
         ↓
輸出：Result（最佳解 + 詳細統計）
```

**關鍵設計**：局部搜尋將容量和時間窗視為**軟約束**（透過懲罰處理），讓搜尋探索更廣的解空間，並自動調整懲罰係數使一定比例的解保持可行。

### 5.2 遺傳演算法（`GeneticAlgorithm.py`）

**語言**：Python（邏輯協調）

每次迭代流程：
1. **親本選擇**：k-way tournament（預設 k=2，即二元競賽）
2. **交叉**：SREX（Selective Route Exchange）→ 產生後代
3. **局部搜尋**：改善後代
4. **更新最佳解**：若後代可行且更優
5. **加入族群**：觸發存活者選擇（若超過上限）

**GA 參數（CVRP / VRPTW）**：

| 參數 | CVRP | VRPTW |
|------|------|-------|
| `repair_probability` | 50% | 80% |
| `nb_iter_no_improvement`（重啟閾值）| 20,000 | 20,000 |

### 5.3 局部搜尋（`LocalSearch.py` + `_search.so`）

**語言**：C++（效能關鍵）

> *"Software profiling suggests that in PyVRP it accounts for **80-90% of the runtime**."*

#### 5.3.1 稀疏鄰域（Granular Neighbourhood）

- 來源：Toth & Vigo 2003
- 每個客戶只考慮 $k$ 個最近鄰居（預設 CVRP: 20，VRPTW: 40）
- 複雜度從 $O(n^2)$ 降至 $O(kn)$
- 鄰域結構可由使用者完全替換

**VRPTW proximity 公式**：
$$\text{prox}(i, j) = d_{ij} + 0.2 \cdot \max(e_j - t_{ij} - s_i - l_i, 0) + 1.0 \cdot \max(e_i + s_i + t_{ij} - l_j, 0) - \text{prize}(j)$$

（CVRP 不考慮時間項）

#### 5.3.2 節點操作符（Node Operators）

每個操作符評估客戶 $u$ 與其鄰域 $N(u)$ 中客戶 $v$ 之間的移動：

**(N, M)-exchange 系列**（以 C++ template 機制實作）：

| 操作符 | 說明 |
|--------|------|
| Exchange(1,0) | Relocate：將客戶 $u$ 插入 $v$ 之後（移動） |
| Exchange(2,0) | 將 $u$ 及其後繼客戶一起移動 |
| Exchange(3,0) | 將 $u$ 及其後兩個客戶一起移動 |
| Exchange(1,1) | Swap：$u$ 和 $v$ 互換位置 |
| Exchange(2,1) | 兩客戶序列和一個客戶互換 |
| Exchange(2,2) | 兩客戶序列互換 |
| Exchange(3,1) | 三客戶序列和一個客戶互換 |
| Exchange(3,2) | 三客戶序列和兩客戶序列互換 |
| Exchange(3,3) | 兩個三客戶序列互換 |

> *"We implement (N,M)-exchange using C++'s template mechanism, which after compilation results in efficient, specialised operator implementations for any N and M."*

**MoveTwoClientsReversed**：(2,0)-exchange 的變形，移動前先反轉順序。

**2-OPT**：
- 將路線表示為有向線圖，弧 $u \to x$ 表示 $x$ 緊跟在 $u$ 之後
- **跨路線**：把弧 $u \to x$ 和 $v \to y$ 替換為 $u \to y$ 和 $v \to x$（重組兩條路線的首尾）
- **同一路線**（$u$ 在 $v$ 之前）：把 $u \to x$ 和 $v \to y$ 替換為 $u \to v$ 和 $x \to y$（反轉 $x$ 到 $v$ 的段落）

#### 5.3.3 路線操作符（Route Operators）

對路線對操作，不受鄰域限制，利用 caching 保持效率：

**RELOCATE\***：
- 找到並套用兩條路線間最佳的 (1,0)-exchange
- 使用 N=1, M=0 的 (N,M)-exchange 操作符評估每個移動

**SWAP\***（來源：Vidal 2022；PyVRP 強化版）：
- 找到兩條路線間的最佳客戶互換
- **關鍵**：互換的客戶不要求插入對方原本的位置，而是各自插入另一條路線中**最佳的位置**
- **PyVRP 相對 Vidal 2022 的增強**：
  1. 加入時間窗支援
  2. 更多 caching 機會
  3. 針對「已知差的移動」提前停止評估

#### 5.3.4 空路線處理

- 節點操作也可以把客戶插入「空車輛的空路線」
- 為最小化使用車輛數，此類插入**只在所有客戶對之間的移動都已窮盡後才評估**

### 5.4 族群管理（`Population.py` + C++ `SubPopulation`）

**語言**：Python（邏輯）+ C++（資料存取）

#### 5.4.1 雙子群結構

```
Population
├── Feasible SubPopulation（可行解子群）
└── Infeasible SubPopulation（不可行解子群）
```

新解依是否可行放入對應子群。

#### 5.4.2 族群初始化

- 初始族群以**隨機方式**生成（不要求可行）
- 確保初始多樣性

#### 5.4.3 親本選擇（k-way Tournament，Kwon et al. 2022）

- 預設 k=2（二元競賽）
- 隨機抽 2 個解，選 **biased fitness** 較好的

**Biased Fitness（Vidal 2022）**：

$$\text{biased\_fitness}(s) = \text{rank\_quality}(s) \cdot (1 - \text{elite\_ratio}) + \text{rank\_diversity}(s) \cdot \text{elite\_ratio}$$

- `rank_quality`：按目標值排名（越小越好）
- `rank_diversity`：按與其他解的平均距離排名（越孤立越稀有越好）
- `elite_ratio = nb_elite / min_pop_size = 4 / 25 = 0.16`

#### 5.4.4 存活者選擇

當子群超過 `min_pop_size + generation_size`（預設 65）時觸發：
1. 先移除**完全重複**的解
2. 按 biased fitness 從最差開始淘汰
3. 縮回至 `min_pop_size`（25）

> 論文 Figure 1 直接驗證：*"It is clear from this figure that periodic survivor selection improves diversity."*

#### 5.4.5 多樣性指標 — BPD（Broken Pairs Distance）

**定義**：
$$\text{BPD}(A, B) = \frac{|P_A \triangle P_B|}{2n}$$

其中 $P_A = \{(u, v) \mid v \text{ 緊接在 } u \text{ 之後}\}$（含逆向配對），$\triangle$ 為對稱差集，$n$ 為客戶數。

- BPD = 0：兩個解完全相同
- BPD = 1：兩個解完全不同
- 使用者可以替換為自訂多樣性函數

---

## 6. PyVRP 套件

### 6.1 套件結構

```
pyvrp/                          ← 頂層命名空間
├── Model.py                    建模介面（高層入口）
├── GeneticAlgorithm.py         HGS 主迴圈（Python）
├── Population.py               族群邏輯（Python）
├── PenaltyManager.py           動態懲罰管理（Python）
├── Result.py                   結果封裝
├── Statistics.py               統計收集
├── read.py                     讀取 VRPLIB/Solomon 格式
├── _pyvrp.so                   C++ 核心（ProblemData, Solution...）
│
├── crossover/                  交叉算子
│   └── selective_route_exchange.py + _crossover.so
│
├── diversity/                  多樣性指標
│   └── broken_pairs_distance（Python 介面 + C++ 計算）
│
├── search/                     局部搜尋
│   ├── LocalSearch.py
│   ├── neighbourhood.py        compute_neighbours
│   └── _search.so              11 種節點操作符 + 2 種路線操作符
│
├── stop/                       停止條件
│   ├── MaxRuntime.py
│   ├── MaxIterations.py
│   ├── NoImprovement.py
│   └── TimedNoImprovement.py
│
└── plotting/                   視覺化
    ├── plot_result.py
    ├── plot_solution.py
    ├── plot_objectives.py
    ├── plot_diversity.py
    └── ...（共 10 個繪圖模組）
```

**安裝方式**：
```bash
pip install pyvrp
```
提供 Windows、macOS、Linux 預編譯二進位，無需自行編譯 C++ 擴充。

### 6.2 使用範例

#### 範例 1：模型介面（高層，適合實務應用者）

```python
import numpy as np
from pyvrp import Model
from pyvrp.stop import MaxRuntime

gen = np.random.default_rng(seed=42)
coords = gen.integers(0, 100, size=(10, 2))
demands = gen.integers(0, 10, size=(10,))

m = Model()
m.add_vehicle_type(capacity=15, num_available=4)
depot = m.add_depot(x=coords[0][0], y=coords[0][1])
clients = [
    m.add_client(x=coords[idx][0], y=coords[idx][1], demand=demands[idx])
    for idx in range(1, len(coords))
]
for frm in m.locations:
    for to in m.locations:
        distance = abs(frm.x - to.x) + abs(frm.y - to.y)  # Manhattan
        m.add_edge(frm, to, distance=distance)

res = m.solve(stop=MaxRuntime(1), seed=4)
print(res)
```

#### 範例 2：底層組裝（適合研究者自定義）

```python
from pyvrp import *
from pyvrp.crossover import selective_route_exchange as srex
from pyvrp.diversity import broken_pairs_distance as bpd
from pyvrp.search import *
from pyvrp.stop import MaxRuntime

data = read("RC2_10_5.txt", instance_format="solomon", round_func="dimacs")
rng = RandomNumberGenerator(seed=42)

ls = LocalSearch(data, rng, compute_neighbours(data))
for op in NODE_OPERATORS:
    ls.add_node_operator(op(data))
for op in ROUTE_OPERATORS:
    ls.add_route_operator(op(data))

pen_manager = PenaltyManager()
pop = Population(bpd)
init_pop = [Solution.make_random(data, rng) for _ in range(25)]
algo = GeneticAlgorithm(data, pen_manager, rng, pop, ls, srex, init_pop)
res = algo.run(stop=MaxRuntime(60))
```

### 6.3 延伸 PyVRP

支援新 VRP 變型的步驟：

1. **判斷硬限制 vs. 軟限制**
   - 硬限制：可能需要修改 C++ 資料結構（`ProblemData`、`Solution`）
   - 軟限制：通常只需修改成本評估函數（`CostEvaluator`）

2. **新增資料屬性**：在 `Client` 或 `VehicleType` 加入新欄位

3. **更新成本 delta 計算**：讓局部搜尋正確計算「套用移動後成本的變化量」

4. **加入 caching**：時間相關成本需要 caching（參考 `TimeWindowSegment`）

5. **Python 層介面**：更新 `Model.add_client()` 等接受新參數

> 完整延伸指南：https://pyvrp.org/dev/new_vrp_variants.html

---

## 7. 實驗結果

**實驗硬體**：AMD EPYC 7H12 CPU，PassMark 單核效能 2014

### 7.1 CVRP 實驗

**Benchmark**：Uchoa et al. 2017 的 X benchmark（100 個實例，100–1001 個客戶）

**慣例**：最小化總距離，歐式距離四捨五入至最近整數。

**時間限制**：$T_{max} = n \times 240/100$ 秒（依 PassMark 分數正規化）
- 100 客戶 → 4 分鐘
- 1001 客戶 → 40 分鐘

（基準 CPU：Intel Gold 6148，PassMark 2183；時間限制乘以 2183/2014 補償速度差異）

**每個實例跑 10 個不同隨機種子，報告平均值。**

#### 主要結果（Table 1）

| 求解器 | 平均成本 | Mean Gap | Gap of Mean |
|--------|---------|----------|-------------|
| **PyVRP** | **63,275.5** | **0.22%** | **0.27%** |
| HGS-2012（Vidal et al. 2013）| 63,285.8 | 0.21% | 0.28% |
| HGS-CVRP（Vidal 2022）| 63,206.1 | 0.11% | 0.16% |
| BKS（最佳已知解）| 63,106.7 | 0.00% | 0.00% |

> *"Despite the fact that PyVRP has not been specifically designed for the CVRP, these gaps are only slightly higher than the gaps of specialised CVRP solvers."*

#### 各規模表現（Table 4 節選）

| 規模 | 代表實例 | PyVRP Gap | BKS |
|------|---------|-----------|-----|
| 最小（101 客戶）| X-n101-k25 | **0.00%** | 27,591 |
| 小型（120 客戶）| X-n120-k6 | **0.00%** | 13,332 |
| 中型（400 客戶）| X-n393-k38 | 0.13% | 38,260 |
| 大型（701 客戶）| X-n701-k44 | 0.66% | 81,923 |
| 最大（1001 客戶）| X-n1001-k43 | 0.89% | 72,355 |

**觀察**：
- 小型實例（100–200 客戶）：多數達到 **精確最優**（Gap = 0%）
- 中型實例（200–500 客戶）：Gap 約 0.1–0.3%
- 大型實例（500–1001 客戶）：Gap 最高約 0.89%，但仍優於大多數啟發式算法

### 7.2 VRPTW 實驗

**Benchmark**：Homberger & Gehring 1999（H&G benchmark，僅展示 1000 客戶實例）

**實例類型**（60 個：6 類 × 10 個）：

| 類型 | 客戶分布 | 時間窗 |
|------|---------|--------|
| C1 | 群聚 | 窄 |
| C2 | 群聚 | 寬 |
| R1 | 隨機 | 窄 |
| R2 | 隨機 | 寬 |
| RC1 | 混合 | 窄 |
| RC2 | 混合 | 寬 |

**時間限制**：2 小時（依 PassMark 正規化：乘以 2000/2014）

**每個實例跑 10 個不同隨機種子，報告平均值。**

#### 主要結果（Table 2）

| 求解器 | 平均成本 | Mean Gap | Gap of Mean |
|--------|---------|----------|-------------|
| **PyVRP** | **33,296.4** | **0.40%** | **0.46%** |
| HGS-DIMACS（Kool et al. 2022）| 33,265.5 | 0.32% | 0.37% |
| DIMACS 參考解 | 33,245.1 | 0.29% | 0.31% |
| BKS | 33,143.8 | 0.00% | 0.00% |

> *"PyVRP would have ended up in second place in the DIMACS VRPTW competition."*

> *"The difference in performance can be explained by the simplified implementation of PyVRP."*

#### 各類型表現（Table 5 節選）

| 類型 | PyVRP 平均 Gap | 最佳實例 | 最差實例 |
|------|--------------|---------|---------|
| C1 | ~0.27% | C1_10_1: **0.00%** | C1_10_10: 0.80% |
| C2 | ~0.04% | C2_10_1: **0.00%** | C2_10_4: 0.16% |
| R1 | ~0.72% | R1_10_5: 0.33% | R1_10_4: 0.94% |
| R2 | ~0.37% | R2_10_1: 0.14% | R2_10_4: 0.64% |
| RC1 | ~0.72% | RC1_10_1: 0.50% | RC1_10_3: **0.99%** |
| RC2 | ~0.26% | RC2_10_2: 0.11% | RC2_10_4: 0.56% |

**特別成就**：
> *"During extended runs, PyVRP managed to improve **27 of the 300 best known solutions** of the complete Homberger and Gehring instances."*

---

## 8. 結論

> *"We introduce PyVRP, an open-source Python package for solving the vehicle routing problem with time windows, and show numerically that PyVRP achieves excellent performance on this problem variant."*

**三大貢獻總結**：

1. **套件框架**：Python + C++ 混合架構，兼顧彈性與效能
2. **演算法優化**：VRPTW 支援、SWAP* 增強（時間窗 caching + 提前停止）、簡化競賽版本
3. **開源生態**：MIT 授權，pip 直接安裝，完整文件與單元測試

**未來展望**：
- 歡迎社群貢獻擴充更多 VRP 變型
- 希望促進 ML+VRP 研究邁向更強基準

---

## 9. 完整參數表

**Table 3（論文附錄 A）**：

| 分類 | 參數 | CVRP | VRPTW |
|------|------|------|-------|
| **遺傳演算法** | repair_probability | 50% | **80%** |
| | nb_iter_no_improvement（重啟閾值）| 20,000 | 20,000 |
| **族群** | min_pop_size（最小族群大小）| 25 | 25 |
| | generation_size（每代額外容量）| 40 | 40 |
| | nb_elite（精英解數量）| 4 | 4 |
| | nb_close（多樣性排名考慮近解數）| 5 | 5 |
| | lb_diversity（親本選擇多樣性下界）| 0.1 | 0.1 |
| | ub_diversity（親本選擇多樣性上界）| 0.5 | 0.5 |
| **懲罰管理器** | init_capacity_penalty | 20 | 20 |
| | init_time_warp_penalty | — | **6** |
| | repair_booster（修復時懲罰放大倍率）| 12 | 12 |
| | num_registrations_between_penalty_updates | **100** | **50** |
| | penalty_increase（懲罰增加倍率）| **1.25** | **1.34** |
| | penalty_decrease（懲罰減少倍率）| **0.85** | **0.32** |
| | target_feasible（目標可行比例）| 0.43 | 0.43 |
| **局部搜尋** | nb_granular（鄰域大小）| **20** | **40** |
| | weight_wait_time | — | 0.2 |
| | weight_time_warp | — | 1.0 |
| | symmetric_proximity | True | True |
| | symmetric_neighbours | **True** | **False** |
| | (1,0)、(2,0)、(3,0)-exchange、MoveTwoClientsReversed | ✓ | ✓ |
| | (1,1)、(2,1)、(2,2)、(3,2)、(3,3)-exchange | ✓ | ✓ |
| | 2-OPT | ✓ | ✓ |
| | RELOCATE* | ✓ | ✓ |
| | SWAP* | ✓ | ✓ |

**CVRP vs VRPTW 差異重點**：
- VRPTW 修復機率更高（80% vs 50%）：時間窗使不可行解更難修復，需要更積極嘗試
- VRPTW 懲罰更新更頻繁（50 次 vs 100 次）：對可行性變化更敏感
- VRPTW 懲罰調整更激進（increase 1.34 vs 1.25；decrease 0.32 vs 0.85）
- VRPTW 鄰域更大（40 vs 20）：時間窗使空間近的客戶不一定時間相容
- VRPTW 鄰域不對稱：時間窗的方向性使得 $i$ 到 $j$ 的訪問可行性不等於 $j$ 到 $i$

---

## 10. 關鍵圖表說明

### Figure 1（論文 p.12）— 單次求解過程的詳細統計

對應求解 RC2_10_5 實例（Listing 2 範例），共四個子圖：

| 子圖 | 內容 | 關鍵觀察 |
|------|------|---------|
| 左上 | 可行 / 不可行子群的平均多樣性（Avg. diversity）| **鋸齒狀曲線**：每次存活者選擇後多樣性立即上升，直接證明族群管理有效防止早熟收斂 |
| 左中 | 兩個子群的最佳 / 平均目標值（Objectives）| 整體呈下降趨勢，GA+LS 有效收斂 |
| 左下 | 每次迭代耗時（秒，含趨勢線）| 迭代耗時穩定，C++ 局部搜尋效率高 |
| 右方 | 最佳觀察解的路線圖 | 視覺化最終配送路線 |

> 論文 Figure 1 caption：*"It is clear from this figure that **periodic survivor selection improves diversity**."*

### Table 4（論文 pp.18–20）— CVRP 完整結果

- 100 個 X-benchmark 實例逐一列出
- 每列：PyVRP 成本/Gap、HGS-2012 成本/Gap、HGS-CVRP 成本/Gap、BKS
- 最終彙總：PyVRP Mean 63,275.5（Gap 0.22%）、Gap of Mean 0.27%

### Table 5（論文 pp.21–22）— VRPTW 完整結果

- 60 個 H&G 1000 客戶實例逐一列出
- 每列：PyVRP 成本/Gap、HGS-DIMACS 成本/Gap、DIMACS 參考解 Gap、BKS
- 最終彙總：PyVRP Mean 33,296.4（Gap 0.40%）、Gap of Mean 0.46%

---

## 11. 參考文獻

| 引用 | 完整資訊 | 在 PyVRP 中的角色 |
|------|---------|-----------------|
| Accorsi et al. 2022 | Guidelines for computational testing of ML approaches to VRP. *Operations Research Letters* 50(2). | ML+VRP 研究使用 LKH-3 作 baseline 的依據 |
| Builuk 2023 | A new solver for rich VRP. Zenodo. | "A VRP Solver"（Rust，Apache 2.0） |
| Coupey et al. 2023 | VROOM v1.13. | VROOM 開源求解器 |
| Helsgaun 2017 | An Extension of LKH for Constrained TSP and VRP. Roskilde University. | LKH-3；ML 研究常用 baseline |
| Homberger & Gehring 1999 | Two Evolutionary Metaheuristics for VRPTW. *INFOR* 37(3). | **H&G benchmark**（VRPTW 1000 客戶標準測試集）|
| Kool et al. 2022 | Hybrid Genetic Search for VRPTW: A High-Performance Implementation. | **HGS-DIMACS**（DIMACS 2021 第一名）；VRPTW 參數設定來源 |
| Kwon 2022 | PyHygese. | HGS-CVRP 的 Python 介面（非官方） |
| Kwon et al. 2022 | Cost shaping via RL for VRP. EURO NeurIPS 2022. | 改進的 k-way tournament 親本選擇方法 |
| Lan 2023 | VRPLIB. | 讀取 VRPLIB/Solomon 格式的套件 |
| Nagata & Kobayashi 2010 | A memetic algorithm for pickup/delivery with SREX. *PPSN* XI, 536–545. | **SREX 交叉算子**原始論文 |
| Perron & Furnon 2022 | OR-Tools. Google. | Google 最佳化工具組 |
| Pessoa et al. 2020 | A generic exact solver for VRP. *Mathematical Programming* 183. | VRPSolver；精確解求解器 |
| Toth & Vigo 2003 | Granular Tabu Search for VRP. *INFORMS J. on Computing* 15(4). | **稀疏鄰域**概念來源 |
| Toth & Vigo 2014 | *Vehicle Routing: Problems, Methods, and Applications.* SIAM. | CVRP/VRPTW 標準教科書 |
| Uchoa et al. 2017 | New benchmark instances for CVRP. *European J. Oper. Res.* 257(3). | **X benchmark**（100 個 CVRP 測試實例）|
| Van Doorn et al. 2022 | Solving static and dynamic VRP with HGS and simulation. | EURO NeurIPS 2022 競賽；PyVRP 靜態組第一名 |
| Vidal 2022 | Hybrid genetic search for CVRP: Open-source implementation and SWAP*. *Computers & Operations Research* 140. | HGS-CVRP 開源實作；SWAP*、Biased Fitness 來源 |
| Vidal et al. 2013 | A hybrid genetic algorithm with adaptive diversity management for VRP with TW. *Computers & Operations Research* 40(1). | **HGS 原始論文**；PyVRP 的演算法基礎 |
| Wouda et al. 2023 | PyVRP: a high-performance VRP solver package. IJOC GitHub archive. | PyVRP v0.5.0 靜態存檔（可重現實驗） |

---

*摘要整理日期：2026-05-29*
*論文 arXiv：2403.13795v2 \[cs.NE] 21 Mar 2024*
*涵蓋：正文全 7 節 + Listing 1/2 + Appendix A（Table 3）+ Appendix B（Table 4，100 CVRP 實例）+ Appendix C（Table 5，60 VRPTW 實例）+ 完整參考文獻*
