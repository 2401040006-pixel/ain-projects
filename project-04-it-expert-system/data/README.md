# Data dictionary — Project 04

All data in this folder is synthetic helpdesk fixtures. No real user tickets, real staff contacts, or real device inventories are used. Every file is loaded and schema-checked by `starter/rule_loader.py`, which **rejects unknown top-level keys** on each record.

## `symptoms.json` (27 symptoms)

| Field | Type | Notes |
|---|---|---|
| `id` | string | Unique symptom id, e.g. `SYM01`. |
| `domain` | string | One of `hanu_wifi`, `fit_lms`, `lab_computers`, `hanu_account`, `fit_printer`. |
| `description` | string | User-facing symptom text. |

## `causes.json` (14 causes)

| Field | Type | Notes |
|---|---|---|
| `id` | string | Unique cause id, e.g. `CAUSE01`. |
| `domain` | string | Same five-domain vocabulary as symptoms. |
| `description` | string | Root-cause text. |
| `recommended_action` | string | Suggested remediation, informational only (not part of the graded core). |

## `rules.json` (48 rules)

| Field | Type | Notes |
|---|---|---|
| `id` | string | Rule id, e.g. `R020`. |
| `if` | list[string] | Symptom ids that must **all** be present for the rule to fire (conjunction). |
| `then` | string | The cause id concluded when `if` is satisfied. |

Several causes deliberately share overlapping `if` sets (e.g. `R005`/`R007`, or `R020`/`R024`). That overlap is intentional: it is what makes a symptom set "ambiguous" (see `scenarios.json`) and it is the subset you edit for the required rule-removal experiment.

## `scenarios.json` (15 scenarios)

| Field | Type | Notes |
|---|---|---|
| `id` | string | Scenario id. |
| `class` | string | One of the four required demo classes: `single_cause`, `ambiguous`, `missing_info`, `contradictory_symptoms`. |
| `domain` | string | Primary domain for the scenario. |
| `presented_symptoms` | list[string] | Symptom ids the user reports for this scenario. |
| `description` | string | Plain-language summary of the case. |
| `expected_behavior` | string | Qualitative description of correct reasoning; not a hard-coded return value. |
| `reasoning_probe` | string | Presentation/oral-defense question tied to this fixture. |

Representative fixtures by class: `SC01_single_cause_portal_loop` (`single_cause`), `SC04_ambiguous_wifi_drop` (`ambiguous`), `SC06_missing_info_no_symptoms` (`missing_info`), and `SC07_contradictory_printer` (`contradictory_symptoms`).

## Unknown-key policy

`rule_loader.py` raises `ValueError` if a record in any of these files contains a key not listed above (or in the matching loader's `ALLOWED_KEYS` set), and also if a rule or scenario references a symptom/cause id that does not exist in `symptoms.json` / `causes.json`. If you add a field or a fixture, update this dictionary and the loader's allow-list together.
