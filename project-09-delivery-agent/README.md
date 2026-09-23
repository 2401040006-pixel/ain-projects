# Project 09 — Autonomous Campus Delivery Agent

## 1. Problem Description

Reinforcement Learning (RL) is a subfield of Artificial Intelligence (AI) where an autonomous agent learns optimal behavioral policies through sequential trial-and-error interactions with an environment. The foundational mathematical model is the Markov Decision Process (MDP), formalized by the tuple $\langle S, A, P, R, \gamma \rangle$, representing the state space, action space, transition probability dynamics, scalar reward signals, and temporal discount factor.

This project simulates an autonomous indoor delivery robot navigating a discrete grid world that represents the corridors and rooms of a campus building. The robot picks up packages from a designated office (`PICKUP`) and transports them to one of the computer lab destinations (`GOAL`), while avoiding structural obstacles (`WALL`) and hazardous zones such as wet floors or restricted maintenance areas (`DANGER`).

**Grid legend** — cell types and their map symbols:

| Symbol | Cell Type | Meaning |
|--------|-----------|---------|
| `S` | `START` | Robot's initial spawn position |
| `P` | `PICKUP` | Package collection point (office) |
| `G` | `GOAL` | Delivery destination (lab) |
| `D` | `DANGER` | Hazardous zone (penalty) |
| `#` | `WALL` | Impassable obstacle |
| `@` | — | Current agent position (runtime overlay) |

The state space is defined as $s = (r, c, p) \in \mathcal{S}$, tracking the robot's row coordinate, column coordinate, and package carriage status ($p \in \{\text{True}, \text{False}\}$). The robot executes directional moves $a \in \{\text{UP}, \text{DOWN}, \text{LEFT}, \text{RIGHT}\}$. Students must formulate tabular Q-learning from first principles, balance exploration versus exploitation, investigate reward hacking, and converge toward safe, cost-minimal navigation policies.

---

## 2. Provided Materials & Starter Resources

The project package provides a deterministic grid simulation engine, multi-difficulty navigation maps, reward presets, and an interactive Streamlit dashboard.

### File Structure
```text
project-09-delivery-agent/
├── environment/
│   ├── gridworld.py              # Grid world simulator: state transitions, bounds, and cell types
│   ├── config.json               # Action definitions and reward presets (default, bad_reward, improved_reward)
│   └── maps/                     # Floor plans: easy.json (open), medium.json (hazard), hard.json (maze)
├── data/
│   └── scenarios.json            # Benchmark test fixtures (N1, D1/D2 hazard routes, F1, X1 reward hack)
├── starter/
│   ├── visualization.py          # Matplotlib grid and policy vector rendering utilities
│   ├── student_core.py           # Algorithmic stubs: select_action and q_learning
│   └── app.py                    # Streamlit interactive learning and execution dashboard
├── tests/
│   └── test_project_09_sanity.py # Unit tests validating transitions, reward signals, and stub interfaces
└── requirements.txt              # Pinned Python package dependencies (including streamlit, matplotlib)
```

### Starter Infrastructure vs. Student Implementation
`environment/gridworld.py` governs environment resets, step transitions, and reward evaluations. `starter/app.py` renders interactive grid updates under a baseline random policy. Students implement the learning core in `starter/student_core.py`:

- **`select_action(state, q_table, actions, epsilon)`** — executes uniform random exploration with probability $\epsilon$ and greedy exploitation of maximal Q-values otherwise.
- **`q_learning(env, episodes, alpha, gamma, epsilon)`** — runs the full training loop applying the Bellman temporal-difference update.

Shipping pre-trained Q-tables (`.pkl`, `.json`), deep RL libraries, and external LLM APIs is strictly prohibited.

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
- **Algorithmic Implementation**: Implement tabular Q-learning in `starter/student_core.py`. `select_action` must perform $\epsilon$-greedy selection. `q_learning` must apply the Bellman optimality update:
  $$Q(s, a) \leftarrow Q(s, a) + \alpha \left( r + \gamma \max_{a'} Q(s', a') - Q(s, a) \right)$$
- **Mandatory Controlled Experiment**: Run a hyperparameter ablation varying at least two of: learning rate $\alpha$, discount factor $\gamma$, exploration decay $\epsilon$, and reward preset (`default`, `bad_reward`, `improved_reward`). Plot episodic return curves, measure convergence speed, and document the pathology of reward hacking under `bad_reward` (e.g., the agent avoiding pickups or looping to exploit step rewards).
- **Deliverables**: Implemented `student_core.py`, training notebooks/scripts, and `presentation.pdf`.
- **Grading**: MDP formulation and Q-learning correctness (15 pts); ablation depth and reward-hacking analysis (10 pts); oral defense with live policy execution (15 pts). **Total: 40 pts.**

### 3.2 Final Milestone — AI Product
- **Interactive Application**: Package the trained agent into a Streamlit simulation. Required features: map selection (`easy` / `medium` / `hard`); hyperparameter sliders ($\alpha, \gamma, \epsilon$); real-time episodic reward plots; Q-value heatmaps and policy-arrow overlays; live playback comparing the trained agent to a random baseline.
- **Stress & Edge Scenarios**: Demonstrate policy robustness on all five benchmark scenarios from `data/scenarios.json`: standard open-layout delivery (`N1`), hazard-zone avoidance (`D1`, `D2`), forced-pickup path (`F1`), and systematic failure under a degenerate reward function (`X1`).
- **Deliverables**: Functional Streamlit application, clean GitHub repository, and `report.pdf` (IEEE format).
- **Grading**: UI interactivity, visual telemetry, and policy animation (25 pts); report mathematical rigor and Bellman derivations (15 pts); oral defense against altered obstacle maps (10 pts). **Total: 50 pts.**

---

## 4. References

- [1] C. J. C. H. Watkins and P. Dayan, "Q-learning," *Machine Learning*, vol. 8, no. 3–4, pp. 279–292, 1992, doi: 10.1007/BF00992698.
- [2] R. S. Sutton and A. G. Barto, *Reinforcement Learning: An Introduction*, 2nd ed. Cambridge, MA, USA: MIT Press, 2018.
- [3] S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed. Hoboken, NJ, USA: Pearson, 2020, pp. 789–827.
