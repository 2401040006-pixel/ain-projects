# Project 08 — Smart Team Formation Optimizer

## 1. Problem Description

Local Search algorithms in Artificial Intelligence (AI) explore large combinatorial state spaces where systematic exhaustive search is computationally intractable. Rather than retaining systematic search paths from a root node, local search operates iteratively on complete candidate configurations, evaluating neighborhood perturbations via an explicit scalar objective function to navigate rugged landscapes toward global or near-optimal solutions.

This project addresses team formation for collaborative coursework projects. Given a cohort of 60 synthetic students (seed 42), the optimization objective partitions students into teams of 3 to 4 members while optimizing four competing criteria:

1. **Skill Balance**: Minimizing cross-team variance in composite technical capabilities (Programming, Mathematics, Presentation).
2. **Schedule Alignment**: Minimizing meeting conflicts by maximizing shared weekly free intervals (Monday–Saturday).
3. **Role Diversity**: Ensuring each team possesses complementary roles (`Leader`, `Coder`, `Researcher`, `Presenter`).
4. **Team Size Penalty**: Penalizing deviations from the target group size bounds (3–4 members).

Students must formulate a scalar loss objective $J$, analyze the pathology of local optima trapping greedy Hill-Climbing search, and implement stochastic metaheuristics like Simulated Annealing (SA) to escape suboptimal plateaus. All student records are strictly synthetic educational datasets.

---

## 2. Provided Materials & Starter Resources

The project package provides cohort configurations, benchmark scenario weights, synthetic student datasets, and an interactive Streamlit application.

### File Structure
```text
project-08-team-formation/
├── data/
│   ├── README.md                      # Data dictionary, field specifications, and penalty formalisms
│   ├── config.json                    # Team size bounds, role taxonomies, and objective term labels
│   ├── scenarios.json                 # Benchmark fixtures (P08-SKILL-PRIORITY to P08-HC-LOCAL-OPTIMUM)
│   ├── students_seed42.csv            # 60 synthetic student profile records (seed 42)
│   └── SHA256SUMS                     # Cryptographic checksums ensuring byte-for-byte reproducibility
├── scripts/
│   └── generate_students.py           # Configurable synthetic cohort generator with random seed control
├── starter/
│   ├── loader.py                      # CSV/JSON loaders, student dictionary parsers, and random baseline
│   ├── student_core.py                # Algorithmic stubs for multi-criteria objective and local search
│   └── app.py                        # Streamlit team partitioning and diagnostic dashboard
├── tests/
│   └── test_project_08_sanity.py      # Unit tests validating cohort properties and interface contracts
└── requirements.txt                   # Pinned Python package dependencies (including streamlit)
```

### Starter Infrastructure vs. Student Implementation
The module `starter/loader.py` provides dataset deserialization and a naive stochastic baseline (`random_baseline`). The module `starter/app.py` renders an interactive dashboard displaying team composition metrics. Students implement the optimization engine in `starter/student_core.py`, specifically: the weighted objective function (`objective`), steepest-ascent or first-choice Hill Climbing (`hill_climbing`), and Simulated Annealing with an explicit geometric cooling schedule (`simulated_annealing`). Third-party optimization libraries (e.g., SciPy, OR-Tools) and Large Language Model (LLM) APIs are strictly prohibited.

### Installation and Execution
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run starter/app.py
```

---

## 3. Requirements & Deliverables

### 3.1 Midterm Milestone — AI Core
- **Algorithmic Implementation**: Construct an optimization core from first principles in `starter/student_core.py`. Define the scalar cost function:
  $$J = w_1 \cdot \text{SkillImbalance} + w_2 \cdot \text{ScheduleConflict} + w_3 \cdot \text{RoleImbalance} + w_4 \cdot \text{TeamSizePenalty}$$
  Implement `hill_climbing` using 1-for-1 or 2-for-2 student swaps between teams. Implement `simulated_annealing` using the Metropolis acceptance criterion $P(\text{accept}) = \exp(-\Delta J / T)$ with a documented cooling schedule (e.g., $T_k = T_0 \cdot \alpha^k$).
- **Mandatory Controlled Experiment**: Execute an empirical trade-off analysis using `P08-WEIGHT-TRADEOFF` from `data/scenarios.json`. Alter weight priorities (e.g., heavily weighting schedule alignment versus skill variance) and evaluate Pareto trade-offs. Furthermore, initialize search from the verified local optimum fixture `P08-HC-LOCAL-OPTIMUM`, demonstrating that Hill Climbing becomes trapped in a suboptimal state while Simulated Annealing stochastically escapes to a lower global cost.
- **Deliverables**: Fully implemented `student_core.py`, empirical optimization scripts/notebooks, and an oral presentation slide deck (`presentation.pdf`).
- **Grading Criteria**: Mathematical formulation of objective terms and search correctness (15 pts); local-optimum escape analysis and weight trade-off rigor (10 pts); oral defense and live team partitioning demo (15 pts). Total: 40 points (40% weight).

### 3.2 Final Milestone — AI Product
- **Interactive Application**: Package the team optimization engine into an interactive Streamlit dashboard. The application must support: uploading custom synthetic cohorts; interactive sliders for team sizes (3–4) and objective weights ($w_1, w_2, w_3, w_4$); side-by-side visual comparisons against the random baseline; team radar/bar charts showing skill distributions and meeting compatibility matrices; and convergence curves plotting loss $J$ over iteration steps.
- **Stress & Edge Scenarios**: Demonstrate search convergence and robust team partitioning across all four benchmark profiles in `data/scenarios.json`: skill-dominant weighting (`P08-SKILL-PRIORITY`), schedule-dominant weighting (`P08-SCHEDULE-PRIORITY`), role-dominant weighting (`P08-ROLE-PRIORITY`), and local-optimum escape (`P08-HC-LOCAL-OPTIMUM`).
- **Deliverables**: Functional Streamlit web product, clean GitHub repository, and an IEEE-formatted engineering technical report (`report.pdf`).
- **Grading Criteria**: User interface aesthetics, visual analytics clarity, and real-time responsiveness (25 pts); technical report mathematical rigor and empirical convergence analysis (15 pts); oral defense against complex weight constraints (10 pts). Total: 50 points (50% weight).

---

## 4. References

- [1] S. Kirkpatrick, C. D. Gelatt, and M. P. Vecchi, "Optimization by simulated annealing," *Science*, vol. 220, no. 4598, pp. 671–680, 1983, doi: 10.1126/science.220.4598.671.
- [2] S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed. Hoboken, NJ, USA: Pearson, 2020, pp. 120–145.
- [3] V. Cerny, "Thermodynamical approach to the traveling salesman problem: An efficient simulation algorithm," *Journal of Optimization Theory and Applications*, vol. 45, no. 1, pp. 41–51, 1985, doi: 10.1007/BF00940812.
