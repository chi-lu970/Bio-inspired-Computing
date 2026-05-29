# Spec: Methods — System Implementation Slides (Slides 15–16)

---

## Slide 15 — System Architecture

**標題**：`Our Contribution: PyVRP-Web Full-Stack System`

**四層架構圖（直接引用實作報告的 ASCII 圖，製作成視覺化版本）**：

```
┌──────────────────────────────────────────────────────┐
│              PRESENTATION LAYER                      │
│  HTML + CSS + Vanilla JS (ES Module)                 │
│  Leaflet.js Map  ·  Form Validation  ·  Route Colors │
└─────────────────────────┬────────────────────────────┘
                          │ fetch() / JSON
┌─────────────────────────▼────────────────────────────┐
│                 API LAYER (FastAPI)                   │
│  POST /api/solve  ·  Pydantic validation             │
│  ThreadPoolExecutor  ·  asyncio.Semaphore(1)          │
└─────────────────────────┬────────────────────────────┘
                          │ Python function call
┌─────────────────────────▼────────────────────────────┐
│              SERVICE LAYER                           │
│  coord.py: WGS84 → UTM          solver.py: HGS wrap  │
│  pyproj library                  nb_granular=7 fix   │
│  serializer.py: Route → JSON    exceptions.py: 5 err │
└─────────────────────────┬────────────────────────────┘
                          │ GA + Local Search
┌─────────────────────────▼────────────────────────────┐
│              SOLVER ENGINE (PyVRP)                   │
│  GeneticAlgorithm + LocalSearch + SREX crossover     │
│  TimedNoImprovement stop criterion                   │
└──────────────────────────────────────────────────────┘
```

**右側技術選型列表**：
```
Frontend:  Vanilla JS + Leaflet.js (no framework overhead)
Backend:   FastAPI (async, auto OpenAPI docs)
Geo:       pyproj WGS84→UTM conversion
Solver:    PyVRP v0.5.0 (PyVRP paper's version)
Protocol:  JSON REST API
```

**底部 Takeaway**：
```
"Fill the form → Click Solve → See the map"
Zero programming required. HGS solver accessible to anyone.
```

**Presenter Notes**：
> "We built four layers: the browser UI, the FastAPI REST layer, the service layer that handles coordinate conversion and GA tuning, and finally PyVRP itself. The key design principle was keeping PyVRP untouched—we treated it as a black-box library, only adding the web wrapper around it."

---

## Slide 16 — Key Technical Challenges

**標題**：`3 Non-Trivial Engineering Problems We Solved`

**三個問題各佔一欄（三欄版面）**：

---

**問題 1：座標系統不相容**

```
[圖示: 地球儀 → 網格]

Problem:
PyVRP requires INTEGER planar coordinates
Users input WGS84 lat/lng (floating point)

Naïve approach: multiply degrees by constant
→ Severe distortion in Taiwan's latitude range

Our solution:
WGS84 → UTM (EPSG:32651/32650)
         (pyproj library)
UTM meters × scale factor 10
→ 0.1-meter precision, no distortion
```

---

**問題 2：小問題求解過慢**

```
[圖示: 放大鏡 + 時鐘]

Problem:
PyVRP default nb_granular=20
For 16 customers → nearly exhaustive search
Each local search iteration: very slow
10-second limit: too few iterations, bad solution

Our solution:
NB_GRANULAR = min(7, num_clients - 1)
Smaller neighborhood → faster iterations
Same time → far more iterations → better solution
```

---

**問題 3：各站抵達時間計算**

```
[圖示: 時鐘 + 路線]

Problem:
PyVRP Route only gives visit ORDER
Does not provide arrival/departure times per stop

Our solution (serializer.py):
Walk-through simulation:
  departure = depot.tw_early
  for each stop:
    arrival = prev_departure + travel_time
    wait = max(0, stop.tw_early - arrival)
    departure = max(arrival, stop.tw_early)
               + service_minutes
```

**底部 Takeaway**：
```
Real engineering = bridging the gap between research API and user expectations.
```

**Presenter Notes**：
> "These three problems aren't listed in any tutorial. We discovered them by actually building and testing the system. The coordinate system issue is particularly subtle—a 1-degree error in longitude near Taiwan's latitude corresponds to roughly 100km of distance error."
