# Project Report — Proposal

> **變更 ID**：`project_report`
> **課程**：Bio-inspired Computing（仿生計算）
> **截止日期**：2026-06-26 23:59（UTC+8）
> **提交格式**：TermProject_414085193.zip

---

## 1. 核心問題釐清

### 1.1 要交付什麼

| 項目 | 規格 | 備註 |
|------|------|------|
| 報告本體 | ≥ 4 頁（不含參考文獻頁）| IEEE 雙欄、單倍行距 |
| 必要章節 | Introduction / Related Work / Methods / Results / Conclusion | 缺一不可 |
| 源代碼 | 完整可執行原始碼 | `webapp/` 目錄 + `pyvrp/` |
| PDF | 報告的最終 PDF 版本 | 由 LaTeX 或 Word 產生 |
| 實驗數據 | Benchmark 結果或系統執行截圖 | |
| 復現說明文件 | 如何設定、編譯、執行的說明 | `README_reproduction.md` |
| 壓縮格式 | `TermProject_414085193.zip` | |

### 1.2 業務痛點與技術問題

本報告描述的核心工作：

1. **學術層（Algorithm）**：研讀並深入理解 PyVRP 論文（Wouda et al. 2024）提出的 HGS 演算法，包含遺傳算子、局部搜尋、族群管理與動態懲罰機制。
2. **工程層（System）**：將 HGS 求解器包裝成全端 Web 應用，解決「非工程師無法使用研究級工具」的痛點。

**仿生計算連結**（課程要求關鍵）：
- HGS = 遺傳演算法（模擬生物演化）+ 局部搜尋（精確改善）
- 遺傳演算法是最具代表性的仿生計算範疇
- 族群多樣性管理直接類比自然界的物種多樣性

### 1.3 影響範圍

**不涉及**：新演算法發明、修改 PyVRP 套件本體。

**涉及**：
- PyVRP HGS 演算法深度解析（論文全文理解）
- 全端系統實作（FastAPI + Leaflet.js + pyproj）
- 真實場景測試（台北 7-ELEVEN 配送案例）

---

## 2. 關鍵設計取捨

| 取捨點 | 選擇 | 理由 |
|--------|------|------|
| 報告語言 | **英文** | IEEE 格式慣例；評分者期待 |
| 演算法描述深度 | 數學公式 + 直觀說明並行 | 兼顧學術嚴謹性與可讀性 |
| 結果章節重心 | Benchmark 數據（論文結果）+ 系統 Demo 並重 | 單純 Demo 不夠有說服力 |
| 報告長度目標 | 5–6 頁（超過最低 4 頁）| 確保安全邊際，避免被扣分 |
| LaTeX vs Word | 建議 LaTeX（IEEE template）| 版面精準；自動處理雙欄 |

---

## 3. 交付物清單

```
TermProject_414085193.zip
├── report/
│   ├── TermProject_414085193.pdf          ← 最終 PDF
│   ├── main.tex                            ← LaTeX 源碼（若使用）
│   └── figures/                            ← 圖表
├── source/
│   ├── webapp/                             ← 系統源碼
│   ├── run_server.py
│   └── pyproject.toml
├── data/
│   ├── taipei_demo.json                    ← 範例輸入資料
│   └── taipei_711_night.json
└── README_reproduction.md                  ← 復現說明文件
```
