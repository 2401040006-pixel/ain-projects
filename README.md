# Artificial Intelligence — Semester Projects

## 1. Overview and Pedagogical Framework

This repository provides twelve self-contained project packages for an **Artificial Intelligence** course.

The curriculum follows the foundational core of artificial intelligence as formalized by Russell and Norvig [1] and aligns with the seven knowledge domains of Harvard University's CS50's Introduction to Artificial Intelligence with Python [2]:

1. **Search**: State-space graphs, uninformed search, informed heuristic search, and adversarial games.
2. **Knowledge**: Propositional and first-order logic, inference engines, and rule-based expert systems.
3. **Uncertainty**: Probability theory, Bayesian Networks (BN), and temporal Hidden Markov Models (HMM).
4. **Optimization**: Constraint Satisfaction Problems (CSP), backtracking heuristics, and local search algorithms.
5. **Learning**: Supervised machine learning, tabular reinforcement learning, and Markov Decision Processes (MDP).
6. **Neural Networks**: Deep learning fundamentals, convolutional architectures, and transfer learning.
7. **Language**: Natural language processing, vector space models, intent classification, and information retrieval.

### Core Pedagogical Boundaries

- **Autonomous Algorithmic Implementation**: In the Midterm milestone, students implement the assigned artificial intelligence core algorithms from first principles in Python 3.11.
- **Offline and Self-Contained Execution**: All projects run locally on `localhost`. Using hosted commercial Large Language Model (LLM) APIs to substitute for required core algorithmic logic is strictly forbidden.
- **Curated Educational Resources**: Students do not need to collect external data. Each project directory provides synthetic datasets, environment simulators, verified test fixtures, and starter application skeletons.

---

## 2. Repository Architecture

```text
semester-ai-projects/
├── .gitignore
├── .python-version
├── .streamlit/config.toml              # Shared Streamlit theme for starter apps
├── README.md                           # This document
│
├── project-01-campus-route/            # Graph search & campus wayfinding
├── project-02-board-game/              # Adversarial search & Connect Four
├── project-03-academic-advisor/        # Knowledge representation & degree audit
├── project-04-it-expert-system/        # Rule-based diagnostic expert system
├── project-05-bayesian-student/        # Bayesian Networks & academic outcomes
├── project-06-hmm-traffic/             # Hidden Markov Models & crowd estimation
├── project-07-timetable/               # Constraint satisfaction & scheduling
├── project-08-team-formation/          # Local search & team partitioning
├── project-09-delivery-agent/          # Reinforcement learning & grid delivery
├── project-10-ticket-router/           # Text classification & ticket routing
├── project-11-waste-classifier/        # Convolutional networks & waste sorting
└── project-12-campus-faq/              # Information retrieval & FAQ assistant
```

Each project folder contains:

- `README.md`: Problem definition, provided resources, midterm and final requirements, grading criteria, and references.
- `data/` or `environment/`: Pre-processed datasets, configuration files, and problem instances.
- `starter/`: Data loaders, GUI skeletons, and empty core algorithm stubs.
- `tests/`: Automated sanity tests for data schema and stub signatures.
- `requirements.txt`: Pinned Python dependencies.

Most projects place the graded core in `starter/student_core.py`. Project 06 uses `starter/traffic_core.py` instead.

---

## 3. The Twelve Semester Projects Matrix

| ID     | Project Title                  | Primary AI Domain         | Core Algorithms & Techniques                                                        | Dataset & Environment                                  | Setting                                                                              |
| ------ | ------------------------------ | ------------------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------------ |
| **01** | **Campus Route Planner**       | Search & Optimization     | Breadth-First Search (BFS), Greedy Best-First Search (GBFS), A\* Search             | 54 nodes, 75 edges campus graph                        | Multi-building campus navigation with accessibility and blocked-path constraints     |
| **02** | **Board Game Arena**           | Adversarial Search        |Minimax Algorithm, Alpha-Beta Pruning, Static Board Evaluation|Deterministic 6×7 Connect Four engine| Two-player Connect Four arena with human vs AI and AI vs AI modes                    |
| **03** |**Academic Advisor**|Knowledge Representation| Propositional Logic, Knowledge Base Entailment, Model Checking                      | Curated degree rules, 12 mandatory courses             | Course eligibility and graduation audit over synthetic transcripts                   |
| **04** | **IT Expert System**           | Knowledge Engineering     | Rule-Based Forward Chaining, Explanation Facility Generation                        | 27 symptoms, 14 causes, 48 inference rules             | Campus IT helpdesk diagnosis across Wi-Fi, LMS, labs, accounts, and printers         |
| **05** | **Bayesian Student Simulator** | Uncertainty & Probability | Bayesian Networks (BN), Conditional Probability Tables (CPT), Enumeration Inference | Synthetic academic causal Directed Acyclic Graph (DAG) | Probabilistic prediction of academic performance under uncertainty                   |
| **06** | **Campus Crowd Estimator**     | Temporal Uncertainty      | Hidden Markov Models (HMM), Forward Algorithm, Viterbi Algorithm                    | Corrupted sensor sequence streams (5%–30% noise)       | Real-time corridor crowd-density estimation from noisy sensors                       |
|**07**|**Timetable Scheduler**|Constraint Satisfaction|Constraint Satisfaction Problems (CSP), Backtracking Search, MRV Heuristic| 4 problem instances (feasible, restricted, unsat)      | Weekly lecture and laboratory classroom scheduling                                   |
| **08** |**Smart Team Formation**|Local Search Optimization| Hill-Climbing Search (HC), Simulated Annealing (SA), Multi-Criteria Objective       | 60 synthetic student profiles (seed 42)                | Balanced 3–4 student team allocation by skills, roles, and schedules                 |
| **09** | **Autonomous Delivery Agent**  | Reinforcement Learning    | Markov Decision Processes (MDP), Tabular Q-Learning, Epsilon-Greedy Exploration     | 2D GridWorld simulator with obstacles and hazards      | Package delivery between office and labs while avoiding danger cells                 |
| **10** |**IT Ticket Router**|Machine Learning & NLP| Bag-of-Words (BoW), TF-IDF, Naive Bayes Classifier, Support Vector Machines (SVM)   | 3,000 synthetic helpdesk tickets across 6 classes      | Automated categorization of English IT support tickets                               |
| **11** | **Visual Waste Sorting**       | Deep Learning & Vision    | Convolutional Neural Networks (CNN), Max Pooling, Transfer Learning / Fine-Tuning   | Pinned TrashNet dataset (2,527 images, 6 classes)      | Visual waste classification for campus recycling bins                                |
| **12** | **Campus FAQ Assistant**       | Information Retrieval     | Vector Space Model (VSM), TF-IDF Cosine Similarity, Intent Classification           | 112 synthetic handbook articles & notices              | Automated query answering with abstention for student handbook FAQs                  |

---

## 4. Getting Started

### 4.1 System Prerequisites

- Operating System: Linux, macOS, or Windows 10/11 with PowerShell.
- Python Version: **Python 3.11** (verified via `python3.11 --version`).

### 4.2 Setting Up the Virtual Environment

Open a terminal in the root of this repository and execute:

```bash
# Create a Python 3.11 virtual environment
python3.11 -m venv .venv

# Activate the virtual environment
# On macOS / Linux:
source .venv/bin/activate
# On Windows (PowerShell):
# .venv\Scripts\Activate.ps1

# Upgrade pip package installer
pip install --upgrade pip
```

### 4.3 Installing Project Dependencies

Navigate into your assigned project directory and install its dependencies:

```bash
cd project-01-campus-route  # Replace with your assigned project directory
pip install -r requirements.txt
```

### 4.4 Running the Local Application

Every project provides an interactive local interface powered by Streamlit, except Project 02, which uses Pygame:

```bash
# For Streamlit projects (Projects 01, 03-12), run from the repository root
# so the shared .streamlit/config.toml theme is applied:
streamlit run project-01-campus-route/starter/app.py

# Or from inside a project folder:
streamlit run starter/app.py

# For Pygame (Project 02):
python starter/app.py
```

### 4.5 Executing Automated Sanity Tests

```bash
# Run tests for your specific project
pytest project-01-campus-route/tests/ -v

# Run the complete suite across all twelve projects (from repository root)
pytest -v
```

---

## 5. Development Milestones and Submission

Each assigned group develops their project through two synchronized milestones:

1. **Midterm Milestone — AI Core (40% Course Weight)**:

- Formulate the problem mathematically and implement the core algorithm from first principles in `starter/student_core.py` (or `starter/traffic_core.py` for Project 06).
- Conduct the mandatory controlled experiment described in your project README, comparing performance against a baseline.
- Deliverables: Codebase, executable experimental scripts, PDF slide deck, and an in-class oral presentation with live algorithmic demonstration.

2. **Final Milestone — AI Product (50% Course Weight)**:

- Integrate the validated AI core into a functional, user-friendly local application.
- Address stress scenarios and failure cases gracefully.
- Deliverables: Runnable software, academic technical report (`report.pdf`), GitHub repository, and oral defense.

_(Comprehensive grading rubrics and assessment criteria are maintained by the course instructors in the separate course policy documentation)._

---

## 6. Academic References

- [1] S. Russell and P. Norvig, _Artificial Intelligence: A Modern Approach_, 4th ed. Hoboken, NJ, USA: Pearson, 2020.
- [2] D. J. Malan and B. Yu, "CS50's Introduction to Artificial Intelligence with Python," Harvard University, Cambridge, MA, USA, 2024. [Online]. Available: [https://cs50.harvard.edu/ai/](https://cs50.harvard.edu/ai/)
- [3] IEEE Standards Association, _IEEE Standard for Developing Software Project Management Plans_, IEEE Std 1058-1998, 1998.
