"""Sanity tests for Project 07 (University Timetable Scheduler).

These tests check that the provided instances load, that the four required
demo instances exist with the right satisfiability status, and that the
starter core is still unimplemented. They do **not** grade any student's
solver.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
STARTER_DIR = PROJECT_ROOT / "starter"


def _load_module(module_name: str, file_path: Path):
    """Load a starter module under a project-unique name.

    Project 07's `starter/student_core.py` and project 08's
    `starter/student_core.py` share the same on-disk filename. Plain
    `sys.path.insert` + `import student_core` would collide via
    `sys.modules["student_core"]` when both projects' tests run in the same
    pytest session (as the kit-wide verification command does). Loading by
    file path under a unique module name avoids that collision entirely.
    """
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


loaders = _load_module("project07_loaders", STARTER_DIR / "loaders.py")
student_core = _load_module("project07_student_core", STARTER_DIR / "student_core.py")

REQUIRED_INSTANCES = (
    "feasible",
    "restricted_rooms",
    "extra_lecturer",
    "unsat",
)


def test_data_dir_has_no_sample_solution():
    """The locked rule: never ship a solved instance to students."""
    assert not (DATA_DIR / "sample_solution.json").exists()
    for instance_name in REQUIRED_INSTANCES:
        instance_dir = DATA_DIR / f"instance_{instance_name}"
        assert not (instance_dir / "sample_solution.json").exists()
        assert not (instance_dir / "feasible_witness.json").exists()


@pytest.mark.parametrize("instance_name", REQUIRED_INSTANCES)
def test_each_instance_has_required_files(instance_name):
    instance_dir = DATA_DIR / f"instance_{instance_name}"
    for filename in ("courses.csv", "lecturers.csv", "rooms.csv", "timeslots.csv", "constraints.json"):
        assert (instance_dir / filename).exists(), f"missing {filename} in {instance_dir}"


@pytest.mark.parametrize("instance_name", REQUIRED_INSTANCES)
def test_each_instance_loads_and_validates(instance_name):
    instance_dir = DATA_DIR / f"instance_{instance_name}"
    instance = loaders.load_instance(instance_dir)
    assert len(instance["courses"]) >= 1
    assert len(instance["lecturers"]) >= 1
    assert len(instance["rooms"]) >= 1
    assert len(instance["all_slots"]) >= 1


def test_feasible_instance_size_within_recommended_band():
    instance = loaders.load_instance(DATA_DIR / "instance_feasible")
    assert 15 <= len(instance["courses"]) <= 25
    assert 6 <= len(instance["lecturers"]) <= 10
    assert 6 <= len(instance["rooms"]) <= 10
    assert 15 <= len(instance["all_slots"]) <= 25


def test_restricted_rooms_instance_has_fewer_rooms_than_feasible():
    feasible = loaders.load_instance(DATA_DIR / "instance_feasible")
    restricted = loaders.load_instance(DATA_DIR / "instance_restricted_rooms")
    assert len(restricted["rooms"]) < len(feasible["rooms"])


def test_extra_lecturer_instance_has_an_extra_constraint():
    instance = loaders.load_instance(DATA_DIR / "instance_extra_lecturer")
    extra = instance["constraints"]["extra_constraints"]
    assert len(extra) >= 1
    assert extra[0]["type"] == "lecturer_daily_limit"


def test_unsat_instance_has_a_singleton_lecturer_bottleneck():
    """Confirm the pigeonhole structure without running the instructor solver:
    at least two courses share an eligible_lecturers set of size 1 pointing at
    the same lecturer, and that lecturer has exactly one available slot.
    """
    instance = loaders.load_instance(DATA_DIR / "instance_unsat")
    singleton_courses = [
        c for c in instance["courses"] if len(c["eligible_lecturers"]) == 1
    ]
    by_lecturer: dict[str, list[str]] = {}
    for course in singleton_courses:
        lecturer_id = course["eligible_lecturers"][0]
        by_lecturer.setdefault(lecturer_id, []).append(course["course_id"])
    bottleneck_lecturers = [
        lid
        for lid, course_ids in by_lecturer.items()
        if len(course_ids) >= 2 and len(instance["lecturers"][lid]["available_slots"]) == 1
    ]
    assert bottleneck_lecturers, (
        "expected at least one lecturer with exactly one available slot "
        "required exclusively by 2+ courses"
    )


def test_validate_assignment_flags_lecturer_double_booking():
    instance = loaders.load_instance(DATA_DIR / "instance_feasible")
    courses = instance["courses"]
    # Force both of the first two courses onto the same lecturer/slot/room
    # combo that is legal for the first course, to check the validator
    # catches the resulting double-booking rather than silently accepting it.
    first, second = courses[0], courses[1]
    domain_first = loaders.candidate_domain(first, instance)
    assert domain_first, "test fixture assumption: first course must have a non-empty domain"
    lecturer_id, room_id, slot_id = domain_first[0]
    bad_assignment = {
        first["course_id"]: (lecturer_id, room_id, slot_id),
        second["course_id"]: (lecturer_id, room_id, slot_id),
    }
    is_valid, violations = loaders.validate_assignment(instance, bad_assignment)
    assert not is_valid
    assert violations


def test_solve_csp_is_not_implemented():
    instance = loaders.load_instance(DATA_DIR / "instance_feasible")
    with pytest.raises(NotImplementedError):
        student_core.solve_csp(instance)


def test_soft_constraint_score_is_not_implemented():
    instance = loaders.load_instance(DATA_DIR / "instance_feasible")
    with pytest.raises(NotImplementedError):
        student_core.soft_constraint_score(instance, {})
