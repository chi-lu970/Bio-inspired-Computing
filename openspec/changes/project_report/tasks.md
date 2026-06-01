# Project Report — Tasks

> 接續 [design.md](./design.md) / [specs/](./specs/)
> **截止日期**：2026-06-26 23:59（UTC+8）
> **提交格式**：`TermProject_414085193.zip`

---

## 進度快照（2026-06-01 更新）

| 階段 | 狀態 | 說明 |
|------|------|------|
| Phase 1：圖表資產 | ⬜ 待完成 | fig1（流程圖）、fig2（截圖）需手動製作 |
| Phase 2：LaTeX 檔 | ✅ 已完成 | `report/main.tex` + `report/references.bib` 已生成 |
| Phase 2：Overleaf 編譯 | ⬜ 待完成 | 需上傳圖片後編譯 PDF |
| Phase 3：內容審查 | ⬜ 待完成 | 編譯後核對 |
| Phase 4：目錄結構 | ✅ 已完成 | `TermProject_414085193/` 已建立、源碼已複製 |
| Phase 4：PDF 放入 + 打包 | ⬜ 待完成 | 編譯完 PDF 後執行 |

**剩餘必做步驟（依序）**：
1. [Task 1.1](#task-11hgs-主迴圈流程圖必要fig-1) — 畫 HGS 流程圖，存為 `report/figures/fig1_hgs_flowchart.png`
2. [Task 1.2](#task-12web-系統求解結果截圖必要fig-2) — 啟動伺服器截圖，存為 `report/figures/fig2_web_demo.png`
3. [Task 2.1](#task-21建立-overleaf-專案) — Overleaf 上傳圖片、編譯 PDF（≥ 5 頁）
4. [Task 4.3](#task-43複製報告檔案) — 將 PDF 複製為 `TermProject_414085193/report/TermProject_414085193.pdf`
5. [Task 4.4](#task-44打包-zip) — `Compress-Archive` 打包為 zip

---

## 概覽

```
Phase 1  資產準備（圖表截圖）     ← 必須先完成，LaTeX 才能插圖
Phase 2  LaTeX 編譯               ← 用 Overleaf 或本機 TeX
Phase 3  內容審查與修訂           ← 確保頁數 ≥ 5、格式正確
Phase 4  打包提交                 ← 生成 TermProject_414085193.zip
```

---

## Phase 1 — 資產準備

### Task 1.1｜HGS 主迴圈流程圖（必要，Fig. 1）

**目標**：繪製 HGS 演算法主迴圈，對應 report-draft.md 的 Algorithm 1。

**方法**（選一種）：
- **draw.io（推薦）**：至 app.diagrams.net，使用 Flowchart 模板
- **LaTeX TikZ**：直接在 main.tex 內用 tikzpicture 繪製
- **Mermaid + 截圖**：用 mermaid.live 生成再截圖

**流程圖內容**（按 Algorithm 1 pseudocode）：
```
開始 → 初始化族群(μ=25) → [迴圈開始]
  → 選親本 → SREX 交叉 → 局部搜尋(11+2 operators)
  → 評估 biased fitness → 更新族群（feasible/infeasible 各別）
  → 存活者選取（縮到 min_pop_size=25）
  → [每50代] 更新懲罰係數 α, β
  → 判斷停止條件（MaxRuntime / TimedNoImprovement）
  → 是 → 返回最佳可行解 → 結束
  → 否 → 回到迴圈開始
```

**輸出**：`figures/fig1_hgs_flowchart.pdf`（向量）或 `.png`（≥300 dpi）
**LaTeX 插入位置**：Methods 章節，緊接 Algorithm 1 之後

---

### Task 1.2｜Web 系統求解結果截圖（必要，Fig. 2）

**目標**：啟動 PyVRP-Web，載入台北範例，截圖求解結果地圖。

**步驟**：
```bash
# 啟動伺服器
uv run --python 3.11 python run_server.py

# 瀏覽器操作
# 1. 開啟 http://localhost:8000/
# 2. 點擊「載入範例 ▾」→ 選「台北日班」
# 3. 點擊「開始計算」
# 4. 等待 ~8-12 秒，結果出現後截圖
```

**截圖要求**：
- 包含地圖上的路線顯示（至少 3 條不同顏色路線）
- 包含右側結果面板（Routes: 3, Distance: ~92 km）
- 解析度 ≥ 1280×800；去除瀏覽器工具列

**輸出**：`figures/fig2_web_demo.png`（≥150 dpi 即可，螢幕截圖）
**LaTeX 插入位置**：Results 章節，Case Study 描述前

---

### Task 1.3｜四層系統架構圖（選用，Fig. 3）

**目標**：視覺化 PyVRP-Web 的四層架構，對應 report-draft.md 的 ASCII 圖。

**架構內容**：
```
Layer 1: Frontend      [HTML/CSS/JS + Leaflet.js]
           ↕ HTTP/JSON
Layer 2: API Gateway   [FastAPI + Pydantic schemas]
           ↕ Python call
Layer 3: Solver        [PyVRP HGS + pyproj UTM]
           ↕ Result dict
Layer 4: Serializer    [Timeline reconstruction + JSON]
```

**方法**：draw.io 矩形方塊圖，用箭頭連接各層，標示協議/格式。

**輸出**：`figures/fig3_architecture.pdf`
**LaTeX 插入位置**：Methods III-B 章節末尾

---

### Task 1.4｜論文 Figure 1 截圖（選用，Fig. 4）

**目標**：從 PyVRP 論文擷取 Figure 1（diversity + objectives 四格圖）。

**步驟**：
```
1. 開啟 openspec/changes/論文本體/PyVRP論文.pdf
2. 定位至 Figure 1（約第 6 頁）
3. 截取四格圖（p1 feasible/infeasible + p2 diversity sawtooth）
```

**輸出**：`figures/fig4_paper_figure1.png`（≥200 dpi）
**LaTeX 插入位置**：Methods III-A 末尾，說明族群行為

**注意**：引用時需標注 "Figure 1 from [1]"，避免著作權疑慮。

---

### Task 1.5｜HGS 參數表（選用，Table III）

**目標**：在 LaTeX 中新增 Table III，列出 HGS 關鍵參數。

**資料來源**：design.md §3 / PyVRP論文-詳細摘要.md §10（論文 Table 3）

| 參數 | 值 | 描述 |
|------|----|------|
| `min_pop_size` (μ) | 25 | 最小族群大小 |
| `generation_size` (λ) | 40 | 每代新增個體 |
| `nb_elite` | 4 | 菁英個體數 |
| `nb_granular` | 20/40 | 近鄰搜尋範圍 |
| `target_feasible` | 0.43 | 可行解目標比率 |
| Repair rate | ×12 | 懲罰修復倍率 |

**實作**：直接在 `main.tex` 內新增 `\begin{table}...\end{table}` 環境
**LaTeX 插入位置**：Methods III-A，biased fitness 段落之後

---

## Phase 2 — LaTeX 編譯

### Task 2.1｜建立 Overleaf 專案

> ✅ `report/main.tex` 與 `report/references.bib` 已生成，**不需要再從 latex-template.md 複製**。
> 本步驟只需：上傳檔案 + 放入圖片 + 編譯。

**Overleaf 上傳步驟**：
1. 登入 [overleaf.com](https://www.overleaf.com)
2. 點擊「New Project」→「Upload Project」
3. 將 `report/` 資料夾打包上傳（含 `main.tex`、`references.bib`、`figures/`）
   - 或手動建立 Blank Project，上傳各個檔案
4. Overleaf 已內建 `IEEEtran.cls`（選 IEEE Conference 模板即有），**不需額外上傳**
5. 點擊「Compile」，確認無錯誤
6. 確認頁數 ≥ 5（若不足，見 Task 2.4 補足方案）
7. 下載 PDF

**本機 LaTeX 方式**（MiKTeX / TeX Live）：
```powershell
cd C:\school\workSpace\Bio-inspired-Computing\report
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex   # 第三次確保交叉引用正確
# 開啟 PDF
start main.pdf
```

---

### Task 2.2｜複製 report-draft.md 內容至 LaTeX ✅

> **已完成**：`report/main.tex` 已包含全部章節（Introduction / Related Work / Methods / Results / Conclusion），並在原稿基礎上加入 Table III（參數表）與更詳細的 bio-inspired 連結描述。**此步驟可跳過。**

**步驟**（供參考，若需手動核對）：將 `specs/report-draft.md` 中各章節文字轉換為 LaTeX 語法。

**轉換對照表**：

| Markdown | LaTeX |
|----------|-------|
| `## I. Introduction` | `\section{Introduction}` |
| `### A. 子節` | `\subsection{Sub-section}` |
| `**粗體**` | `\textbf{text}` 或 `\emph{text}` |
| `$公式$` | `$formula$`（inline）/ `\begin{equation}...\end{equation}` |
| `[1]` 引用 | `\cite{wouda2024pyvrp}` |
| Table | `\begin{table}...\end{table}`（已在 latex-template.md） |
| Algorithm 1 | `\begin{algorithm}...\end{algorithm}`（已在 latex-template.md） |

**方程式確認清單**（確保 LaTeX 語法正確）：
- [ ] 目標函數 $\min \sum_{k} \sum_{(i,j)} c_{ij} x_{ijk}$
- [ ] Biased Fitness $f_\text{biased}(s) = r_\text{q}(s)(1-\rho) + r_\text{d}(s)\rho$
- [ ] BPD $\text{BPD}(A,B) = |\mathcal{P}_A \triangle \mathcal{P}_B| / 2n$
- [ ] Penalty $f_\text{pen} = d + \alpha \Delta_\text{cap} + \beta \Delta_\text{tw}$

---

### Task 2.3｜插入圖表

**圖表插入 checklist**：

- [ ] **Fig. 1**（HGS flowchart）— 在 Methods III-A 末
  ```latex
  \begin{figure}[t]
    \centering
    \includegraphics[width=\columnwidth]{figures/fig1_hgs_flowchart}
    \caption{Main loop of Hybrid Genetic Search (HGS). ...}
    \label{fig:hgs}
  \end{figure}
  ```
- [ ] **Fig. 2**（Web demo）— 在 Results IV-B
  ```latex
  \begin{figure}[t]
    \centering
    \includegraphics[width=\columnwidth]{figures/fig2_web_demo}
    \caption{PyVRP-Web interface showing optimized routes ...}
    \label{fig:webdemo}
  \end{figure}
  ```
- [ ] **Table I**（CVRP benchmark）— 已在 latex-template.md
- [ ] **Table II**（VRPTW benchmark）— 已在 latex-template.md

**選用圖表**：
- [ ] Fig. 3（架構圖） — Methods III-B 末
- [ ] Fig. 4（論文 Figure 1）— Methods III-A 族群行為說明處
- [ ] Table III（參數表）— Methods III-A biased fitness 之後

---

### Task 2.4｜編譯與頁數檢查

**頁數目標**：≥ 5 頁（不含參考文獻頁算入 5 頁即可）

**頁數不足時的補足方案**（按優先順序）：
1. 加入 Fig. 3（架構圖）— 約 +0.4 頁
2. 加入 Table III（參數表）— 約 +0.3 頁
3. 加入 Fig. 4（論文 Figure 1）— 約 +0.4 頁
4. 擴展 Results IV-B，加入更多 Taipei case study 細節（逐路線描述）
5. 擴展 Methods III-B，加入更多 API endpoint 說明

**編譯指令（本機）**：
```bash
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
open main.pdf   # macOS
start main.pdf  # Windows
```

---

## Phase 3 — 內容審查與修訂

### Task 3.1｜格式合規性檢查

| 項目 | 標準 | 檢查方式 |
|------|------|---------|
| 頁數 | ≥ 4 頁正文（目標 5-6） | PDF 頁碼 |
| 欄數 | 雙欄 | 目視確認 |
| 字型 | Times New Roman 10pt | IEEEtran.cls 自動處理 |
| 摘要 | 100–150 字 | 字數統計 |
| 引用格式 | 方括號 [1]–[10] | 目視確認 |
| 圖標題 | "Fig. X." 格式 | 目視確認 |
| 表標題 | "TABLE X" 全大寫 | IEEEtran 自動處理 |

---

### Task 3.2｜內容完整性核對

**章節 checklist**：

- [ ] **Abstract**：4 句話結構（問題→方法→實作→結果）；~130 字
- [ ] **I. Introduction**：VRP 定義、NP-hard 動機、bio-inspired 連結、2 條貢獻列表
- [ ] **II. Related Work**：
  - [ ] A. VRP Solver Landscape（LKH-3, OR-Tools, VROOM, VRPSolver）
  - [ ] B. HGS 演化脈絡（Vidal 2013 → Vidal 2022 → PyVRP 2024）
- [ ] **III. Methods**：
  - [ ] A. HGS 核心（CVRP/VRPTW 數學公式、Algorithm 1、SREX、LS、族群管理、懲罰機制）
  - [ ] B. PyVRP-Web 系統（四層架構、3 個工程決策）
- [ ] **IV. Results**：
  - [ ] A. Benchmark（Table I + Table II）
  - [ ] B. Case Study（Taipei 16 stores, 3 routes, ~92 km, ~8 sec）
- [ ] **V. Conclusion**：總結 + 4 條未來工作方向
- [ ] **References**：至少 8 篇，按 IEEE 格式

---

### Task 3.3｜數據正確性核對

參照 `openspec/changes/論文本體/PyVRP論文-詳細摘要.md` 確認：

| 數據點 | 正確值 | 所在章節 |
|--------|--------|---------|
| CVRP Mean Gap | 0.22% | Table I / Results |
| VRPTW Mean Gap | 0.40% | Table II / Results |
| BKS 改進數 | 27 instances | Results |
| CVRP instances | 100 (X benchmark) | Table I |
| VRPTW instances | 60 (Homberger) | Table II |
| PyVRP version | 0.5.0 | Methods / Intro |
| nb_granular (CVRP) | 20 | Methods |
| nb_granular (VRPTW) | 40 | Methods |
| target_feasible | 43% | Methods |
| Taipei stores | 16 | Results |
| Taipei routes | 3 | Results |
| Taipei distance | ~92 km | Results |
| Taipei solve time | ~8 sec | Results |

---

### Task 3.4｜仿生計算連結核對（課程要求）

論文必須明確展示 HGS 與仿生計算的連結。確認以下描述存在於報告中：

- [ ] Introduction 明確使用 "bio-inspired" / "Genetic Algorithm" 詞彙
- [ ] Methods 說明 SREX = 交叉算子（crossover）類比生物基因重組
- [ ] Methods 說明族群多樣性管理（BPD）類比物種多樣性
- [ ] Methods 說明動態懲罰機制類比環境壓力調節
- [ ] Conclusion 回顧 HGS 的 bio-inspired 本質

---

## Phase 4 — 打包提交

### Task 4.1｜建立提交目錄結構 ✅

> **已完成**：`TermProject_414085193/` 目錄已建立，結構如下（`__pycache__` 已清除）。

```
TermProject_414085193/
├── report/
│   ├── TermProject_414085193.pdf    ← 最終 PDF（Phase 2 產出）
│   ├── main.tex                      ← LaTeX 源碼
│   ├── references.bib
│   └── figures/
│       ├── fig1_hgs_flowchart.png   （Task 1.1）
│       ├── fig2_web_demo.png        （Task 1.2）
│       ├── fig3_architecture.png    （Task 1.3，選用）
│       └── fig4_paper_figure1.png   （Task 1.4，選用）
│
├── source/
│   ├── run_server.py
│   ├── pyproject.toml
│   └── webapp/
│       ├── backend/
│       │   ├── main.py
│       │   ├── api/
│       │   │   ├── routes.py
│       │   │   └── schemas.py
│       │   ├── services/
│       │   │   ├── coord.py
│       │   │   ├── solver.py
│       │   │   ├── serializer.py
│       │   │   └── exceptions.py
│       │   └── examples/
│       │       ├── taipei_demo.json
│       │       └── taipei_711_night.json
│       └── frontend/
│           ├── index.html
│           ├── css/style.css
│           └── js/
│               ├── api.js
│               ├── map.js
│               └── form.js
│
└── README_reproduction.md            ← specs/README_reproduction.md
```

---

### Task 4.2｜複製源碼並確認可執行 ✅

> **已完成**：`source/webapp/`、`source/run_server.py`、`source/pyproject.toml`、`README_reproduction.md` 均已複製至提交目錄。
> 仍建議執行下方驗證指令確認源碼正常運行。

```powershell
# 建立提交目錄
New-Item -ItemType Directory -Force "TermProject_414085193\report\figures"
New-Item -ItemType Directory -Force "TermProject_414085193\source"

# 複製 webapp 源碼（從專案根目錄）
Copy-Item -Recurse "webapp" "TermProject_414085193\source\webapp"
Copy-Item "run_server.py" "TermProject_414085193\source\"
Copy-Item "pyproject.toml" "TermProject_414085193\source\"

# 複製 README
Copy-Item "openspec\changes\project_report\specs\README_reproduction.md" `
          "TermProject_414085193\README_reproduction.md"

# 驗證源碼可執行
cd TermProject_414085193\source
uv run --python 3.11 python run_server.py
# 開瀏覽器確認 http://localhost:8000/ 正常
```

---

### Task 4.3｜複製報告檔案

> `main.tex` 和 `references.bib` 已在 `TermProject_414085193\report\` 中。
> 只需補上圖片（fig1、fig2）和 Overleaf 編譯完成的 PDF。

```powershell
# 複製 PDF（Overleaf 下載後）
Copy-Item "report\main.pdf" "TermProject_414085193\report\TermProject_414085193.pdf"

# 複製圖表（確保圖片也同步進去）
Copy-Item "report\figures\*" "TermProject_414085193\report\figures\" -Force
```

---

### Task 4.4｜打包 Zip

```powershell
# Windows（PowerShell 5+）
Compress-Archive -Path "TermProject_414085193" `
                 -DestinationPath "TermProject_414085193.zip" `
                 -Force

# 確認壓縮包結構
Expand-Archive "TermProject_414085193.zip" -DestinationPath "verify_zip" -Force
Get-ChildItem -Recurse "verify_zip" | Select-Object FullName
```

---

### Task 4.5｜提交前最終核查

**最終 checklist**：

- [ ] **PDF 存在**：`report/TermProject_414085193.pdf`
- [ ] **頁數 ≥ 4**（目標 5–6 頁）
- [ ] **5 章節完整**：Introduction / Related Work / Methods / Results / Conclusion
- [ ] **引用 ≥ 8 篇**
- [ ] **圖 ≥ 2 張**（Fig. 1 + Fig. 2 為最低要求）
- [ ] **表 ≥ 1 張**（Table I）
- [ ] **源碼可執行**：`uv run --python 3.11 python run_server.py` 不報錯
- [ ] **README_reproduction.md 存在**
- [ ] **zip 名稱正確**：`TermProject_414085193.zip`（學號無誤）
- [ ] **zip 內無多餘大型檔案**（.venv、__pycache__、.git 等）

**排除不需要的檔案**：
```powershell
# 清理 __pycache__
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

# 確認沒有 .venv 在 zip 內（安裝說明已在 README）
```

---

## 快速執行順序參考（2026-06-01 更新後）

```
✅ 已完成（不需再做）
  ├── main.tex / references.bib 已生成 → report/
  ├── TermProject_414085193/ 目錄結構已建立
  └── 源碼（webapp、run_server.py）已複製進去

⬜ 剩餘工作（約 1.5–2 小時）

Step 1（30 分鐘）｜製作 Fig. 1 — HGS 流程圖
  → 至 app.diagrams.net，按 Task 1.1 內容繪製
  → 存為 report\figures\fig1_hgs_flowchart.png（≥300 dpi）

Step 2（10 分鐘）｜製作 Fig. 2 — Web 截圖
  → uv run --python 3.11 python run_server.py
  → 開啟 http://localhost:8000/，載入「台北日班」，點求解後截圖
  → 存為 report\figures\fig2_web_demo.png

Step 3（20 分鐘）｜Overleaf 編譯 PDF
  → 登入 overleaf.com → New Project → Upload Project
  → 上傳 report\ 整個資料夾（含 main.tex、references.bib、figures\）
  → Compile，確認頁數 ≥ 5
  → 下載 PDF，存為 report\main.pdf

Step 4（5 分鐘）｜放入 PDF 並打包
  → Copy-Item "report\main.pdf" "TermProject_414085193\report\TermProject_414085193.pdf"
  → Copy-Item "report\figures\*" "TermProject_414085193\report\figures\" -Force
  → Compress-Archive -Path "TermProject_414085193" -DestinationPath "TermProject_414085193.zip" -Force

Step 5（10 分鐘）｜Task 4.5 最終核查
  → 對照 checklist 確認 PDF 頁數、章節、引用數、圖數、zip 名稱
```

---

## 相關規格文件

| 文件 | 用途 |
|------|------|
| [proposal.md](./proposal.md) | 交付物清單、zip 結構 |
| [design.md](./design.md) | IEEE 格式規範、章節字數目標 |
| [specs/report-draft.md](./specs/report-draft.md) | **完整英文報告草稿（直接複製）** |
| [specs/latex-template.md](./specs/latex-template.md) | **完整 main.tex + references.bib** |
| [specs/README_reproduction.md](./specs/README_reproduction.md) | 復現說明文件（直接使用） |
