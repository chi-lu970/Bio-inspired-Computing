# LaTeX 完整模板 — 可直接使用

> 將以下內容存為 `main.tex`，搭配 `IEEEtran.cls` 編譯。
> Overleaf 可直接使用：建立新專案 → 選 IEEE Conference 模板 → 替換內容。

---

## main.tex

```latex
\documentclass[conference]{IEEEtran}

% ── Packages ──────────────────────────────────────────────
\usepackage{cite}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{hyperref}
\usepackage{algorithm}
\usepackage{algpseudocode}
\usepackage{array}

% ── Title ─────────────────────────────────────────────────
\begin{document}

\title{PyVRP-Web: Bio-inspired Vehicle Routing Optimization\\
with Interactive Web Visualization}

\author{
  \IEEEauthorblockN{Student ID: 414085193}
  \IEEEauthorblockA{
    Department of [Your Department]\\
    [Your University], Taiwan\\
    Email: [your email]
  }
}

\maketitle

% ── Abstract ──────────────────────────────────────────────
\begin{abstract}
The Vehicle Routing Problem (VRP) is a combinatorial optimization problem
of high practical importance in logistics planning, yet it is NP-hard and
infeasible to solve optimally at scale. This paper presents our study of
PyVRP, a high-performance open-source VRP solver implementing Hybrid Genetic
Search (HGS)---a bio-inspired algorithm combining genetic evolution with
local search. We analyze the algorithmic components of HGS in depth,
including its SREX crossover operator, population diversity management via
Broken Pairs Distance, and adaptive penalty mechanism. Furthermore, we
implement PyVRP-Web, a full-stack web application that exposes the HGS
solver through an interactive browser interface, enabling zero-code problem
definition and real-time geographic route visualization. Benchmark evaluation
shows PyVRP achieves a mean gap of 0.22\% from best-known solutions on 100
CVRP instances, and 0.40\% on 60 VRPTW instances with 1,000 customers. A
real-world case study with 16 Taipei convenience stores validates practical
usability.
\end{abstract}

\begin{IEEEkeywords}
Vehicle Routing Problem, Hybrid Genetic Search, Genetic Algorithm,
Bio-inspired Computing, Web Application, Local Search
\end{IEEEkeywords}

% ── Section I: Introduction ───────────────────────────────
\section{Introduction}

The \textbf{Vehicle Routing Problem (VRP)} is a classical combinatorial
optimization problem with direct applications in last-mile delivery, public
transit, and supply chain management. Given a depot, a fleet of vehicles
with limited capacity, and a set of customers with delivery demands, the VRP
seeks a minimum-cost set of routes such that every customer is served exactly
once and vehicle capacity constraints are satisfied~\cite{toth2014vehicle}.
The VRP with Time Windows (VRPTW) additionally requires each customer to be
served within a specified time interval.

VRP is NP-hard: for a problem with merely 20 customers, the number of
possible route permutations exceeds $2\times10^{18}$, making brute-force
enumeration computationally infeasible. This motivates the use of
\textbf{bio-inspired metaheuristics}---algorithms modeled on natural
processes such as evolutionary selection and genetic recombination---which
trade optimality guarantees for scalability.

This work centers on \textbf{PyVRP}~\cite{wouda2024pyvrp}, a
state-of-the-art solver implementing \textbf{Hybrid Genetic Search (HGS)}:
a framework synergizing Genetic Algorithm (GA) exploration with Local Search
exploitation. PyVRP won the 2021 DIMACS VRPTW Challenge and ranked first in
the EURO meets NeurIPS 2022 competition.

Our contributions are:
\begin{enumerate}
  \item \textbf{Algorithmic Analysis}: A systematic study of HGS components,
    including SREX crossover~\cite{nagata2010memetic}, broken pairs distance
    diversity, and adaptive penalty management.
  \item \textbf{System Implementation}: PyVRP-Web, a full-stack web
    application wrapping HGS in a zero-code interface with real-time map
    visualization.
\end{enumerate}

% ── Section II: Related Work ──────────────────────────────
\section{Related Work}

\subsection{VRP Solver Landscape}

Numerous tools address VRP. \textbf{LKH-3}~\cite{helsgaun2017extension}
transforms VRP into a TSP and applies the Lin-Kernighan heuristic, but is
restricted to academic, non-commercial use. \textbf{OR-Tools}~\cite{ortools}
from Google uses constraint programming and is easy to use but
performs ``far from the state of the art''~\cite{wouda2024pyvrp}.
\textbf{VRPSolver}~\cite{pessoa2020generic} finds exact solutions but
does not scale beyond a few hundred customers.

PyVRP occupies a unique position: near-optimal performance with full Python
customizability under the MIT license.

\subsection{Hybrid Genetic Search}

HGS was introduced by Vidal et al.~\cite{vidal2013hybrid} for a broad class
of VRP variants, maintaining both feasible and infeasible solutions via
dynamic penalty coefficients. Vidal~\cite{vidal2022hybrid} extended HGS-CVRP
with the SWAP* operator and biased fitness criterion. The SREX crossover
operator~\cite{nagata2010memetic} preserves complete sub-routes across
generations, avoiding the quality degradation of naive crossover.

PyVRP~\cite{wouda2024pyvrp} builds on HGS-CVRP by adding VRPTW support,
adopting a Python+C++ hybrid architecture, and robustifying the
implementation.

% ── Section III: Methods ──────────────────────────────────
\section{Methods}

\subsection{Problem Formulation}

The \textbf{CVRP} is defined on a complete directed graph $G=(V,A)$ where
$V=\{0,1,\ldots,n\}$ (0: depot, $1\ldots n$: customers). Customer $i$ has
demand $q_i\geq 0$; each vehicle has capacity $Q$. Objective:
\begin{equation}
  \min \sum_{(i,j)\in A} d_{ij}\,x_{ij}
\end{equation}
subject to every customer visited exactly once, routes starting/ending at
the depot, and total route demand $\leq Q$.

The \textbf{VRPTW} additionally requires service at customer $i$ to begin
within $[e_i, l_i]$, with service duration $s_i$ and travel time $t_{ij}$.

\subsection{Hybrid Genetic Search}

HGS~\cite{wouda2024pyvrp,vidal2013hybrid} combines GA exploration with LS
exploitation. The main loop is outlined in Algorithm~\ref{alg:hgs}.

\begin{algorithm}
\caption{HGS Main Loop}\label{alg:hgs}
\begin{algorithmic}[1]
\State Initialize population $\mathcal{P}$ with $n_{\min}=25$ random solutions
\Repeat
  \State $(p_1, p_2) \leftarrow$ \textsc{TournamentSelect}($\mathcal{P}$)
  \State $c \leftarrow$ \textsc{SREX}$(p_1, p_2)$
  \State $c \leftarrow$ \textsc{LocalSearch}$(c)$
  \If{$\text{rand}() < p_{\text{repair}}$ \textbf{and} infeasible($c$)}
    \State $c \leftarrow$ \textsc{LocalSearch}$(c,\ \alpha\times12,\ \beta\times12)$
  \EndIf
  \State $\mathcal{P} \leftarrow \mathcal{P} \cup \{c\}$
  \If{$|\mathcal{P}| > n_{\min} + n_{\text{gen}}$}
    \State \textsc{SurvivorSelection}($\mathcal{P}$)
  \EndIf
  \State \textsc{UpdatePenalties}($\mathcal{P}$) \Comment{every 50/100 iters}
\Until{stopping criterion met}
\State \Return best feasible solution
\end{algorithmic}
\end{algorithm}

\subsubsection{SREX Crossover}
The Selective Route Exchange operator~\cite{nagata2010memetic} constructs an
offspring by (1) inheriting a subset of complete routes from parent $B$, then
(2) greedily inserting unserved customers guided by parent $A$'s structure.
This preserves entire high-quality sub-routes across generations.

\subsubsection{Local Search}
Local search~\cite{wouda2024pyvrp} accounts for \textbf{80--90\% of runtime}
and is implemented in C++. It operates at two levels:

\textit{Node operators} evaluate moves between customer pairs $(u,v)$ within
the \textbf{granular neighbourhood}~\cite{toth2003granular} of size $k$
(CVRP: $k=20$; VRPTW: $k=40$), reducing complexity from $O(n^2)$ to
$O(kn)$. PyVRP provides 11 operators: $(N,M)$-exchange for
$N\in\{1,2,3\}$, $M\leq N$ (implemented via C++ template specialization),
MoveTwoClientsReversed, and 2-OPT.

\textit{Route operators} evaluate cross-route moves without granularity
restriction: RELOCATE* (best single-customer relocation) and SWAP* (best
customer swap with optimal insertion position, enhanced with time-window
caching and early termination~\cite{wouda2024pyvrp}).

\subsubsection{Population Management and Diversity}
The biased fitness criterion~\cite{vidal2022hybrid} balances quality and
diversity:
\begin{equation}
  f_{\text{biased}}(s)=r_{\text{qual}}(s)\cdot(1-\rho)+r_{\text{div}}(s)\cdot\rho
\end{equation}
where $\rho = n_{\text{elite}}/n_{\min} = 4/25$ and diversity is measured
by \textbf{Broken Pairs Distance}:
\begin{equation}
  \text{BPD}(A,B)=\frac{|P_A \triangle P_B|}{2n},\quad \text{BPD}\in[0,1]
\end{equation}
Survivor selection removes duplicates, then eliminates solutions with
worst biased fitness until the population returns to $n_{\min}=25$.

\subsubsection{Dynamic Penalty Management}
Constraints are soft via penalized cost:
\begin{equation}
  c_{\text{pen}} = d_{\text{total}} + \alpha\,\Delta_{\text{cap}} + \beta\,\Delta_{\text{tw}}
\end{equation}
$\alpha$ and $\beta$ are adjusted every 50 iterations targeting 43\%
feasibility. A repair booster multiplies penalties by 12 when attempting
to recover infeasible offspring.

\subsection{System Architecture: PyVRP-Web}

PyVRP-Web is a four-layer application (Figure~\ref{fig:arch}):
(1) \textit{Presentation}: Vanilla JS + Leaflet.js map;
(2) \textit{API}: FastAPI with Pydantic validation and asyncio.Semaphore(1);
(3) \textit{Service}: WGS84$\to$UTM conversion (pyproj, EPSG:32651),
    neighbourhood tuning ($k=\min(7,n{-}1)$), per-stop timeline reconstruction;
(4) \textit{Engine}: PyVRP v0.5.0 HGS solver.

% ── Figure placeholder ────────────────────────────────────
%\begin{figure}[h]
%  \centering
%  \includegraphics[width=0.48\textwidth]{figures/architecture.png}
%  \caption{PyVRP-Web four-layer system architecture.}
%  \label{fig:arch}
%\end{figure}

% ── Section IV: Results ───────────────────────────────────
\section{Results}

\subsection{Benchmark Performance}

\begin{table}[h]
\caption{CVRP Benchmark Results (X instances, Uchoa et al.~\cite{uchoa2017new})}
\label{tab:cvrp}
\centering
\begin{tabular}{lccc}
\toprule
\textbf{Solver} & \textbf{Mean Cost} & \textbf{Mean Gap} & \textbf{Gap of Mean} \\
\midrule
BKS             & 63,106.7 & 0.00\% & 0.00\% \\
HGS-CVRP~\cite{vidal2022hybrid} & 63,206.1 & 0.11\% & 0.16\% \\
HGS-2012~\cite{vidal2013hybrid} & 63,285.8 & 0.21\% & 0.28\% \\
\textbf{PyVRP~\cite{wouda2024pyvrp}} & \textbf{63,275.5} & \textbf{0.22\%} & \textbf{0.27\%} \\
\bottomrule
\end{tabular}
\end{table}

PyVRP achieves a mean gap of \textbf{0.22\%} from best-known solutions on
100 CVRP instances with 100--1001 customers ($T_{\max}=n\times2.4$\,s,
10 seeds). Multiple instances are solved to \textbf{proven optimality}
(e.g., X-n101-k25, X-n110-k13, X-n115-k10).

\begin{table}[h]
\caption{VRPTW Benchmark Results (H\&G 1000-customer instances~\cite{homberger1999two})}
\label{tab:vrptw}
\centering
\begin{tabular}{lccc}
\toprule
\textbf{Solver} & \textbf{Mean Cost} & \textbf{Mean Gap} & \textbf{Gap of Mean} \\
\midrule
BKS              & 33,143.8 & 0.00\% & 0.00\% \\
HGS-DIMACS~\cite{kool2022hybrid} & 33,265.5 & 0.32\% & 0.37\% \\
\textbf{PyVRP~\cite{wouda2024pyvrp}} & \textbf{33,296.4} & \textbf{0.40\%} & \textbf{0.46\%} \\
\bottomrule
\end{tabular}
\end{table}

On 60 VRPTW instances (2-hour time limit, 10 seeds), PyVRP achieves
\textbf{0.40\%} mean gap---equivalent to a \textbf{2nd-place rank} in the
DIMACS VRPTW competition. Extended runs improved \textbf{27 of 300}
best-known solutions across the full H\&G benchmark set.

\subsection{System Demonstration}

We validate PyVRP-Web on a real-world case: \textbf{Taipei 7-ELEVEN daytime
distribution}. Setup: 1 depot (Taipei Distribution Center), 16 stores
(time windows 10:00--13:00), 2 large trucks (capacity 140) + 4 medium
trucks (capacity 80), speed 28\,km/h.

Results (Figure~\ref{fig:demo}): a feasible plan found in $\approx$8\,s;
\textbf{3 routes}, total distance $\approx$92\,km. The algorithm naturally
clusters geographically proximate stores---northern (Shilin, Beitou),
central (Da'an, Songshan), and southwestern (Banqiao, Wenshan) districts.

%\begin{figure}[h]
%  \centering
%  \includegraphics[width=0.48\textwidth]{figures/taipei_demo_result.png}
%  \caption{PyVRP-Web route visualization for the Taipei 7-ELEVEN
%           daytime case study (16 stores, 3 routes, 92\,km).}
%  \label{fig:demo}
%\end{figure}

% ── Section V: Conclusion ─────────────────────────────────
\section{Conclusion}

This paper presented a comprehensive study of Hybrid Genetic Search, a
state-of-the-art bio-inspired algorithm for VRP, and its implementation in
PyVRP. We analyzed the biological analogy underlying HGS: SREX crossover
mimics chromosomal recombination, biased fitness implements natural selection
with a diversity premium, and dynamic penalties act as environmental pressure
steering the population toward feasibility.

PyVRP-Web demonstrates that research-grade bio-inspired optimization can be
made accessible via modern web technologies, achieving near-optimal routing
within seconds for practical problem sizes (0.22\% from BKS on CVRP). Future
directions include integrating real road networks (OSRM), multi-depot VRP
support, and real-time GA convergence visualization.

% ── References ────────────────────────────────────────────
\bibliographystyle{IEEEtran}
\bibliography{references}

\end{document}
```

---

## references.bib

```bibtex
@article{wouda2024pyvrp,
  author  = {Wouda, Niels A. and Lan, Leon and Kool, Wouter},
  title   = {{PyVRP}: a high-performance {VRP} solver package},
  journal = {INFORMS Journal on Computing},
  volume  = {36},
  number  = {4},
  pages   = {943--955},
  year    = {2024},
  note    = {arXiv:2403.13795}
}

@article{vidal2013hybrid,
  author  = {Vidal, Thibaut and Crainic, Teodor Gabriel and Gendreau, Michel and Prins, Christian},
  title   = {A hybrid genetic algorithm with adaptive diversity management for a large class of vehicle routing problems with time-windows},
  journal = {Computers \& Operations Research},
  volume  = {40},
  number  = {1},
  pages   = {475--489},
  year    = {2013}
}

@article{vidal2022hybrid,
  author  = {Vidal, Thibaut},
  title   = {Hybrid genetic search for the {CVRP}: open-source implementation and {SWAP*} neighborhood},
  journal = {Computers \& Operations Research},
  volume  = {140},
  pages   = {105643},
  year    = {2022}
}

@inproceedings{nagata2010memetic,
  author    = {Nagata, Yuichi and Kobayashi, Shigenobu},
  title     = {A memetic algorithm for the pickup and delivery problem with time windows using selective route exchange crossover},
  booktitle = {Parallel Problem Solving from Nature -- PPSN XI},
  pages     = {536--545},
  year      = {2010},
  publisher = {Springer}
}

@article{toth2003granular,
  author  = {Toth, Paolo and Vigo, Daniele},
  title   = {The granular tabu search and its application to the vehicle-routing problem},
  journal = {INFORMS Journal on Computing},
  volume  = {15},
  number  = {4},
  pages   = {333--346},
  year    = {2003}
}

@article{uchoa2017new,
  author  = {Uchoa, Eduardo and Pecin, Diego and Pessoa, Artur and Poggi, Marcus and Vidal, Thibaut and Subramanian, Anand},
  title   = {New benchmark instances for the capacitated vehicle routing problem},
  journal = {European Journal of Operational Research},
  volume  = {257},
  number  = {3},
  pages   = {845--858},
  year    = {2017}
}

@article{homberger1999two,
  author  = {Homberger, J{\"o}rg and Gehring, Hermann},
  title   = {Two evolutionary metaheuristics for the vehicle routing problem with time windows},
  journal = {INFOR: Information Systems and Operational Research},
  volume  = {37},
  number  = {3},
  pages   = {297--318},
  year    = {1999}
}

@techreport{kool2022hybrid,
  author      = {Kool, Wouter and Juninck, Joep O. and Roos, Ernst and Cornelissen, Kamiel and Agterberg, Pieter and van Hoorn, Jasper and Visser, Thomas},
  title       = {Hybrid Genetic Search for the Vehicle Routing Problem with Time Windows: a High-Performance Implementation},
  institution = {ORTEC},
  year        = {2022}
}

@misc{ortools,
  author       = {Perron, Laurent and Furnon, Vincent},
  title        = {{OR-Tools}},
  howpublished = {Google LLC},
  year         = {2022},
  url          = {https://developers.google.com/optimization/}
}

@book{toth2014vehicle,
  editor    = {Toth, Paolo and Vigo, Daniele},
  title     = {Vehicle Routing: Problems, Methods, and Applications},
  edition   = {2nd},
  publisher = {Society for Industrial and Applied Mathematics},
  address   = {Philadelphia, PA},
  year      = {2014}
}

@techreport{helsgaun2017extension,
  author      = {Helsgaun, Keld},
  title       = {An Extension of the {Lin-Kernighan-Helsgaun TSP} Solver for Constrained Traveling Salesman and Vehicle Routing Problems},
  institution = {Roskilde University},
  year        = {2017}
}

@article{pessoa2020generic,
  author  = {Pessoa, Artur and Sadykov, Ruslan and Uchoa, Eduardo and Vanderbeck, Fran{\c{c}}ois},
  title   = {A generic exact solver for vehicle routing and related problems},
  journal = {Mathematical Programming},
  volume  = {183},
  pages   = {483--523},
  year    = {2020}
}
```
