# Project 04 — IT Troubleshooting Expert System

## 1. Problem Description

Expert Systems (ES)—a classical subfield of Knowledge-Based Systems within Artificial Intelligence—emulate human domain specialists by combining empirical rule bases with deductive inference engines to solve diagnostic problems. Unlike opaque black-box models, rule-based systems offer determinism, modular knowledge curation, and an explicit explanation facility tracing the causal chain behind every diagnosis.

This project builds an intelligent diagnostic expert system for a campus IT helpdesk. The system handles technical incidents across five support domains: **Campus Wi-Fi**, **Learning Management System (LMS)**, **Computer Laboratories**, **Student Identity and Accounts**, and **Network Printers** (stored in `data/` under the domain keys `hanu_wifi`, `fit_lms`, `lab_computers`, `hanu_account`, and `fit_printer`). Given an arbitrary set of user-reported symptoms the system must apply forward-chaining deduction to identify supported failure causes, resolve ambiguous multi-cause conflicts, detect contradictory reports, and prescribe actionable remediations.

---

## 2. Provided Materials & Starter Resources

The project provides a curated rule base, symptom and cause catalogs, benchmark scenarios, and a Streamlit interface skeleton.

### File Structure
```text
project-04-it-expert-system/
├── data/
│   ├── README.md                 # Data dictionary and taxonomy definitions
│   ├── symptoms.json             # 27 structured symptom definitions across 5 IT domains
│   ├── causes.json               # 14 diagnostic causes with recommended actions
│   ├── rules.json                # 48 if-then production rules with intentional overlap
│   └── scenarios.json            # 15 benchmark diagnostic fixtures (SC01–SC15)
├── starter/
│   ├── rule_loader.py            # Schema validation and cross-referencing utilities (provided)
│   ├── student_core.py           # Algorithmic stubs — implement here
│   └── app.py                   # Streamlit diagnostic interface skeleton (provided)
├── tests/
│   └── test_project_04_sanity.py
└── requirements.txt
```

### Starter Infrastructure vs. Student Implementation
`starter/rule_loader.py` validates rule syntax and JSON schema conformity. `starter/app.py` renders a categorised symptom checklist. Students implement all AI logic in `starter/student_core.py`. Third-party rule engines (e.g., CLIPS, PyKE) and LLM APIs are prohibited.

### Installation and Execution
```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run starter/app.py
```

---

## 3. Requirements & Deliverables

### 3.1 Midterm Milestone — AI Core
- **Implement**: `infer(reported_symptoms, rules)` — forward-chaining rule matching that evaluates precondition satisfaction and returns all valid candidate causes without premature elimination; and `explain(cause_id, reported_symptoms, rules)` — chronological proof traces showing the exact sequence of fired rules. When symptoms are insufficient the engine must return an empty diagnosis rather than an unsupported guess.
- **Experiment**: Perform an ablation study on `data/rules.json`. Remove or modify targeted rule subsets (e.g., remove `R007`) and analyse how ambiguous case `SC04_ambiguous_wifi_drop` transitions from multi-cause ambiguity to a single deterministic cause. Quantify diagnostic sensitivity and conflict-resolution behaviour, and formalise the theoretical boundaries of monotonic deterministic rule systems when handling contradictory inputs (`SC07_contradictory_printer`).
- **Deliverables**: Completed `student_core.py`, ablation experiment notebooks/scripts, `presentation.pdf`.
- **Grading Criteria**: Rule engine architecture and logical soundness (15 pts); ablation rigour and conflict analysis (10 pts); oral defence and live diagnostic demo (15 pts). **Total: 40 pts.**

### 3.2 Final Milestone — AI Product
- **Interactive Application**: Streamlit application with interactive symptom selection organised by the five support domains (`hanu_wifi`, `fit_lms`, `lab_computers`, `hanu_account`, `fit_printer`); dynamic follow-up questioning when preliminary symptoms yield ambiguous or empty matches; a visual reasoning graph; and actionable remediation recommendations.
- **Stress Scenarios**: Validate system stability across the four mandatory fixture archetypes: unambiguous single cause (`SC01_single_cause_portal_loop`), overlapping ambiguous hypotheses (`SC04_ambiguous_wifi_drop`), uninformative empty symptom set (`SC06_missing_info_no_symptoms`), and mutually contradictory symptoms (`SC07_contradictory_printer`).
- **Deliverables**: Functional Streamlit application, GitHub repository, `report.pdf` (IEEE format).
- **Grading Criteria**: Product UI ergonomics and interactive diagnostic flow (25 pts); technical report formalisation and ablation evaluation (15 pts); oral defence against complex multi-fault incidents (10 pts). **Total: 50 pts.**

---

## 4. References

- [1] E. H. Shortliffe and B. G. Buchanan, "A model of inexact reasoning in medicine," *Mathematical Biosciences*, vol. 23, no. 3–4, pp. 351–379, 1975, doi: 10.1016/0025-5564(75)90047-4.
- [2] J. Giarratano and G. Riley, *Expert Systems: Principles and Programming*, 4th ed. Boston, MA, USA: Course Technology, 2004.
- [3] S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed. Hoboken, NJ, USA: Pearson, 2020, pp. 280–313.
