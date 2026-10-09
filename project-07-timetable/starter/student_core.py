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
from starter.loaders import candidate_domain
# Vừa thêm vào 

from __future__ import annotations

from typing import Dict, Optional, Tuple

Choice = Tuple[str, str, str]  # (lecturer_id, room_id, slot_id)

# THAY THẾ TIẾP NÀY 
# def solve_csp(instance: dict, strategy: str = "naive") -> Optional[Dict[str, Choice]]:
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
    # raise NotImplementedError("Implement the timetable CSP solver for Project 07.")
# THAY THẾ TIẾP NÀY 
# 
def solve_csp(instance: dict, strategy: str = "naive") -> Optional[Dict[str, Choice]]:
    courses = instance["courses"]
    
    # 1. Khởi tạo Domain cho từng môn học
    domains = {
        c_id: candidate_domain(c_id, instance) 
        for c_id in courses
    }
    
    # Nếu có môn học nào domain rỗng ngay từ đầu -> UNSAT
    if any(len(dom) == 0 for dom in domains.values()):
        return None

    assignment: Dict[str, Choice] = {}

    def is_consistent(course_id: str, choice: Choice, current_assignment: Dict[str, Choice]) -> bool:
        lec_id, room_id, slot_id = choice
        c_info = courses[course_id]
        
        for assigned_c_id, (a_lec, a_room, a_slot) in current_assignment.items():
            if a_slot == slot_id:
                # Kiểm tra trùng phòng
                if a_room == room_id:
                    return False
                # Kiểm tra trùng giảng viên
                if a_lec == lec_id:
                    return False
                # Kiểm tra trùng lịch của Cohort (nếu sinh viên thuộc cùng lớp/ngành)
                assigned_c_info = courses[assigned_c_id]
                if set(c_info.get("cohorts", [])).intersection(set(assigned_c_info.get("cohorts", []))):
                    return False
        return True

    def select_unassigned_variable(current_assignment: Dict[str, Choice]):
        unassigned = [c for c in courses if c not in current_assignment]
        if strategy == "mrv":
            # MRV (Minimum Remaining Values): Chọn môn học có ít lựa chọn hợp lệ nhất
            return min(unassigned, key=lambda c: len(domains[c]))
        else:
            # Naive: Chọn theo thứ tự xuất hiện ban đầu
            return unassigned[0]

    def backtrack() -> bool:
        if len(assignment) == len(courses):
            return True

        var = select_unassigned_variable(assignment)

        for value in domains[var]:
            if is_consistent(var, value, assignment):
                assignment[var] = value
                
                # Thực hiện đệ quy
                if backtrack():
                    return True
                
                # Quay lui (Backtrack)
                del assignment[var]

        return False

    if backtrack():
        return assignment
    return None
# 


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
