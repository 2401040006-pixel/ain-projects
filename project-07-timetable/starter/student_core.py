"""Graded AI core for Project 07 (University Timetable Scheduler).

You implement this module. It must formalize the timetable problem as a
CSP over the variables, domains, and hard constraints documented in
`data/README.md` (see also `loaders.py::candidate_domain` and
`loaders.py::validate_assignment`, which you may use as building blocks),
then **search** for a legal assignment -- or prove none exists.

Do not hand-code the answer for a specific instance: `solve_csp` must
generalize to any instance built from the same `data/` schema (courses.csv,
lecturers.csv, rooms.csv, timeslots.csv, constraints.json).

Forbidden shortcuts (do not paste or adapt any of these into this file or
elsewhere in `starter/`):

- a finished backtracking/CSP solver copied from a library, a previous
  course, or an AI assistant without you understanding and being able to
  explain every line;
- a hard-coded lookup table of (course_id -> lecturer/room/slot) that
  bypasses search entirely;
- calling a hosted LLM to produce the schedule instead of searching over
  the CSP yourself.
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

Choice = Tuple[str, str, str]  # (lecturer_id, room_id, slot_id)


def solve_csp(instance: dict, strategy: str = "naive") -> Optional[Dict[str, Choice]]:
    """Search for a legal assignment of every course to (lecturer, room, slot).

    Parameters
    ----------
    instance:
        The dict returned by `loaders.load_instance` -- has keys `courses`,
        `lecturers`, `rooms`, `all_slots`, `slot_info`, `constraints`.
    strategy:
        Your own label for which search strategy this call uses, e.g.
        `"naive"` for plain chronological backtracking with no ordering,
        and something like `"mrv"` or `"forward_checking"` for the
        heuristic/pruning strategy the midterm asks you to compare against
        the naive baseline. The exact strategy names are your design
        decision -- document them in your report and presentation.

    Returns
    -------
    A dict mapping every `course_id` to a `(lecturer_id, room_id, slot_id)`
    triple that satisfies every hard constraint in `instance["constraints"]`
    (see `loaders.HARD_CONSTRAINT_NAMES` and `loaders.validate_assignment`),
    or `None` if the instance is unsatisfiable.

    You are expected to also measure and report, for your required
    experiment: runtime, number of assignments/nodes explored, and search
    validity, comparing `strategy="naive"` against your heuristic strategy.
    How you collect those numbers (return them, log them, or store them on
    `self`/a module-level counter) is your design choice.

    Raises
    ------
    NotImplementedError
        Always, until you implement this function.
    """
    raise NotImplementedError("Implement the timetable CSP solver for Project 07.")


def soft_constraint_score(instance: dict, assignment: Dict[str, Choice]) -> float:
    """Optional: score a *legal* assignment against the soft constraints listed in
    `instance["constraints"]["soft_constraints"]` (e.g. cohort_daily_spread,
    lecturer_load_balance). Only required if your group chooses to use soft
    constraints -- the spec allows a solver that only handles hard constraints.

    Raises
    ------
    NotImplementedError
        Always, until you implement this function (or you may leave it
        unimplemented and skip soft constraints entirely; document that
        choice in your report if so).
    """
    raise NotImplementedError("Implement soft-constraint scoring for Project 07, or omit it and say so in your report.")
