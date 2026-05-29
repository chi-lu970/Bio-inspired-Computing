# Final Project Presentation — Tasks

> **狀態**：待實作確認
> **預計完成**：期末報告截止前（2026-06-26）
> **執行者**：Student 414085193
> 
> ⚠️ 本文件整理所有幻燈片製作任務，請確認後開始製作。

---

## 第一階段：截圖素材收集（優先完成）

在製作投影片前，需要先從系統取得截圖素材。

### Task 1.1 — 啟動 Web 系統並截圖

**步驟**：
```bash
uv run --python 3.11 python run_server.py
# 打開 http://localhost:8000
```

**需要截圖的畫面**：

| 截圖編號 | 說明 | 用於哪張投影片 |
|---------|------|--------------|
| `screenshot_01_empty.png` | 空白初始表單 | Slide 19 左上 |
| `screenshot_02_preview.png` | 載入台北日班範例後的地圖預覽 | Slide 19 右上 |
| `screenshot_03_solving.png` | 求解中的 loading overlay | （選用）|
| `screenshot_04_result_map.png` | 求解完成的多色路線地圖（全頁）| Slide 19 左下 + Slide 20 |
| `screenshot_05_result_panel.png` | 右側路線詳細面板 | Slide 19 右下 |
| `screenshot_06_popup.png` | 點擊某個店面後的 Popup 資訊 | （選用，補充說明）|

**截圖建議**：
- 解析度：至少 1920×1080
- 格式：PNG
- 瀏覽器：Chrome（Ctrl+Shift+I → Device toolbar 設定固定解析度）

---

### Task 1.2 — 圖表製作素材整理

需要製作的圖表，以及對應的數據來源：

**圖表 1：CVRP Benchmark 橫條圖**（Slide 17）
```
數據來源：論文 Table 1
  PyVRP:     Mean Gap = 0.22%
  HGS-CVRP:  Mean Gap = 0.11%
  HGS-2012:  Mean Gap = 0.21%
  BKS:       Mean Gap = 0.00%
製作建議：PowerPoint / Google Slides 橫條圖，藍色系
```

**圖表 2：VRPTW Benchmark 橫條圖**（Slide 18）
```
數據來源：論文 Table 2
  PyVRP:        Mean Gap = 0.40%
  HGS-DIMACS:   Mean Gap = 0.32%
  DIMACS ref:   Mean Gap = 0.29%
  BKS:          Mean Gap = 0.00%
製作建議：同上，橙色系以區別
```

**圖表 3：HGS 主迴圈流程圖**（Slide 10）
```
建議工具：draw.io（免費）或 Miro
可直接使用 Spec 03 中的 ASCII 流程圖稍微美化即可
```

**圖表 4：系統四層架構圖**（Slide 15）
```
可直接參考 fullstack實作完整報告.md 中的 ASCII 圖美化
建議工具：draw.io
```

---

## 第二階段：投影片製作

依照 specs/ 目錄下的內容逐張製作。

### Task 2.1 — Title + Agenda（Slides 1–2）
- [ ] 製作 Slide 1 Title（含背景地圖）
- [ ] 製作 Slide 2 Agenda（5個章節圓形圖示）

### Task 2.2 — Introduction（Slides 3–6）
- [ ] Slide 3: VRP 問題定義（含地圖截圖）
- [ ] Slide 4: NP-hard 說明（數字視覺化）
- [ ] Slide 5: 演化類比表格（自然界 vs 演算法）
- [ ] Slide 6: 貢獻概述（雙欄）

### Task 2.3 — Related Work（Slides 7–9）
- [ ] Slide 7: 求解器比較表格
- [ ] Slide 8: HGS 研究歷史時間軸
- [ ] Slide 9: PyVRP 論文三大貢獻

### Task 2.4 — Methods: Algorithm（Slides 10–14）
- [ ] Slide 10: HGS 主迴圈流程圖（重點製作，需要時間）
- [ ] Slide 11: 選擇 + SREX 交叉示意
- [ ] Slide 12: 局部搜尋操作符表格 + 示意
- [ ] Slide 13: 族群管理 + BPD 多樣性
- [ ] Slide 14: 動態懲罰機制流程

### Task 2.5 — Methods: System（Slides 15–16）
- [ ] Slide 15: 四層架構圖（直接美化 draw.io）
- [ ] Slide 16: 三大技術挑戰（三欄）

### Task 2.6 — Results（Slides 17–20）
- [ ] Slide 17: CVRP 橫條圖（需要先完成 Task 1.2 圖表 1）
- [ ] Slide 18: VRPTW 橫條圖（需要先完成 Task 1.2 圖表 2）
- [ ] Slide 19: 系統截圖 2×2（需要先完成 Task 1.1）
- [ ] Slide 20: 台北案例全頁截圖 + 說明

### Task 2.7 — Conclusion + Q&A（Slides 21–23）
- [ ] Slide 21: 雙軌貢獻總結
- [ ] Slide 22: 限制與未來工作
- [ ] Slide 23: Q&A + References

---

## 第三階段：校對與演練

### Task 3.1 — 內容校對清單
- [ ] 所有數據是否與論文一致（Gap 數值、迭代次數等）
- [ ] 所有技術術語是否拼寫正確（HGS, SREX, BPD, VRPTW...）
- [ ] 投影片文字是否有中英混用不一致的問題
- [ ] 截圖解析度是否清晰（在投影機上放大也看得清楚）

### Task 3.2 — Presenter Notes 完善
- [ ] 每張投影片都有 Presenter Notes
- [ ] 每個 Notes 都包含：核心訊息 + 過渡語
- [ ] 預備 Q&A 回答（參考 Spec 06 的附錄）

### Task 3.3 — 時間測試
- [ ] 完整試講一次，計時
- [ ] 目標：15 分鐘以內
- [ ] 若超時：優先刪減 Related Work 的細節

### Task 3.4 — 技術備案
- [ ] 確認系統可以 Live Demo（提前 30 分鐘啟動）
- [ ] 備用：錄製一段操作影片（以防網路/系統問題）
- [ ] 關閉瀏覽器其他分頁，避免通知干擾

---

## 重要數據速查（製作時可直接引用）

### 演算法核心數據
| 指標 | 數值 | 來源 |
|------|------|------|
| CVRP Mean Gap | **0.22%** | 論文 Table 1 |
| VRPTW Mean Gap | **0.40%** | 論文 Table 2 |
| 改善 BKS 數量 | **27 個** | 論文 Section 6 |
| 局部搜尋佔用時間 | **80–90%** | 論文 Section 3 |
| Population 大小 | **25–65** | Table 3 (Appendix A) |
| Target feasible | **43%** | Table 3 |
| Restart 條件 | **20,000 次無改善** | GeneticAlgorithmParams |

### 系統實作數據
| 指標 | 數值 | 來源 |
|------|------|------|
| 台北日班求解時間 | **~8 秒** | 實測 |
| 台北日班總距離 | **~92 km** | 實測 |
| 台北日班使用車輛 | **3 台**（共 6 台）| 實測 |
| 台北日班店面數 | **16 家** | taipei_demo.json |
| API 端點數 | **2**（health + solve）| routes.py |
| Pydantic models | **8 個** | schemas.py |
| 自訂例外類型 | **5 種** | exceptions.py |
| JS 模組數 | **3**（api, map, form）| 前端 js/ |
| 支援顏色數 | **10 色 palette** | serializer.py |

---

## 完成標準

當以下所有項目打勾，視為任務完成：

- [ ] 23 張投影片全部製作完成
- [ ] Presenter Notes 填寫完整
- [ ] 完整試講時間 ≤ 15 分鐘
- [ ] Live Demo 系統可正常運行
- [ ] 所有數據與論文/實作報告一致
- [ ] 已準備 5 題 Q&A 回答稿
