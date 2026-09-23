"""Data loaders and hard-constraint validation for Project 07 (timetable CSP).

This module is **infrastructure only**. It:

- loads `courses.csv`, `lecturers.csv`, `rooms.csv`, `timeslots.csv`, and
  `constraints.json` from an instance folder and validates their shape
  (unknown ids, malformed availability, duplicate ids, negative numbers);
- can check whether a *given* assignment satisfies every hard constraint
  (`validate_assignment`), and can list the candidate domain for one course
  (`candidate_domain`), both of which are useful building blocks for your
  solver and for your UI.

It does **not** search for an assignment. Finding a legal (or provably
impossible) assignment is the graded AI core in `student_core.py::solve_csp`.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

Choice = Tuple[str, str, str]  # (lecturer_id, room_id, slot_id)

HARD_CONSTRAINT_NAMES = (
    "lecturer_in_eligible_set",
    "lecturer_available_at_slot",
    "room_type_and_capacity_match",
    "room_available_at_slot",
    "no_room_double_booking",
    "no_lecturer_double_booking",
    "no_cohort_double_booking",
)


class SchemaError(ValueError):
    """Raised when instance data does not match the documented schema."""


def _read_csv(path: Path) -> List[dict]:
    if not path.exists():
        raise SchemaError(f"{path}: file not found")
    with path.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise SchemaError(f"{path}: no data rows")
    return rows


def _parse_slot_set(value: str, all_slots: Sequence[str], where: str) -> set:
    value = (value or "").strip()
    if value.upper() == "ALL":
        return set(all_slots)
    slots = [s for s in value.split(";") if s]
    unknown = [s for s in slots if s not in all_slots]
    if unknown:
        raise SchemaError(f"{where}: unknown slot id(s) {unknown}")
    if not slots:
        raise SchemaError(f"{where}: available_slots must be 'ALL' or a non-empty ';'-separated list")
    return set(slots)


def load_timeslots(path: Path) -> Tuple[List[str], Dict[str, dict]]:
    """Returns (ordered slot_ids, slot_id -> {day, period, start_time, end_time})."""
    rows = _read_csv(path)
    slots: Dict[str, dict] = {}
    for row in rows:
        slot_id = row["slot_id"]
        if slot_id in slots:
            raise SchemaError(f"{path}: duplicate slot_id {slot_id!r}")
        slots[slot_id] = {
            "day": row["day"],
            "period": int(row["period"]),
            "start_time": row["start_time"],
            "end_time": row["end_time"],
        }
    return list(slots.keys()), slots


def load_lecturers(path: Path, all_slots: Sequence[str]) -> Dict[str, dict]:
    rows = _read_csv(path)
    lecturers: Dict[str, dict] = {}
    for row in rows:
        lecturer_id = row["lecturer_id"]
        if lecturer_id in lecturers:
            raise SchemaError(f"{path}: duplicate lecturer_id {lecturer_id!r}")
        lecturers[lecturer_id] = {
            "name": row["name"],
            "available_slots": _parse_slot_set(
                row["available_slots"], all_slots, f"{path}#{lecturer_id}"
            ),
        }
    return lecturers


def load_rooms(path: Path, all_slots: Sequence[str]) -> Dict[str, dict]:
    rows = _read_csv(path)
    rooms: Dict[str, dict] = {}
    for row in rows:
        room_id = row["room_id"]
        if room_id in rooms:
            raise SchemaError(f"{path}: duplicate room_id {room_id!r}")
        capacity = int(row["capacity"])
        if capacity <= 0:
            raise SchemaError(f"{path}#{room_id}: capacity must be positive")
        rooms[room_id] = {
            "room_type": row["room_type"],
            "capacity": capacity,
            "available_slots": _parse_slot_set(
                row["available_slots"], all_slots, f"{path}#{room_id}"
            ),
        }
    return rooms


def load_courses(path: Path, lecturers: Dict[str, dict]) -> List[dict]:
    rows = _read_csv(path)
    courses: List[dict] = []
    seen_ids = set()
    for row in rows:
        course_id = row["course_id"]
        if course_id in seen_ids:
            raise SchemaError(f"{path}: duplicate course_id {course_id!r}")
        seen_ids.add(course_id)

        min_capacity = int(row["min_capacity"])
        if min_capacity <= 0:
            raise SchemaError(f"{path}#{course_id}: min_capacity must be positive")

        eligible = [x for x in row["eligible_lecturers"].split(";") if x]
        if not eligible:
            raise SchemaError(f"{path}#{course_id}: eligible_lecturers must not be empty")
        unknown = [lid for lid in eligible if lid not in lecturers]
        if unknown:
            raise SchemaError(f"{path}#{course_id}: unknown lecturer id(s) {unknown}")

        courses.append(
            {
                "course_id": course_id,
                "course_name": row["course_name"],
                "cohort": row["cohort"],
                "required_room_type": row["required_room_type"],
                "min_capacity": min_capacity,
                "eligible_lecturers": eligible,
            }
        )
    return courses


def load_constraints(path: Path) -> dict:
    if not path.exists():
        raise SchemaError(f"{path}: file not found")
    with path.open("r", encoding="utf-8") as handle:
        constraints = json.load(handle)
    for key in ("hard_constraints", "extra_constraints"):
        if key not in constraints:
            raise SchemaError(f"{path}: missing key {key!r}")
    unknown_hard = set(constraints["hard_constraints"]) - set(HARD_CONSTRAINT_NAMES)
    if unknown_hard:
        raise SchemaError(f"{path}: unknown hard_constraints entries {sorted(unknown_hard)}")
    return constraints


def load_instance(instance_dir: Path) -> dict:
    """Load and validate one instance folder. Does not search for a solution.

    Returns a dict with keys: ``courses``, ``lecturers``, ``rooms``,
    ``all_slots``, ``slot_info``, ``constraints``.
    """
    instance_dir = Path(instance_dir)
    all_slots, slot_info = load_timeslots(instance_dir / "timeslots.csv")
    lecturers = load_lecturers(instance_dir / "lecturers.csv", all_slots)
    rooms = load_rooms(instance_dir / "rooms.csv", all_slots)
    courses = load_courses(instance_dir / "courses.csv", lecturers)
    constraints = load_constraints(instance_dir / "constraints.json")

    room_types_available = {room["room_type"] for room in rooms.values()}
    for course in courses:
        if course["required_room_type"] not in room_types_available:
            raise SchemaError(
                f"{instance_dir}#{course['course_id']}: no room has "
                f"room_type={course['required_room_type']!r}"
            )

    return {
        "courses": courses,
        "lecturers": lecturers,
        "rooms": rooms,
        "all_slots": all_slots,
        "slot_info": slot_info,
        "constraints": constraints,
    }


def candidate_domain(course: dict, instance: dict) -> List[Choice]:
    """All (lecturer_id, room_id, slot_id) triples that satisfy this course's own
    hard constraints in isolation (eligibility, room type/capacity, availability).
    Does not check other courses -- use `validate_assignment` for that.
    """
    domain: List[Choice] = []
    for lecturer_id in course["eligible_lecturers"]:
        lecturer = instance["lecturers"][lecturer_id]
        for room_id, room in instance["rooms"].items():
            if room["room_type"] != course["required_room_type"]:
                continue
            if room["capacity"] < course["min_capacity"]:
                continue
            for slot_id in lecturer["available_slots"] & room["available_slots"]:
                domain.append((lecturer_id, room_id, slot_id))
    return domain


def validate_assignment(
    instance: dict, assignment: Dict[str, Choice]
) -> Tuple[bool, List[str]]:
    """Check a *given* assignment (course_id -> (lecturer_id, room_id, slot_id))
    against every hard constraint. Returns (is_valid, violation_messages).

    This function does not search: it only checks the assignment you (or your
    solver) already produced. An empty assignment, or one missing courses, is
    reported as violations rather than raising.
    """
    violations: List[str] = []
    courses_by_id = {c["course_id"]: c for c in instance["courses"]}

    missing = set(courses_by_id) - set(assignment)
    if missing:
        violations.append(f"missing assignment for course(s): {sorted(missing)}")

    slot_usage: Dict[str, List[str]] = {}
    for course_id, choice in assignment.items():
        course = courses_by_id.get(course_id)
        if course is None:
            violations.append(f"{course_id}: not a course in this instance")
            continue
        lecturer_id, room_id, slot_id = choice

        if lecturer_id not in course["eligible_lecturers"]:
            violations.append(f"{course_id}: lecturer {lecturer_id} not in eligible_lecturers")
        lecturer = instance["lecturers"].get(lecturer_id)
        if lecturer is not None and slot_id not in lecturer["available_slots"]:
            violations.append(f"{course_id}: lecturer {lecturer_id} not available at {slot_id}")

        room = instance["rooms"].get(room_id)
        if room is None:
            violations.append(f"{course_id}: unknown room {room_id}")
        else:
            if room["room_type"] != course["required_room_type"]:
                violations.append(f"{course_id}: room {room_id} has the wrong room_type")
            if room["capacity"] < course["min_capacity"]:
                violations.append(f"{course_id}: room {room_id} capacity too small")
            if slot_id not in room["available_slots"]:
                violations.append(f"{course_id}: room {room_id} not available at {slot_id}")

        slot_usage.setdefault(slot_id, []).append(course_id)

    # Cross-course double-booking + cohort clash.
    for slot_id, course_ids in slot_usage.items():
        for i, course_id_a in enumerate(course_ids):
            for course_id_b in course_ids[i + 1 :]:
                choice_a = assignment[course_id_a]
                choice_b = assignment[course_id_b]
                if choice_a[0] == choice_b[0]:
                    violations.append(
                        f"{course_id_a}/{course_id_b}: same lecturer {choice_a[0]} at {slot_id}"
                    )
                if choice_a[1] == choice_b[1]:
                    violations.append(
                        f"{course_id_a}/{course_id_b}: same room {choice_a[1]} at {slot_id}"
                    )
                cohort_a = courses_by_id[course_id_a]["cohort"]
                cohort_b = courses_by_id[course_id_b]["cohort"]
                if cohort_a == cohort_b:
                    violations.append(
                        f"{course_id_a}/{course_id_b}: same cohort {cohort_a} at {slot_id}"
                    )

    slot_day = {slot_id: info["day"] for slot_id, info in instance["slot_info"].items()}
    for rule in instance["constraints"].get("extra_constraints", []):
        if rule.get("type") == "lecturer_daily_limit":
            lecturer_id = rule["lecturer_id"]
            max_per_day = int(rule.get("max_per_day", 1))
            per_day: Dict[str, int] = {}
            for course_id, (l_id, _room_id, slot_id) in assignment.items():
                if l_id != lecturer_id:
                    continue
                day = slot_day.get(slot_id)
                per_day[day] = per_day.get(day, 0) + 1
            for day, count in per_day.items():
                if count > max_per_day:
                    violations.append(
                        f"lecturer_daily_limit: {lecturer_id} teaches {count} courses on "
                        f"{day} (max {max_per_day})"
                    )

    return (len(violations) == 0, violations)
