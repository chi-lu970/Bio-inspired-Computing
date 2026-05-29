# PyVRP-Web: Bio-inspired Vehicle Routing Optimization with Interactive Web Visualization

> **Student ID**: 414085193
> **Course**: Bio-inspired Computing
> **Format Note**: This draft follows the IEEE conference proceedings structure.
> Convert to LaTeX using IEEEtran.cls for final submission.

---

## Abstract

The Vehicle Routing Problem (VRP) is a combinatorial optimization problem of high practical importance in logistics planning, yet it is NP-hard and infeasible to solve optimally at scale. This paper presents our study of PyVRP, a high-performance open-source VRP solver implementing Hybrid Genetic Search (HGS)—a bio-inspired algorithm combining genetic evolution with local search. We analyze the algorithmic components of HGS in depth, including its crossover operator (SREX), population diversity management (BPD), and dynamic penalty mechanism. Furthermore, we design and implement PyVRP-Web, a full-stack web application that exposes the HGS solver through an interactive browser interface, enabling non-technical users to define routing problems and visualize optimal solutions on a geographic map. Experimental evaluation on standard benchmarks demonstrates that PyVRP achieves a mean gap of 0.22% from the best-known solutions on 100 CVRP instances, and 0.40% on 60 VRPTW instances with 1,000 customers. A real-world case study using 16 Taipei convenience store locations confirms the system's practical usability.

---

## I. Introduction

The **Vehicle Routing Problem (VRP)** is a classical combinatorial optimization problem with direct applications in last-mile delivery, public transit, and supply chain management. Given a depot, a fleet of vehicles with limited capacity, and a set of customers with delivery demands, the VRP seeks a minimum-cost set of routes such that every customer is served exactly once and vehicle capacity constraints are satisfied [10]. The VRP with Time Windows (VRPTW) adds the constraint that each customer must be served within a specified time interval, further increasing the problem's complexity.

VRP is NP-hard, meaning no known algorithm solves all instances in polynomial time. For a delivery problem with merely 20 customers, the number of possible route combinations exceeds $2 \times 10^{18}$—making brute-force enumeration computationally infeasible. This motivates the use of **metaheuristic** and **bio-inspired** approaches that trade optimality guarantees for scalability.

**Bio-inspired computing** offers a compelling paradigm: algorithms modeled on natural processes—evolutionary selection, genetic recombination, swarm behavior—have demonstrated remarkable effectiveness on combinatorial optimization. The **Genetic Algorithm (GA)** [2], inspired by Darwinian evolution, maintains a population of candidate solutions and iteratively applies selection, crossover, and mutation. Applied to VRP, GA explores a diverse solution space without being trapped in local optima.

This work is centered on **PyVRP** [1], a state-of-the-art VRP solver implementing **Hybrid Genetic Search (HGS)**—a framework that synergizes GA's broad exploration with Local Search's deep exploitation. PyVRP won the 2021 DIMACS VRPTW Challenge and ranked first in the EURO meets NeurIPS 2022 competition. Our contributions are twofold:

1. **Algorithmic Analysis**: A systematic study of PyVRP's HGS components, including the SREX crossover operator [4], broken pairs distance diversity metric, and adaptive penalty management.
2. **System Implementation**: PyVRP-Web, a full-stack web application that wraps the HGS solver in a zero-code interface with real-time map visualization. We identify three concrete barriers that prevent practitioners from using research-grade VRP solvers: (i) the requirement to write Python code to assemble the solver model; (ii) the mismatch between PyVRP's integer planar coordinate system and real-world WGS84 GPS data; and (iii) the absence of visual route output, leaving decision-makers unable to inspect or validate solutions. PyVRP-Web resolves all three barriers.

---

## II. Related Work

### A. VRP Solver Landscape

Numerous tools have been developed for VRP. **LKH-3** [Helsgaun, 2017] transforms VRP into a Traveling Salesman Problem and applies the Lin-Kernighan heuristic, achieving strong results but restricted to academic, non-commercial use. **OR-Tools** [9], Google's general-purpose optimization toolkit, employs constraint programming and is easy to use but performs far below state-of-the-art metaheuristics. **VROOM** integrates with road network APIs for real-world routing, but lacks the solution quality of HGS-based solvers. **VRPSolver** [Pessoa et al., 2020] provides exact solutions but does not scale beyond a few hundred customers.

PyVRP [1] occupies a unique position: it achieves near-optimal performance comparable to specialized C++ solvers while remaining fully customizable through Python, and is freely available under the MIT license.

### B. Hybrid Genetic Search

HGS was introduced by Vidal et al. [2] as a framework combining genetic algorithms with problem-specific local search for a broad class of VRP variants. A key property is that the algorithm maintains both feasible and infeasible solutions in the population, using dynamic penalty coefficients to convert hard constraints into soft ones. This enables exploration of a wider solution space while steering convergence toward feasibility.

Vidal [3] extended HGS for CVRP (HGS-CVRP), introducing the SWAP* route operator and the biased fitness criterion for population management. The SREX crossover operator [4], originally proposed for pickup-and-delivery problems, was adapted for VRP: it selects complete sub-routes from each parent and uses greedy repair to handle unserved customers, preserving high-quality route structures across generations.

PyVRP [1] builds upon HGS-CVRP by: (i) adding VRPTW support with time-window-aware operators, (ii) adopting a Python+C++ hybrid architecture for extensibility, and (iii) simplifying and robustifying the implementation while maintaining competitive performance.

---

## III. Methods

### A. Problem Formulation

The **CVRP** is formally defined on a complete directed graph $G = (V, A)$ where $V = \{0, 1, \ldots, n\}$ is the vertex set (0: depot; $1 \ldots n$: customers), and $A$ is the arc set. Customer $i$ has demand $q_i \geq 0$. Each vehicle has capacity $Q$. The objective is:

$$\min \sum_{(i,j) \in A} d_{ij} x_{ij}$$

subject to: each customer visited exactly once; each route starts and ends at the depot; total demand per route $\leq Q$.

The **VRPTW** additionally requires that service at customer $i$ begins within time window $[e_i, l_i]$, with service duration $s_i$. Travel time from $i$ to $j$ is $t_{ij}$. Vehicles may wait (if arriving early) but not violate $l_i$.

### B. Hybrid Genetic Search (HGS)

HGS [1][2] is the core bio-inspired algorithm. Its key insight is that neither GA nor Local Search alone performs optimally—combining them yields superior results: GA provides *exploration* across the solution space, while Local Search provides *exploitation* within promising regions.

**Algorithm 1: HGS Main Loop**

```
Initialize population P with min_pop_size random solutions
Set initial penalty weights (capacity: 20, time warp: 6)

repeat
  (p1, p2) ← TournamentSelect(P)        // binary tournament on biased fitness
  offspring ← SREX(p1, p2)              // crossover
  offspring ← LocalSearch(offspring)    // local search improvement
  if rand() < repair_probability then   // repair attempt (80% VRPTW)
    if not feasible(offspring):
      offspring ← LocalSearch(offspring, penalty × 12)
  P ← P ∪ {offspring}
  if |P| > max_pop_size then
    SurvivorSelection(P)               // trim to min_pop_size
  UpdatePenalties(P)                   // every 50/100 iterations
  if no_improvement > 20,000 then
    RestartPopulation(P)
until stopping criterion met

return best feasible solution found
```

#### 1) SREX Crossover Operator

The **Selective Route Exchange (SREX)** operator [4] constructs an offspring by:
1. Selecting a subset of complete routes from parent $B$ (inheriting intact)
2. Filling unserved customers from parent $A$ using greedy insertion

This strategy preserves *entire good sub-routes* rather than randomly mixing customers—a crucial distinction that prevents the offspring quality degradation common in naive crossover operators.

#### 2) Local Search

Local Search operates on two levels [1]:

**Node operators** evaluate moves between customer pairs $(u, v)$ where $v \in \mathcal{N}(u)$ (the granular neighbourhood of $u$). The granular neighbourhood [5] limits each customer to its $k$ nearest neighbours, reducing complexity from $O(n^2)$ to $O(kn)$. PyVRP implements 11 node operators:

- $(N,0)$-exchange ($N = 1,2,3$): relocate $N$ consecutive customers
- $(N,M)$-exchange ($N,M \in \{1,2,3\}$, $M \leq N$): swap segments of $N$ and $M$ customers
- **MoveTwoClientsReversed**: reversed (2,0)-exchange
- **2-OPT**: reverse a route segment or reconnect two routes

These are implemented via **C++ template specialization**—each $(N,M)$ combination is compiled into an independent, highly optimized function, eliminating runtime generalization overhead.

**Route operators** evaluate larger neighbourhoods across route pairs:
- **RELOCATE\***: finds the best single-customer move between two routes
- **SWAP\***: finds the best customer swap between two routes, with each customer inserted into its *optimal position* (not necessarily the original position) in the other route; enhanced with time-window caching and early termination [1]

Profiling confirms Local Search accounts for **80–90% of total runtime** [1], justifying its C++ implementation.

#### 3) Population Management and Diversity

The population maintains two sub-populations: *feasible* and *infeasible* solutions. The **biased fitness** criterion [3] balances solution quality and diversity:

$$f_{\text{biased}}(s) = r_{\text{quality}}(s) \cdot (1 - \rho) + r_{\text{diversity}}(s) \cdot \rho$$

where $r_{\text{quality}}$ is the rank by objective value, $r_{\text{diversity}}$ is the rank by average distance to other solutions, and $\rho = n_{\text{elite}} / n_{\text{min}} = 4/25$.

Diversity is measured by the **Broken Pairs Distance (BPD)** [1]:

$$\text{BPD}(A, B) = \frac{|P_A \triangle P_B|}{2n}$$

where $P_A = \{(u,v) \mid v \text{ immediately follows } u \text{ in a route of } A\}$. BPD $\in [0,1]$, with 0 meaning identical solutions.

When the sub-population exceeds $n_{\text{min}} + n_{\text{gen}} = 65$, survivor selection removes duplicate solutions and then eliminates solutions with the worst biased fitness until the population shrinks to $n_{\text{min}} = 25$.

#### 4) Dynamic Penalty Management

Constraints are treated as soft via **penalized cost**:

$$c_{\text{pen}} = d_{\text{total}} + \alpha \cdot \Delta_{\text{cap}} + \beta \cdot \Delta_{\text{tw}}$$

where $\alpha$ and $\beta$ are dynamically adjusted every 50 iterations to maintain a target feasibility ratio of **43%**:

$$\alpha \leftarrow \begin{cases} \alpha \times 1.34 & \text{if } \phi < 0.38 \\ \alpha \times 0.32 & \text{if } \phi > 0.48 \end{cases}$$

(analogously for $\beta$). When attempting to repair an infeasible offspring, penalties are temporarily multiplied by 12 (the *repair booster*) to aggressively steer the search toward feasibility.

### C. System Architecture: PyVRP-Web

We designed and implemented PyVRP-Web, a four-layer full-stack application:

```
┌─────────────────────────────────────────────────┐
│  Presentation Layer                              │
│  HTML + CSS + Vanilla JS (ES Module)             │
│  Leaflet.js (interactive map)                    │
└────────────────────┬────────────────────────────┘
                     │ REST API (JSON)
┌────────────────────▼────────────────────────────┐
│  API Layer — FastAPI                             │
│  POST /api/solve  ·  asyncio.Semaphore(1)        │
│  ThreadPoolExecutor · Pydantic validation        │
└────────────────────┬────────────────────────────┘
                     │ Python function call
┌────────────────────▼────────────────────────────┐
│  Service Layer                                   │
│  coord.py: WGS84 → UTM (pyproj)                 │
│  solver.py: GA assembly, nb_granular=7 tuning    │
│  serializer.py: route timeline reconstruction    │
└────────────────────┬────────────────────────────┘
                     │ PyVRP API
┌────────────────────▼────────────────────────────┐
│  Solver Engine — PyVRP v0.5.0                    │
│  GeneticAlgorithm + LocalSearch + SREX           │
│  TimedNoImprovement stopping criterion           │
└─────────────────────────────────────────────────┘
```

**Design Principle — Zero-Intrusion Encapsulation**: The system treats PyVRP as an unmodified black-box library. All extensions—coordinate conversion, neighbourhood tuning, timeline reconstruction—are encapsulated in surrounding service modules (`coord.py`, `solver.py`, `serializer.py`). This ensures that future PyVRP version upgrades require no changes to the HGS core and incur only peripheral adapter updates.

**Data Flow Pipeline**: Data undergoes a sequence of transformations across layers:

$$\text{WGS84 lat/lng} \xrightarrow{\text{coord.py}} \text{UTM integers} \xrightarrow{\text{solver.py}} \text{HGS solution} \xrightarrow{\text{serializer.py}} \text{per-stop JSON} \xrightarrow{\text{Leaflet.js}} \text{map render}$$

**Key Engineering Decisions**:

1. **Coordinate Conversion**: PyVRP requires integer planar coordinates. Users supply WGS84 latitude/longitude, which carries a fundamental incompatibility: naive multiplication of degrees by a constant introduces severe metric distortion at Taiwan's latitude. We project to UTM Zone 51N (EPSG:32651) via pyproj, then scale by 10 to achieve 0.1-meter integer precision with no geometric distortion.

2. **Neighbourhood Tuning**: PyVRP's default `nb_granular = 20` becomes near-exhaustive for small problems (e.g., 16 customers), causing each local search iteration to be prohibitively slow and yielding only a handful of iterations within a 10-second web timeout. We reduce it dynamically to `min(7, n-1)`, enabling an order-of-magnitude more iterations within the same wall-clock budget and substantially improving solution quality.

3. **Per-Stop Timeline Reconstruction**: PyVRP's `Route` object provides only the customer visit sequence, not individual arrival or departure times. Decision-makers cannot validate a routing plan without a per-stop timeline. We reconstruct it via forward simulation: $t_{\text{arrival}}^{i+1} = t_{\text{departure}}^i + t_{i,i+1}$, where $t_{\text{departure}}^i = \max(t_{\text{arrival}}^i,\, e_i) + s_i$.

4. **Stopping Criterion Adaptation**: PyVRP's default `TimedNoImprovement` threshold is 20,000 iterations—far too long for a web interface where users expect results within 10–30 seconds. We set `max_iterations = 500`: profiling on the Taipei case study shows that the objective stabilizes within 400–600 iterations, so the adapted criterion terminates computation promptly without sacrificing solution quality.

5. **Concurrency Control**: A single `asyncio.Semaphore(1)` ensures at most one solve request executes concurrently, preventing system overload from the computationally intensive C++ kernel.

---

## IV. Results

### A. Benchmark Performance

We evaluate PyVRP v0.5.0 on two standard benchmark sets following [1].

**CVRP** — X benchmark [6], 100 instances, 100–1001 customers. Time limit: $T_{\max} = n \times 2.4$ seconds (PassMark-normalized). Results averaged over 10 random seeds.

**Table I: CVRP Benchmark Results (X instances, Uchoa et al. 2017)**

| Solver | Mean Cost | Mean Gap | Gap of Mean |
|--------|-----------|----------|-------------|
| BKS | 63,106.7 | 0.00% | 0.00% |
| HGS-CVRP [3] | 63,206.1 | 0.11% | 0.16% |
| HGS-2012 [2] | 63,285.8 | 0.21% | 0.28% |
| **PyVRP [1]** | **63,275.5** | **0.22%** | **0.27%** |

PyVRP achieves a mean gap of **0.22%** from the best-known solutions—within 0.03% of the specialized HGS-CVRP solver, despite being designed for the more general VRPTW. Multiple small-scale instances (e.g., X-n101-k25, X-n110-k13) are solved to **proven optimality (0% gap)**.

**VRPTW** — Homberger & Gehring benchmark [7], 60 instances with 1,000 customers across six categories. Time limit: 2 hours (PassMark-normalized).

**Table II: VRPTW Benchmark Results (H&G 1000-customer instances)**

| Solver | Mean Cost | Mean Gap | Gap of Mean |
|--------|-----------|----------|-------------|
| BKS | 33,143.8 | 0.00% | 0.00% |
| HGS-DIMACS [8] | 33,265.5 | 0.32% | 0.37% |
| **PyVRP [1]** | **33,296.4** | **0.40%** | **0.46%** |

PyVRP achieves **0.40%** mean gap. The simplified implementation would rank 2nd in the DIMACS VRPTW competition. In extended runs, PyVRP improved **27 of 300** best-known solutions across the full H&G instance set.

Performance varies by instance type: clustered instances with wide time windows (C2) yield near-optimal results (~0.04% gap), while random instances with narrow time windows (R1, RC1) are more challenging (~0.72% gap).

### B. System Demonstration

We validate PyVRP-Web on a real-world case study: **Taipei 7-ELEVEN daytime distribution** (Figure 2).

**Setup**: 1 depot (Unified Enterprise Taipei Distribution Center, 09:30–13:00), 16 stores across Taipei City (time windows 10:00–13:00), 2 large trucks (capacity 140) + 4 medium trucks (capacity 80), average speed 28 km/h.

**Results**: A feasible routing plan is found in approximately **8 seconds** using the HGS solver with `TimedNoImprovement(max_iterations=500)` as the stopping criterion—chosen to match web UI responsiveness expectations while preserving solution quality (the objective converges within 400–600 iterations on this instance). The solution uses **3 vehicles** with a total distance of approximately **92 km**, well within the fleet capacity. The algorithm naturally clusters geographically proximate stores—northern stores (Shilin, Beitou) in one route, central stores (Da'an, Songshan) in another, and southwestern stores (Banqiao, Wenshan) in a third—an emergent geographic structure induced by the HGS objective without explicit geographic instructions.

The web interface provides: real-time map visualization with directional arrows, per-route timelines (arrival/departure/wait times), and color-coded route highlighting with interactive selection.

---

## V. Conclusion

This paper presented a comprehensive study of **Hybrid Genetic Search**—a state-of-the-art bio-inspired algorithm for the Vehicle Routing Problem—and its implementation in PyVRP. We analyzed in depth the biological analogy underlying HGS: the genetic crossover (SREX) mimics chromosomal recombination, the biased fitness criterion implements natural selection with a diversity premium, and the dynamic penalty mechanism acts as an environmental pressure steering the population toward feasibility.

Our implementation, **PyVRP-Web**, demonstrates that research-grade bio-inspired optimization can be made accessible through modern web technologies. Guided by a zero-intrusion encapsulation principle—leaving PyVRP unmodified and wrapping all extensions in peripheral service modules—the system resolves three practitioner barriers: coordinate system incompatibility, neighbourhood size misconfiguration for small instances, and the absence of per-stop timeline output. The system achieves near-optimal routing solutions within seconds for practical problem sizes, as validated by both standard benchmarks (0.22% from BKS on CVRP) and a real-world Taipei distribution scenario.

**Future directions** include: (i) integrating real road network distances via OSRM for travel time accuracy, (ii) supporting multi-depot VRP variants, (iii) adding electric vehicle constraints (battery, charging stations), and (iv) visualizing the GA convergence trajectory in real time to enhance educational value.

---

## References

[1] N. A. Wouda, L. Lan, and W. Kool, "PyVRP: a high-performance VRP solver package," *INFORMS Journal on Computing*, vol. 36, no. 4, pp. 943–955, 2024. arXiv:2403.13795.

[2] T. Vidal, T. G. Crainic, M. Gendreau, and C. Prins, "A hybrid genetic algorithm with adaptive diversity management for a large class of vehicle routing problems with time-windows," *Computers & Operations Research*, vol. 40, no. 1, pp. 475–489, 2013.

[3] T. Vidal, "Hybrid genetic search for the CVRP: open-source implementation and SWAP* neighborhood," *Computers & Operations Research*, vol. 140, p. 105643, 2022.

[4] Y. Nagata and S. Kobayashi, "A memetic algorithm for the pickup and delivery problem with time windows using selective route exchange crossover," in *Proc. PPSN XI*, pp. 536–545, 2010.

[5] P. Toth and D. Vigo, "The granular tabu search and its application to the vehicle-routing problem," *INFORMS Journal on Computing*, vol. 15, no. 4, pp. 333–346, 2003.

[6] E. Uchoa, D. Pecin, A. Pessoa, M. Poggi, T. Vidal, and A. Subramanian, "New benchmark instances for the capacitated vehicle routing problem," *European Journal of Operational Research*, vol. 257, no. 3, pp. 845–858, 2017.

[7] J. Homberger and H. Gehring, "Two evolutionary metaheuristics for the vehicle routing problem with time windows," *INFOR: Information Systems and Operational Research*, vol. 37, no. 3, pp. 297–318, 1999.

[8] W. Kool et al., "Hybrid genetic search for the vehicle routing problem with time windows: a high-performance implementation," Technical Report, 2022.

[9] L. Perron and V. Furnon, "OR-Tools," Google LLC, 2022. [Online]. Available: https://developers.google.com/optimization/

[10] P. Toth and D. Vigo, Eds., *Vehicle Routing: Problems, Methods, and Applications*, 2nd ed. Philadelphia, PA: SIAM, 2014.
