"""Graded AI core for Project 08 (Smart Team Formation Optimizer).

You implement this module. It must:

1. Define a representation for a team assignment (e.g. a dict mapping
   `team_id -> list[student_id]`, or another representation you justify).
2. Implement `objective`: the weighted sum

       J = w1 * skill_imbalance + w2 * schedule_conflict
         + w3 * role_imbalance  + w4 * team_size_penalty

   from `data/config.json`. **You** design how each term is actually computed
   from `programming`/`mathematics`/`presentation`/`preferred_role`/
   `availability_vector` -- the config file only names the four terms, it does
   not hand you their formulas. You also choose the weights `w1..w4`
   (`data/scenarios.json` gives *example* weights for demos, not required
   values); explain your choice in the report.
3. Implement `hill_climbing`: local search over team assignments using your
   objective, with a random-restart or steepest-ascent/first-choice strategy
   you document.
4. Implement `simulated_annealing`: local search that can accept a temporarily
   worse move, with a cooling schedule you document.

Use `loader.random_baseline` (infrastructure, not part of this file) as the
naive comparison point the midterm experiment asks for.

Forbidden shortcuts (do not paste or adapt any of these into this file or
elsewhere in `starter/`):

- a finished Hill Climbing or Simulated Annealing implementation copied from
  a library, a previous course, or an AI assistant without you understanding
  and being able to explain every line;
- hard-coding the team assignment for `data/students_seed42.csv` instead of
  searching;
- calling a hosted LLM to decide the teams instead of optimizing your own
  objective yourself.
"""

from __future__ import annotations

from typing import Dict, List, Optional


def objective(
    teams: Dict[str, List[str]],
    students_by_id: Dict[str, dict],
    config: dict,
    weights: Dict[str, float],
) -> float:
    """Score a team assignment. Lower is better.

    Parameters
    ----------
    teams:
        `team_id -> list[student_id]`.
    students_by_id:
        `student_id -> student record` (see `loader.students_by_id`).
    config:
        The dict loaded by `loader.load_config` (team size bounds, roles,
        availability slots, objective term names).
    weights:
        `{"w1": ..., "w2": ..., "w3": ..., "w4": ...}` matching
        `config["objective_terms"]`, in the order skill_imbalance,
        schedule_conflict, role_imbalance, team_size_penalty.

    Returns
    -------
    A single float: the weighted sum J described in the module docstring.

    Raises
    ------
    NotImplementedError
        Always, until you implement this function.
    """
    raise NotImplementedError("Implement the team-formation objective function for Project 08.")


def hill_climbing(
    students: List[dict],
    config: dict,
    weights: Dict[str, float],
    team_size: int,
    initial_teams: Optional[Dict[str, List[str]]] = None,
    max_iterations: int = 1000,
    seed: Optional[int] = None,
) -> Dict[str, List[str]]:
    """Local search: repeatedly move to a strictly better neighboring team
    assignment (by `objective`) until no such neighbor exists or
    `max_iterations` is reached.

    Parameters
    ----------
    students:
        The full student list (see `loader.load_students`).
    config, weights, team_size:
        As in `objective`; `team_size` should respect
        `config["team_size_min"]`/`config["team_size_max"]`.
    initial_teams:
        Optional starting assignment (e.g. `loader.random_baseline(...)`, or
        the `start_assignment` fixture from `data/scenarios.json`'s
        `P08-HC-LOCAL-OPTIMUM` scenario, to reproduce the required
        local-optimum analysis). If `None`, generate your own starting point.
    max_iterations:
        Stop condition to prevent an infinite loop on a flat objective.
    seed:
        For any randomized choices in your neighborhood search (e.g. which
        neighbor to try first).

    Returns
    -------
    The best team assignment found, in the same `team_id -> list[student_id]`
    shape as `initial_teams`.

    Raises
    ------
    NotImplementedError
        Always, until you implement this function.
    """
    raise NotImplementedError("Implement Hill Climbing team formation for Project 08.")


def simulated_annealing(
    students: List[dict],
    config: dict,
    weights: Dict[str, float],
    team_size: int,
    initial_teams: Optional[Dict[str, List[str]]] = None,
    max_iterations: int = 1000,
    seed: Optional[int] = None,
) -> Dict[str, List[str]]:
    """Local search that can accept a temporarily worse neighbor according to
    a cooling schedule you design and document (e.g. `T_k = T0 * alpha**k`),
    to escape local optima that trap `hill_climbing` (see the
    `P08-HC-LOCAL-OPTIMUM` scenario in `data/scenarios.json`).

    Parameters and return value match `hill_climbing`.

    Raises
    ------
    NotImplementedError
        Always, until you implement this function.
    """
    raise NotImplementedError("Implement Simulated Annealing team formation for Project 08.")
