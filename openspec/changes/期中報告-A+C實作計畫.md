# 期中報告實作計畫：A + C 組合

> **主題：** 以遺傳演算法解決台灣便利超商補貨路線規劃問題
> **對照：** 自實作的純 Python GA（方向 A）vs PyVRP HGS（論文方法）

---

## 整體架構圖

```
第一部分：方向 A（純 Python GA 解 TSP）
  └─ 問題：一台補貨車跑完台北某區所有 7-ELEVEN（TSP 版本）
  └─ 方法：自己寫遺傳演算法

第二部分：方向 C（PyVRP 解 CVRP）
  └─ 問題：多台補貨車一起出發，每台有載重限制（VRP 版本）
  └─ 方法：用 PyVRP（HGS）求解

第三部分：對比分析
  └─ 解的品質比較、執行時間比較、圖像化展示
```

---

## 一、資料取得

### 最推薦：政府開放資料平台（直接下載 CSV，無需申請）

| 超商品牌 | 門市數 | 資料網址 |
|---------|--------|---------|
| 7-ELEVEN | ~7,021 | https://data.gov.tw/ 搜尋「7-ELEVEN 門市」 |
| 全家 FamilyMart | ~4,251 | https://data.gov.tw/ 搜尋「全家便利商店」 |
| 萊爾富 Hi-Life | ~1,590 | 同上 |

### 備用：7-ELEVEN 電子地圖 API（非官方，可直接查詢）

```python
import requests

# POST 請求可取得指定縣市的門市列表（含經緯度）
url = "http://emap.pcsc.com.tw/EMapSDK.aspx"
payload = {
    "commandid": "SearchStore",
    "city": "台北市",
    "town": "大安區"
}
resp = requests.post(url, data=payload)
# 回傳 XML，解析後有 X（經度）、Y（緯度）
```

### 建議範圍：縮小到「台北市大安區」

全台灣 7,000 家太多，做期中報告選一個區就夠了：
- 大安區 7-ELEVEN 約 **30–40 家**
- 規模適中，GA 可以在幾秒內跑完
- 有明顯的地理分布（可以畫出來看）

---

## 二、問題設定

### Part A：TSP 版本（你的純 Python GA）

```
假設：
  - 一台補貨車，從配送中心出發
  - 要跑完大安區所有 7-ELEVEN
  - 最後回到配送中心
  - 目標：最短總行駛距離

資料：
  - 門市座標（從政府開放資料取得）
  - 配送中心：假設為台北市仁愛路某點（可自訂）
  - 距離計算：使用 Haversine 公式（球面距離）或直線距離
```

### Part C：CVRP 版本（PyVRP HGS）

```
假設：
  - 3 台補貨車同時從配送中心出發
  - 每台車最多載 500 箱商品
  - 每間門市每次補貨需求：10–50 箱（隨機生成或查資料）
  - 目標：所有車輛總行駛距離最短

延伸（如果要加時間窗 VRPTW）：
  - 7-ELEVEN 只在 06:00–08:00 接受補貨（早上補貨時間窗）
  - 行車時間用距離/平均速度估算
```

---

## 三、純 Python GA 實作設計（方向 A 的程式碼骨架）

### 3.1 資料結構

```python
import math
import random

# 門市資料（從 CSV 讀入）
stores = [
    {"id": 0, "name": "配送中心", "lat": 25.033, "lon": 121.543},
    {"id": 1, "name": "大安路門市", "lat": 25.026, "lon": 121.541},
    # ... 其餘門市
]

def haversine(lat1, lon1, lat2, lon2):
    """計算兩點間的球面距離（公里）"""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))
```

### 3.2 染色體表示

```
解的表示：一個排列（permutation）
例如：[0, 5, 12, 3, 8, 21, ..., 0]
       ^                          ^
     出發點                     回到起點

含義：車子依序拜訪這些門市
```

### 3.3 GA 主要元件

```python
# 1. 初始解（隨機排列）
def random_solution(n_stores):
    route = list(range(1, n_stores))  # 不含起點 0
    random.shuffle(route)
    return route

# 2. 適應度（路徑總長，越短越好）
def total_distance(route, stores):
    total = 0
    prev = 0  # 從配送中心出發
    for store_id in route:
        total += haversine(...prev..., ...store_id...)
        prev = store_id
    total += haversine(...prev..., ...0...)  # 回到配送中心
    return total

# 3. 選擇（競賽選擇，對應 HGS 的 k-way tournament）
def tournament_select(population, k=3):
    candidates = random.sample(population, k)
    return min(candidates, key=lambda x: x.fitness)

# 4. 交叉（OX：順序交叉，保留相對順序）
def order_crossover(parent1, parent2):
    # 隨機選一段從 parent1 繼承，其餘按 parent2 順序填入
    ...

# 5. 突變（2-swap：隨機交換兩個門市位置）
def swap_mutate(route, mutation_rate=0.02):
    if random.random() < mutation_rate:
        i, j = random.sample(range(len(route)), 2)
        route[i], route[j] = route[j], route[i]
    return route

# 6. 局部搜尋（2-OPT，對應 HGS 的核心操作）
def two_opt(route, stores):
    improved = True
    while improved:
        improved = False
        for i in range(len(route) - 1):
            for j in range(i + 2, len(route)):
                # 嘗試反轉 route[i+1:j+1]
                new_route = route[:i+1] + route[i+1:j+1][::-1] + route[j+1:]
                if total_distance(new_route, stores) < total_distance(route, stores):
                    route = new_route
                    improved = True
    return route

# 7. GA 主迴圈
def run_ga(stores, pop_size=100, generations=500):
    population = [random_solution(len(stores)) for _ in range(pop_size)]
    best = min(population, key=lambda r: total_distance(r, stores))

    for gen in range(generations):
        new_pop = []
        for _ in range(pop_size):
            p1 = tournament_select(population)
            p2 = tournament_select(population)
            child = order_crossover(p1, p2)
            child = swap_mutate(child)
            child = two_opt(child, stores)  # ← 這是關鍵：局部搜尋
            new_pop.append(child)

        population = new_pop
        current_best = min(population, key=lambda r: total_distance(r, stores))
        if total_distance(current_best, stores) < total_distance(best, stores):
            best = current_best

    return best
```

---

## 四、PyVRP 建模（方向 C 的程式碼骨架）

```python
from pyvrp import Model
from pyvrp.stop import MaxRuntime
import pandas as pd

# 讀取門市資料
df = pd.read_csv("taipei_daan_711.csv")  # 你的門市 CSV

# 建立 PyVRP 模型
m = Model()
m.add_vehicle_type(
    capacity=500,      # 每台車最多 500 箱
    num_available=3    # 3 台補貨車
)

# 加入配送中心（depot）
depot = m.add_depot(
    x=int(df_depot["lon"] * 10000),  # PyVRP 用整數座標
    y=int(df_depot["lat"] * 10000)
)

# 加入所有門市
clients = []
for _, row in df.iterrows():
    c = m.add_client(
        x=int(row["lon"] * 10000),
        y=int(row["lat"] * 10000),
        demand=int(row["demand"])  # 每家門市的補貨需求量
    )
    clients.append(c)

# 加入距離邊（Haversine 距離，轉換成整數公尺）
all_locs = [depot] + clients
for i, frm in enumerate(all_locs):
    for j, to in enumerate(all_locs):
        dist = haversine(frm.y/10000, frm.x/10000,
                         to.y/10000, to.x/10000)
        m.add_edge(frm, to, distance=int(dist * 1000))  # 轉成公尺

# 求解
result = m.solve(stop=MaxRuntime(10))
print(result)
```

---

## 五、實驗設計（對比分析）

### 實驗 1：GA（有 2-OPT）vs GA（無 2-OPT）

| 條件 | 目的 |
|------|------|
| GA 有 2-OPT | 驗證局部搜尋的重要性（對應 HGS 的設計哲學） |
| GA 無 2-OPT | 對照組 |

**預期結果：** 加了 2-OPT 後解品質大幅提升，這正是 HGS 最核心的洞見。

---

### 實驗 2：TSP（單車）vs CVRP（多車）

| 問題設定 | 求解方法 | 比較指標 |
|---------|---------|---------|
| 單車跑完全部門市（TSP） | 你的 GA | 總距離 |
| 3 台車分工（CVRP） | PyVRP HGS | 總距離 |

**預期結果：** 多台車總距離更短（分工後每條路線更緊湊）。

---

### 實驗 3：純 Python GA vs PyVRP HGS（同問題規模）

| 方法 | 時間限制 | 解品質 | 執行時間 |
|------|---------|--------|---------|
| 你的 GA（TSP） | 30 秒 | ? | ? |
| PyVRP HGS（CVRP） | 30 秒 | ? | ? |

**討論方向：** 為什麼 HGS 更好？（更複雜的操作符、動態懲罰機制、更好的多樣性維持）

---

### 輸出圖表建議

1. **門市分布圖**：台北市大安區的 7-ELEVEN 地點（散點圖）
2. **GA 最佳路徑圖**：單車跑完所有門市的路線（折線圖疊加地圖）
3. **PyVRP 路線圖**：三台車各自的路線（三種顏色）
4. **收斂曲線**：GA 每一代的最佳解品質 vs 迭代次數
5. **對比柱狀圖**：GA（無 2-OPT）/ GA（有 2-OPT）/ HGS 三種方法的解品質

---

## 六、取得資料的具體步驟

### Step 1：下載政府開放資料

去 [https://data.gov.tw](https://data.gov.tw) 搜尋「7-ELEVEN 門市」，下載 CSV。
欄位通常包含：`門市名稱`, `縣市`, `鄉鎮市區`, `地址`, `經度`, `緯度`, `電話`

### Step 2：篩選到台北市大安區

```python
import pandas as pd

df = pd.read_csv("711_stores.csv")
daan = df[(df["縣市"] == "台北市") & (df["鄉鎮市區"] == "大安區")]
print(f"大安區共 {len(daan)} 家 7-ELEVEN")
daan.to_csv("taipei_daan_711.csv", index=False)
```

### Step 3：加入補貨需求量（模擬）

由於真實補貨量不公開，模擬生成：

```python
import numpy as np
daan["demand"] = np.random.randint(20, 80, size=len(daan))
# 每家每次補貨 20–80 箱（可根據門市大小調整）
```

### Step 4：視覺化確認資料分布

```python
import matplotlib.pyplot as plt

plt.figure(figsize=(8, 8))
plt.scatter(daan["經度"], daan["緯度"], c="blue", s=50, label="7-ELEVEN 門市")
plt.scatter([121.543], [25.033], c="red", s=200, marker="*", label="配送中心")
for _, row in daan.iterrows():
    plt.annotate(row["門市名稱"], (row["經度"], row["緯度"]), fontsize=6)
plt.title("台北市大安區 7-ELEVEN 分布")
plt.legend()
plt.savefig("store_distribution.png", dpi=150)
```

---

## 七、報告章節建議

```
1. 摘要（1 頁）
   - 問題、方法、主要發現

2. 問題介紹（1–2 頁）
   - VRP 是什麼
   - 台灣便利超商補貨的實際問題
   - 為什麼這是 VRP

3. 相關方法回顧（1–2 頁）
   - HGS 演算法（來自論文）
   - 遺傳演算法基本架構
   - 2-OPT 局部搜尋

4. 資料與問題建模（1 頁）
   - 資料來源（政府開放資料）
   - 如何建模成 TSP / CVRP
   - 距離計算方式

5. 實作方法（2 頁）
   - 你的純 Python GA（程式碼說明）
   - PyVRP 建模（程式碼說明）

6. 實驗結果（2–3 頁）
   - 三張路線圖
   - 收斂曲線
   - 三種方法對比表格

7. 討論（1 頁）
   - 為什麼 HGS 比純 GA 好？
   - 2-OPT 的貢獻有多大？
   - 實際應用上還需要考慮什麼？

8. 結論（0.5 頁）
```

---

*整理時間：2026-04-06*
