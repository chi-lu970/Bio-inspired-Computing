# Reproduction Guide — PyVRP-Web

> **Project**: PyVRP-Web: Bio-inspired Vehicle Routing Optimization with Interactive Web Visualization
> **Student ID**: 414085193
> **Course**: Bio-inspired Computing

This document explains how to set up, run, and reproduce the experimental results presented in the project report.

---

## 1. System Requirements

| Component | Version | Notes |
|-----------|---------|-------|
| Python | 3.11 | Must match PyVRP wheel version |
| uv | latest | Package manager (recommended) |
| OS | Windows 10/11, macOS, Linux | Pre-compiled binaries available |
| RAM | ≥ 4 GB | Recommended for large instances |
| Browser | Chrome / Firefox (latest) | For web interface |

---

## 2. Installation

### Step 1: Clone / Extract the Repository

```bash
# If from zip:
unzip TermProject_414085193.zip
cd TermProject_414085193
```

### Step 2: Install Dependencies

**Using uv (recommended)**:
```bash
# Install uv if not present
pip install uv

# Install all dependencies
uv sync
```

**Using pip (alternative)**:
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install pyvrp fastapi uvicorn pyproj
```

### Step 3: Verify Installation

```bash
uv run python -c "import pyvrp; print('PyVRP version:', pyvrp.__version__)"
# Expected output: PyVRP version: 0.5.0
```

---

## 3. Running the Web Application

### Start the Server

```bash
# Recommended method (handles sys.path correctly)
uv run --python 3.11 python run_server.py
```

If `run_server.py` is unavailable, use:
```bash
uv run --python 3.11 uvicorn webapp.backend.main:app --port 8000
```

### Access the Interface

| URL | Description |
|-----|-------------|
| `http://localhost:8000/` | Main web interface |
| `http://localhost:8000/docs` | FastAPI auto-generated API documentation |
| `http://localhost:8000/api/health` | Health check endpoint |

---

## 4. Reproducing the Case Study Results

### Case 1: Taipei Daytime Distribution (Section IV-B)

1. Open `http://localhost:8000/`
2. Click **"載入範例 ▾"** (Load Example) in the header
3. Select **"台北日班"** (Taipei Daytime)
4. Click **"開始計算"** (Start Solving)
5. Wait approximately 8–12 seconds
6. Observe: 3 routes, ~92 km total distance

**Expected output** (approximate, may vary by run due to random seed):
```
Routes used:    3
Total distance: ~88–96 km
Runtime:        ~6–12 seconds
Feasible:       true
```

**To fix the random seed** for exact reproduction, modify `webapp/frontend/examples/taipei_demo.json`:
```json
"config": {
  "seed": 42,
  "max_runtime_seconds": 10,
  "avg_speed_kmh": 28
}
```

### Case 2: Taipei Night-Shift Distribution

1. Load example **"台北大夜班"** (Taipei Night Shift)
2. Click **"開始計算"**
3. Allow up to 30 seconds (night-shift has tighter time windows)

---

## 5. Running PyVRP Algorithm Directly (No Web UI)

To reproduce the algorithm behavior without the web interface:

```python
from pyvrp import Model
from pyvrp.stop import MaxRuntime

m = Model()
m.add_vehicle_type(capacity=140, num_available=2)
m.add_vehicle_type(capacity=80, num_available=4)

depot = m.add_depot(x=2536, y=1361, tw_early=570, tw_late=780)

# Add stores (UTM coordinates × 10, integer)
# ... (see webapp/backend/services/solver.py for full example)

result = m.solve(stop=MaxRuntime(10.0), seed=42)
print(result)
```

For a minimal reproducible VRP example:

```python
import numpy as np
from pyvrp import Model
from pyvrp.stop import MaxRuntime

rng = np.random.default_rng(seed=42)
coords = rng.integers(0, 100, size=(11, 2))   # 10 customers + 1 depot
demands = rng.integers(1, 10, size=(11,))

m = Model()
m.add_vehicle_type(capacity=30, num_available=3)
depot = m.add_depot(x=int(coords[0][0]), y=int(coords[0][1]))
clients = [
    m.add_client(x=int(coords[i][0]), y=int(coords[i][1]), demand=int(demands[i]))
    for i in range(1, 11)
]
for frm in m.locations:
    for to in m.locations:
        dist = abs(frm.x - to.x) + abs(frm.y - to.y)
        m.add_edge(frm, to, distance=dist)

result = m.solve(stop=MaxRuntime(5.0), seed=42)
print(result)
print(f"Cost: {result.cost():.1f}, Feasible: {result.is_feasible()}")
```

---

## 6. Benchmark Experiments (Section IV-A)

The benchmark results in Table I and Table II are taken directly from PyVRP [1] using v0.5.0.

To reproduce the CVRP benchmark for a single instance:

```bash
# Download X-n101-k25 from CVRPLIB
# http://vrp.galgos.inf.puc-rio.br/

uv run python -m pyvrp X-n101-k25.vrp \
    --seed 42 \
    --max_runtime 240 \
    --round_func round
```

To reproduce the VRPTW benchmark for a single instance:

```bash
# Solomon/Homberger format required
uv run python -m pyvrp RC2_10_5.txt \
    --instance_format solomon \
    --round_func dimacs \
    --seed 42 \
    --max_runtime 7200
```

**Note**: Full benchmark reproduction (100 CVRP + 60 VRPTW instances, 10 seeds each) requires significant compute time (hours to days). The complete results are archived in [1].

---

## 7. Project File Structure

```
TermProject_414085193/
├── run_server.py                    Entry point for web server
├── pyproject.toml                   Dependencies declaration
│
├── webapp/
│   ├── backend/
│   │   ├── main.py                  FastAPI application
│   │   ├── api/
│   │   │   ├── routes.py            POST /api/solve endpoint
│   │   │   └── schemas.py           Pydantic request/response models
│   │   ├── services/
│   │   │   ├── coord.py             WGS84 → UTM coordinate conversion
│   │   │   ├── solver.py            PyVRP HGS integration
│   │   │   ├── serializer.py        Result → JSON (timeline reconstruction)
│   │   │   └── exceptions.py        Custom exception hierarchy
│   │   └── examples/
│   │       ├── taipei_demo.json     Taipei daytime example data
│   │       └── taipei_711_night.json  Taipei night-shift example data
│   │
│   └── frontend/
│       ├── index.html               Single-page application
│       ├── css/style.css            Layout and component styles
│       └── js/
│           ├── api.js               Fetch wrapper + AbortController
│           ├── map.js               Leaflet map management
│           └── form.js              Form validation + result rendering
│
└── README_reproduction.md           This file
```

---

## 8. Troubleshooting

| Problem | Solution |
|---------|---------|
| `ImportError: No module named '_pyvrp'` | Run `uv run --python 3.11 python run_server.py` (ensures correct venv) |
| Server starts but map doesn't load | Check browser console; CartoCDN requires internet access |
| Solve takes > 30 seconds | Reduce `max_runtime_seconds` in the form |
| `CrossUtmZoneError` | All locations must be within the same UTM zone (~6° longitude range) |
| Port 8000 already in use | Change port: `uvicorn ... --port 8001` |

---

## 9. References

[1] N. A. Wouda, L. Lan, and W. Kool, "PyVRP: a high-performance VRP solver package," *INFORMS Journal on Computing*, vol. 36, no. 4, pp. 943–955, 2024.
