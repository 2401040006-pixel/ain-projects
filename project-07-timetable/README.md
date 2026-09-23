# Project 07 — Timetable Scheduler

## 1. Problem Description

Combinatorial optimization is a crucial application area in Artificial Intelligence (AI), specifically in transforming high-dimensional operational planning challenges into formal Constraint Satisfaction Problems (CSPs). A CSP is defined mathematically by a triplet $\langle X, D, C \rangle$, where $X$ is a set of variables, $D$ is a set of corresponding value domains, and $C$ is a set of constraints restricting allowable variable-value assignments.

This project addresses the academic course scheduling problem for a campus department. A scheduler must assign each course offering into an admissible triple:
$$\text{Assignment}(c) = (\text{lecturer}_i, \text{room}_j, \text{timeslot}_k)$$

The search space is bounded by hard constraints:
1. **Room Conflict**: No room may host more than one course during the same timeslot.
2. **Lecturer Conflict**: No lecturer may be scheduled to teach two distinct courses concurrently.
3. **Cohort Conflict**: Students belonging to the same cohort cannot be enrolled in overlapping sessions.
4. **Room Suitability and Capacity**: Laboratory sessions must be assigned to rooms with sufficient capacity and equipment.
5. **Lecturer Availability**: Instructors may only be assigned during declared availability windows.

Students must formulate the scheduling problem as a CSP and implement systematic search algorithms from first principles to locate consistent timetables or conclusively prove unsatisfiability.

---

## 2. Provided Materials & Starter Resources

The project package provides benchmark curriculum instances, room capacity profiles, validation harnesses, and an interactive Streamlit visualization interface.

### File Structure
```text
project-07-timetable/
├── data/
│   ├── README.md                          # Data dictionary and constraint formalisms
│   ├── instance_feasible/                 # Standard tractable benchmark (courses, rooms, timeslots)
│   ├── instance_restricted_rooms/         # Reduced room availability stress benchmark
│   ├── instance_extra_lecturer/           # Same resources plus an extra lecturer hard constraint
│   └── instance_unsat/                    # Provably unsatisfiable overconstrained fixture
├── starter/
│   ├── loaders.py                         # CSV/JSON instance loaders, domain generator, and validator
│   ├── student_core.py                    # Algorithmic stubs for CSP backtracking and heuristics
│   └── app.py                            # Streamlit timetable grid visualization dashboard
├── tests/
│   └── test_project_07_sanity.py          # Unit tests verifying instance integrity and constraint checks
└── requirements.txt                       # Pinned Python package dependencies (including streamlit)
```

### Starter Infrastructure vs. Student Implementation
The module `starter/loaders.py` provides candidate domain generation (`candidate_domain`) and hard constraint verification (`validate_assignment`). The module `starter/app.py` renders interactive weekly schedule grids. Students implement the core search solver in `starter/student_core.py`, specifically: backtracking search (`solve_csp(instance, strategy)`) supporting both naive and heuristic ordering, and optional soft constraint evaluation (`soft_constraint_score`). Commercial or third-party CSP solvers (e.g., `python-constraint`, OR-Tools) and Large Language Model (LLM) APIs are strictly forbidden.

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
- **Algorithmic Implementation**: Construct a systematic CSP backtracking search engine from first principles in `starter/student_core.py`. Implement `solve_csp(instance, strategy)` supporting two search strategies: (i) a baseline naive chronological backtracking search without heuristics, and (ii) an advanced heuristic strategy incorporating variable ordering (Minimum Remaining Values (MRV) or Degree Heuristic) and inference pruning (Forward Checking (FC) or Arc Consistency Algorithm #3 (AC-3)).
- **Mandatory Controlled Experiment**: Conduct an empirical comparative benchmark across all four provided instances (`instance_feasible`, `instance_restricted_rooms`, `instance_extra_lecturer`, and `instance_unsat`). Measure and report: search runtime (wall-clock milliseconds), total nodes explored, and solution validity. Quantify the speedup and node-reduction ratio of the heuristic over naive backtracking, and specifically analyze proof-of-unsatisfiability behavior on `instance_unsat`.
- **Deliverables**: Completed `student_core.py`, empirical performance benchmark scripts, and an oral presentation slide deck (`presentation.pdf`).
- **Grading Criteria**: CSP formalization and search correctness (15 pts); heuristic efficiency and unsatisfiability proof analysis (10 pts); oral defense and live schedule search demonstration (15 pts). Total: 40 points (40% weight).

### 3.2 Final Milestone — AI Product
- **Interactive Application**: Package the scheduler into an interactive Streamlit web dashboard. The system must feature: dynamic instance loading; selectable solver strategy toggles (`naive` vs. `heuristic`); interactive visual calendar grids color-coded by lecturer, room, and cohort; explicit constraint violation monitors; and instant diagnostic reporting when an instance is provably unsatisfiable.
- **Stress & Edge Scenarios**: Demonstrate that `instance_unsat` returns `None` without infinite looping or memory faults, and verify scalability and correctness on `instance_feasible`, `instance_restricted_rooms`, and `instance_extra_lecturer`.
- **Deliverables**: Operational Streamlit web product, clean GitHub repository, and an IEEE-formatted engineering technical report (`report.pdf`).
- **Grading Criteria**: User interface ergonomics, timetable grid clarity, and solver reactivity (25 pts); technical report mathematical rigor, CSP proofs, and heuristic analysis (15 pts); oral defense against complex schedule modifications (10 pts). Total: 50 points (50% weight).

---

## 4. References

- [1] R. Dechter, *Constraint Processing*. San Francisco, CA, USA: Morgan Kaufmann, 2003.
- [2] S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed. Hoboken, NJ, USA: Pearson, 2020, pp. 180–207.
- [3] E. Tsang, *Foundations of Constraint Satisfaction*. London, UK: Academic Press, 1993.
