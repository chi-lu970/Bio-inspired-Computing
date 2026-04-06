# Session Memory — PyVRP 學習與期中報告

## 使用者背景

- 仿生計算（Bio-inspired Computing）課程學生
- 目標：理解 PyVRP 論文程式碼，再撰寫**純 Python 遺傳演算法解 TSP**，作為期中報告的延伸應用
- 參考論文：*PyVRP: A High-Performance VRP Solver Package*，Wouda, Lan, Kool，INFORMS JoC 2024, Vol.36(4), pp.943–955
- 論文 PDF：https://arxiv.org/pdf/2403.13795
- 官方程式碼：https://github.com/INFORMSJoC/2023.0055

---

## 專案位置

```
/Users/lvshaoqi/Developer/PythonProjects/Bio＿inspired＿Computing/PyVRP
```

虛擬環境：`.venv/`（Python 3.13）
啟動方式：`source .venv/bin/activate`

---

## 環境建置紀錄

### 問題背景
PyVRP v0.5.0 官方只支援 Python 3.8–3.11，但本機使用 Python 3.13，PyPI 無預建 wheel，需從原始碼手動編譯 C++ 擴充套件。

### 套用的 Workarounds

1. 在 `.venv` 中安裝建置工具：
   ```bash
   pip install meson ninja poetry docblock
   ```

2. 手動下載 `pybind11-2.10.4.tar.gz`（SSL 問題無法自動抓取），放置於：
   ```
   subprojects/packagecache/pybind11-2.10.4.tar.gz
   ```

3. 建立 meson 所需的 Python wrapper script（meson 從 build 目錄以相對路徑尋找 python）：
   ```
   build/.venv/bin/python
   ```

4. 編譯完成後，手動將 `.so` 檔複製到 pyvrp 各子目錄：

   | 來源 | 目的地 |
   |------|--------|
   | `build/_pyvrp.cpython-313-darwin.so` | `pyvrp/` |
   | `build/_crossover.cpython-313-darwin.so` | `pyvrp/crossover/` |
   | `build/_diversity.cpython-313-darwin.so` | `pyvrp/diversity/` |
   | `build/_search.cpython-313-darwin.so` | `pyvrp/search/` |

---

## 驗證結果

執行 quick_tutorial 範例：

```python
m.solve(stop=MaxRuntime(3))
```

回傳最佳路線成本：**6208**（正確）

---

## 下一步（待辦）

- [ ] 深入理解 PyVRP 的 Hybrid Genetic Search（HGS）演算法架構
- [ ] 設計純 Python GA 解 TSP（期中報告核心）
- [ ] 撰寫報告，說明 HGS 與簡化版 GA 的對應關係
