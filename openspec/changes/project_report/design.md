# Project Report — Design

> 接續 [proposal.md](./proposal.md)

---

## 進度快照（2026-06-01）

| 設計項目 | 狀態 | 備註 |
|---------|------|------|
| LaTeX 模板（IEEEtran）| ✅ 已套用 | `report/main.tex` 使用 `\documentclass[conference]{IEEEtran}` |
| 5 章節結構 | ✅ 已完成 | Intro / Related Work / Methods / Results / Conclusion 全部寫入 |
| 摘要（~130 字）| ✅ 已完成 | 4 句話結構：問題→方法→實作→結果 |
| 數學公式（4 條）| ✅ 已完成 | 目標函數、Biased Fitness、BPD、Penalty |
| Algorithm 1 虛擬碼 | ✅ 已完成 | `algorithm` + `algpseudocode` 環境 |
| Table I（CVRP benchmark）| ✅ 已完成 | 含 BKS / HGS-CVRP / HGS-2012 / PyVRP |
| Table II（VRPTW benchmark）| ✅ 已完成 | 含 BKS / HGS-DIMACS / PyVRP |
| Table III（HGS 參數表）| ✅ 已完成 | 新增於 Methods III-B，7 個關鍵參數 |
| Fig. 1（HGS 流程圖）| ✅ 已完成 | `hgs_algorithm_flowchart.pdf` |
| Fig. 2（Web 截圖）| ✅ 已完成 | `fig2_web_demo.png` |
| 引用 12 篇 | ✅ 已完成 | `references.bib` 含 12 筆 IEEE 格式 |
| Bio-inspired 連結 | ✅ 已完成 | 每章節均有 SREX/GA/diversity 類比說明 |

---

## 1. IEEE 格式規範

### 1.1 版面設定

| 項目 | 規格 |
|------|------|
| 欄數 | 雙欄（Two-column） |
| 行距 | 單倍（Single-spaced） |
| 紙張 | Letter（8.5×11 吋）或 A4 |
| 字型 | Times New Roman 10pt（正文） |
| 邊距 | 上下各 0.75"，左右各 0.625" |
| 標題字型 | 24pt（論文標題）/ 12pt（Section）/ 10pt（Subsection） |

### 1.2 LaTeX 模板使用

推薦使用 IEEE 官方模板：`IEEEtran.cls`

```latex
\documentclass[conference]{IEEEtran}
\usepackage{cite}
\usepackage{amsmath}
\usepackage{graphicx}
\usepackage{booktabs}

\begin{document}
\title{PyVRP-Web: Applying Hybrid Genetic Search to \\
Vehicle Routing with Interactive Visualization}
\author{...}
\maketitle
\begin{abstract}...\end{abstract}

\section{Introduction}
...
\section{Related Work}
...
\section{Methods}
...
\section{Results}
...
\section{Conclusion}
...
\bibliographystyle{IEEEtran}
\bibliography{references}
\end{document}
```

---

## 2. 章節結構與字數目標

| 章節 | IEEE 標準結構 | 目標字數 | 目標雙欄頁數 |
|------|-------------|---------|------------|
| Title + Abstract | 100–150 字摘要 | ~130 字 | 0.1 頁 |
| I. Introduction | 背景、問題、動機、貢獻 | 300–400 字 | ~0.5 頁 |
| II. Related Work | 先前工作、比較 | 300–400 字 | ~0.5 頁 |
| III. Methods | 演算法核心 + 系統架構 | 700–900 字 + 2 圖 | ~2 頁 |
| IV. Results | 實驗數據 + 系統展示 | 400–500 字 + 2 表/圖 | ~1.5 頁 |
| V. Conclusion | 總結 + 未來工作 | 150–200 字 | ~0.3 頁 |
| References | 8–12 篇引用 | — | ~0.3 頁 |
| **合計** | | **~2,000 字** | **≥ 5 頁** |

---

## 3. 圖表規劃

### 必要圖表（影響頁數，至少 2 圖 + 1 表）

| 編號 | 類型 | 內容 | 放置章節 | 狀態 |
|------|------|------|---------|------|
| Fig. 1 | 流程圖 | HGS 主迴圈（GA + LS 混合）| Methods | ✅ 已完成 |
| Fig. 2 | 截圖 | Web 系統求解結果地圖 | Results | ✅ 已完成 |
| Table I | 比較表 | CVRP benchmark（PyVRP vs HGS-CVRP vs BKS）| Results | ✅ 已寫入 main.tex |
| Table II | 比較表 | VRPTW benchmark | Results | ✅ 已寫入 main.tex |

### 建議加入（增加頁數）

| 編號 | 類型 | 內容 | 放置章節 | 狀態 |
|------|------|------|---------|------|
| Fig. 3 | 架構圖 | 四層系統架構 | Methods | ⬜ 選用，main.tex 有佔位符可取消註解 |
| Fig. 4 | 論文截圖 | 論文 Figure 1（diversity + objectives）| Results | ⬜ 選用 |
| Table III | 參數表 | HGS 關鍵參數（Table 3 節選）| Methods | ✅ 已寫入 main.tex |

---

## 4. 引用文獻規劃

> ✅ `references.bib` 已生成，共 **12 篇**，超過最低 8 篇要求。

| BibTeX key | 引用 | 引用位置 | 狀態 |
|------------|------|---------|------|
| `wouda2024pyvrp` | Wouda et al. 2024（PyVRP）| 全文核心 | ✅ |
| `vidal2013hybrid` | Vidal et al. 2013（HGS 原始）| Methods / Related Work | ✅ |
| `vidal2022hybrid` | Vidal 2022（HGS-CVRP）| Related Work + Methods | ✅ |
| `nagata2010memetic` | Nagata & Kobayashi 2010（SREX）| Methods | ✅ |
| `toth2003granular` | Toth & Vigo 2003（Granular）| Methods | ✅ |
| `uchoa2017new` | Uchoa et al. 2017（X benchmark）| Results | ✅ |
| `homberger1999two` | Homberger & Gehring 1999（H&G）| Results | ✅ |
| `kool2022hybrid` | Kool et al. 2022（HGS-DIMACS）| Related Work | ✅ |
| `ortools` | Perron & Furnon 2022（OR-Tools）| Related Work | ✅ |
| `toth2014vehicle` | Toth & Vigo 2014（VRP 教科書）| Introduction | ✅ |
| `helsgaun2017extension` | Helsgaun 2017（LKH-3）| Related Work | ✅ |
| `pessoa2020generic` | Pessoa et al. 2020（VRPSolver）| Related Work | ✅ |

---

## 5. 報告標題與摘要設計

### 標題（最終版）

```
PyVRP-Web: Bio-inspired Vehicle Routing Optimization
with Interactive Web Visualization
```

### 作者欄

```
Student ID: 414085193
Department of [Your Department]
[Your University], Taiwan
```

### Abstract 結構（4 句話）

1. 問題陳述（VRP is NP-hard）
2. 方法（HGS = GA + LS；bio-inspired）
3. 實作（web system）
4. 結果（benchmark + demo）
