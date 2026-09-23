# Project 01 — Smart Campus Route Planner

## 1. Problem Description

Navigating a modern multi-building campus requires routing algorithms that handle real-world layout constraints, accessibility needs, and dynamic path obstructions. In this project students formulate campus navigation as a state-space graph search problem: given a weighted graph of campus locations and connections, an automated planner must find optimal or near-optimal routes between arbitrary landmarks while accommodating temporarily blocked pathways and step-free accessibility requirements.

The core challenge is to implement and evaluate classical graph search algorithms from first principles—comparing uninformed baselines against informed heuristic search—and to analyse trade-offs in search effort, memory footprint, and path cost optimality across a realistic set of navigation scenarios.

---



## 2. Provided Materials & Starter Resources

The project graph models a generic multi-building campus with **54 nodes** and **75 bidirectional edges** annotated with distance, travel time, crowd level, and accessibility attributes.

### File Structure

```text
project-01-campus-route/
├── data/
│   ├── nodes.csv          # Node coordinates (x, y, floor), building names, type
│   ├── edges.csv          # Connectivity, distance (m), travel time (s), stairs, accessible flag
│   ├── scenarios.json     # Evaluation scenarios (normal, blocked edges, accessible routing)
│   ├── campus_map.png     # 2D schematic of the campus layout
│   ├── SHA256SUMS         # Cryptographic checksums
│   └── README.md          # Data dictionary
├── starter/
│   ├── graph.py           # Graph data structures and loader (provided; do not modify)
│   ├── student_core.py    # Algorithmic stubs — implement here
│   └── app.py             # Streamlit interface (provided; do not modify)
├── tests/
│   └── test_project_01_sanity.py
└── requirements.txt
```



### Starter Infrastructure vs. Student Implementation

`starter/graph.py` provides graph loading, neighbour queries, and property lookups. `starter/app.py` renders the campus schematic and path overlays. Students implement all AI logic in `starter/student_core.py`.

### Installation and Execution

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run starter/app.py
```

---



## 3. Requirements & Deliverables



### 3.1 Midterm Milestone — AI Core

- **Implement**: `bfs`, `greedy`, `astar`, `euclidean_heuristic`, and `manhattan_heuristic` in `starter/student_core.py` from scratch. External graph search solvers (e.g., NetworkX search) are prohibited.
- **Experiment**: Run all scenarios in `data/scenarios.json` and compare BFS, GBFS, and A* on (i) nodes expanded, (ii) peak frontier size, (iii) path cost, and (iv) runtime. Formally prove heuristic admissibility ($h(n) \le h^*(n)$) and consistency ($h(n) \le c(n,a,n') + h(n')$).
- **Deliverables**: Completed `student_core.py`, evaluation notebook or script, `presentation.pdf`.
- **Grading Criteria**: Problem formulation and algorithmic correctness (15 pts); experimental rigour and heuristic analysis (10 pts); oral defence and live demo (15 pts). **Total: 40 pts.**



### 3.2 Final Milestone — AI Product

- **Interactive Application**: Streamlit app where users select start and end landmarks, toggle accessible-only routing, dynamically block paths to simulate maintenance, and compare algorithm routes side-by-side.
- **Stress Scenarios**: Demonstrate path recalculation after primary corridors are blocked; correctly detect and report no-path cases without crashing.
- **Deliverables**: Fully operational local web application, GitHub repository, `report.pdf` (IEEE format).
- **Grading Criteria**: Product functionality, UX, and UI integration (25 pts); technical report depth and architectural documentation (15 pts); live defence under stress scenarios (10 pts). **Total: 50 pts.**

---



## 4. References

- [1] S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed. Hoboken, NJ, USA: Pearson, 2020, pp. 63–102.
- [2] P. E. Hart, N. J. Nilsson, and B. Raphael, "A formal basis for the heuristic determination of minimum cost paths," *IEEE Transactions on Systems Science and Cybernetics*, vol. 4, no. 2, pp. 100–107, Jul. 1968, doi: 10.1109/TSSC.1968.300136.
- [3] J. Pearl, *Heuristics: Intelligent Search Strategies for Computer Problem Solving*. Reading, MA, USA: Addison-Wesley, 1984, pp. 33–72.

