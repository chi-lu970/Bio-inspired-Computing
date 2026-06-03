# Final Project Presentation — Proposal

> **變更 ID**：`final_project_presentation_prepare`
> **課程**：Bio-inspired Computing（仿生計算）
> **目標交付物**：期末報告展示幻燈片素材集

---

## 1. 背景與動機

### 1.1 課程要求

期末專案展示（Presentation）需以幻燈片形式，涵蓋以下五個章節：

| 章節 | 必須包含的內容 |
|------|--------------|
| Introduction | 問題定義、研究動機、貢獻概述 |
| Related Work | 既有方法與工具比較 |
| Methods | 核心演算法與系統實作 |
| Results | 實驗數據與系統展示 |
| Conclusion | 總結、貢獻、未來工作 |

主題**必須與仿生計算（Bio-inspired Computing）相關**。

### 1.2 本專案的仿生連結

本專案以 **PyVRP**（一套高效能車輛路線求解器）為核心，並自行開發全端視覺化系統。

PyVRP 的核心演算法是 **HGS（Hybrid Genetic Search，混合遺傳搜尋）**：

```
HGS = 遺傳演算法（Genetic Algorithm）+ 局部搜尋（Local Search）
         ↑ 仿生：模擬生物演化                ↑ 最佳化：精確改善
         廣泛探索（Exploration）              深度利用（Exploitation）
```

**遺傳演算法**模擬自然界的「物競天擇、適者生存」，是仿生計算最具代表性的範疇之一，完全符合課程主題要求。

### 1.3 核心問題釐清

**要解決的業務問題**：如何讓期末報告展示幻燈片材料齊備、重點清晰，使評審一眼看出：
1. 問題的重要性（VRP 是 NP-hard 的實際物流難題）
2. 仿生演算法的精妙（HGS 如何透過基因演化找到近最佳解）
3. 實作的完整性（Fullstack Web 系統將演算法視覺化）
4. 結果的說服力（Benchmark 數據 + 實際操作 Demo）

---

## 2. 影響範圍分析

### 2.1 不涉及程式碼變更

本變更**純為簡報素材整理**，不修改任何程式碼。涉及的資訊來源：

| 來源 | 內容 |
|------|------|
| 論文：PyVRP: A High-Performance VRP Solver Package (2024) | 演算法原理、數學定義、Benchmark 數據 |
| `openspec/changes/pyvrp-original-project-analysis/PyVRP-完整解析.md` | 論文完整解析（已整理） |
| `openspec/changes/pyvrp-fullstack-implementation/fullstack實作完整報告.md` | 系統實作詳解 |
| `webapp/` 目錄 | 系統截圖素材來源 |

### 2.2 目標受眾

簡報面向**課程評審教授與同學**：
- 具備演算法背景，但不一定熟悉 VRP
- 希望看到清楚的仿生計算應用場景
- 重視實作成果的展示（能看到系統運作）

---

## 3. 目標與範疇

### 3.1 交付目標

本 Spec 負責整理出可直接製作幻燈片的**完整材料包**，包含：

1. **每張投影片的標題、子標題、重點文字**（可直接複製貼上）
2. **每張投影片的圖表/圖示建議**（說明需要什麼視覺元素）
3. **演說稿要點**（presenter notes，協助口頭報告）
4. **關鍵數據與引用**（直接從論文提取，可信度高）

### 3.2 簡報規模建議

| 章節 | 建議投影片數 |
|------|------------|
| Title + Agenda | 2 |
| Introduction | 3–4 |
| Related Work | 2–3 |
| Methods | 5–7（演算法 4 + 系統 2）|
| Results | 3–4 |
| Conclusion | 2 |
| Q&A | 1 |
| **合計** | **18–23 張** |

報告時間通常 10–15 分鐘，每張投影片約 40–50 秒。

### 3.3 Out of Scope

- 不負責製作 .pptx/.key 檔案（僅提供素材）
- 不負責課程 Project Report（另有 `project_report` 規格）
- 不修改任何程式碼

---

## 4. 關鍵設計取捨

| 取捨點 | 選擇 | 理由 |
|--------|------|------|
| 演算法深度 vs. 可理解性 | 以類比說明為主，數學公式輔助 | 評審時間有限，視覺衝擊比數學推導重要 |
| 強調論文 vs. 強調自實作 | 兩者並重，先論文後實作 | 論文建立可信度，實作展示個人貢獻 |
| Benchmark 數字呈現 | 用圖表而非表格 | 視覺化更容易在口頭報告時帶過 |
| Demo 方式 | 截圖 + 動態 GIF 或現場 Live Demo | 現場 Demo 風險高，截圖為主、預備 Live Demo |
