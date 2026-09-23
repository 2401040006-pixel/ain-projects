"""Sanity tests for Project 08 (Smart Team Formation Optimizer).

These tests check that the provided data loads, that the required demo
scenarios (including the Hill-Climbing local-optimum fixture) exist and are
internally consistent, and that the starter core is still unimplemented.
They do **not** grade any student's optimizer.
"""

from __future__ import annotations

import importlib.util
import itertools
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
STARTER_DIR = PROJECT_ROOT / "starter"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


def _load_module(module_name: str, file_path: Path):
    """Load a project module under a project-unique name.

    Several projects in this kit ship a `starter/student_core.py` (and some
    ship a `scripts/generate_students.py`). Plain `sys.path.insert` + `import
    student_core` would collide via `sys.modules["student_core"]` when two
    projects' tests run in the same pytest session (as the kit-wide
    verification command does). Loading by file path under a unique module
    name avoids that collision entirely.
    """
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


loader = _load_module("project08_loader", STARTER_DIR / "loader.py")
student_core = _load_module("project08_student_core", STARTER_DIR / "student_core.py")
generate_students = _load_module("project08_generate_students", SCRIPTS_DIR / "generate_students.py")

REQUIRED_SCENARIO_CLASSES = {
    "skill_priority",
    "schedule_priority",
    "role_priority",
    "weight_tradeoff",
    "hill_climbing_local_optimum",
}


def test_config_loads_and_has_required_keys():
    config = loader.load_config()
    assert 3 <= config["team_size_min"] <= config["team_size_max"] <= 4
    assert len(config["roles"]) >= 2
    assert len(config["availability_slots"]) >= 1
    term_names = {t["name"] for t in config["objective_terms"]}
    assert term_names == {
        "skill_imbalance",
        "schedule_conflict",
        "role_imbalance",
        "team_size_penalty",
    }


def test_students_load_and_are_in_committed_range():
    students = loader.load_students()
    assert 40 <= len(students) <= 80
    ids = [s["student_id"] for s in students]
    assert len(ids) == len(set(ids)), "student_id must be unique"
    config = loader.load_config()
    for s in students:
        assert 1 <= s["programming"] <= 10
        assert 1 <= s["mathematics"] <= 10
        assert 1 <= s["presentation"] <= 10
        assert s["preferred_role"] in config["roles"]
        assert len(s["availability_vector"]) == len(config["availability_slots"])
        assert set(s["availability_vector"]) <= {"0", "1"}
        assert "1" in s["availability_vector"], "every student must be available at least one slot"


def test_scenarios_cover_required_classes():
    scenarios = loader.load_scenarios()
    classes = {s["class"] for s in scenarios}
    assert REQUIRED_SCENARIO_CLASSES.issubset(classes)
    ids = [s["id"] for s in scenarios]
    assert len(ids) == len(set(ids)), "scenario ids must be unique"


def test_local_optimum_fixture_students_exist_and_match_recorded_skill_sums():
    scenarios = loader.load_scenarios()
    scenario = loader.find_scenario(scenarios, "P08-HC-LOCAL-OPTIMUM")
    students = loader.students_by_id(loader.load_students())

    team_a = scenario["start_assignment"]["team_local_a"]
    team_b = scenario["start_assignment"]["team_local_b"]
    all_ids = team_a + team_b
    assert len(all_ids) == len(set(all_ids)), "fixture students must be distinct"

    for student_id in all_ids:
        assert student_id in students, f"{student_id} must exist in students_seed42.csv"
        recorded = scenario["skill_sum_per_student"][student_id]
        actual = (
            students[student_id]["programming"]
            + students[student_id]["mathematics"]
            + students[student_id]["presentation"]
        )
        assert actual == recorded, f"{student_id}: skill sum drifted from the documented fixture"


def test_local_optimum_fixture_is_a_genuine_1swap_local_optimum():
    """Re-derive the local-optimum property from the raw skill sums, independent
    of the scenario file's own claims, to guard against the fixture silently
    breaking if students_seed42.csv is ever regenerated differently.
    """
    scenarios = loader.load_scenarios()
    scenario = loader.find_scenario(scenarios, "P08-HC-LOCAL-OPTIMUM")
    skill_sum = scenario["skill_sum_per_student"]
    team_a = list(scenario["start_assignment"]["team_local_a"])
    team_b = list(scenario["start_assignment"]["team_local_b"])

    def imbalance(a_ids, b_ids):
        return abs(sum(skill_sum[x] for x in a_ids) - sum(skill_sum[x] for x in b_ids))

    current = imbalance(team_a, team_b)
    assert current == scenario["current_imbalance"]
    assert current > 0

    # No single swap should produce a strictly smaller imbalance.
    for a in team_a:
        for b in team_b:
            new_a = [x for x in team_a if x != a] + [b]
            new_b = [x for x in team_b if x != b] + [a]
            assert imbalance(new_a, new_b) >= current

    # Some 2-for-2 swap must produce a strictly smaller imbalance (proving it
    # is a local optimum, not the global optimum for this 8-student pool).
    found_escape = False
    for a1, a2 in itertools.combinations(team_a, 2):
        for b1, b2 in itertools.combinations(team_b, 2):
            new_a = [x for x in team_a if x not in (a1, a2)] + [b1, b2]
            new_b = [x for x in team_b if x not in (b1, b2)] + [a1, a2]
            if imbalance(new_a, new_b) < current:
                found_escape = True
                break
        if found_escape:
            break
    assert found_escape, "expected at least one 2-for-2 swap to escape the local optimum"


def test_generator_is_reproducible_for_default_seed(tmp_path):
    rows_a = generate_students.generate_students(n=60, seed=42)
    rows_b = generate_students.generate_students(n=60, seed=42)
    assert rows_a == rows_b

    committed = loader.load_students()
    assert len(rows_a) == len(committed)
    for generated, committed_row in zip(rows_a, committed):
        assert generated["student_id"] == committed_row["student_id"]
        assert int(generated["programming"]) == committed_row["programming"]
        assert int(generated["mathematics"]) == committed_row["mathematics"]
        assert int(generated["presentation"]) == committed_row["presentation"]
        assert generated["preferred_role"] == committed_row["preferred_role"]
        assert generated["availability_vector"] == committed_row["availability_vector"]


def test_random_baseline_partitions_all_students_without_optimizing():
    students = loader.load_students()
    config = loader.load_config()
    teams = loader.random_baseline(students, config["team_size_min"], seed=42)
    assigned = [sid for team in teams.values() for sid in team]
    assert len(assigned) == len(set(assigned))
    assert set(assigned) <= {s["student_id"] for s in students}


@pytest.mark.parametrize(
    "call",
    [
        lambda: student_core.objective({}, {}, loader.load_config(), {"w1": 1, "w2": 0, "w3": 0, "w4": 0}),
        lambda: student_core.hill_climbing(loader.load_students(), loader.load_config(), {"w1": 1, "w2": 0, "w3": 0, "w4": 0}, 4),
        lambda: student_core.simulated_annealing(loader.load_students(), loader.load_config(), {"w1": 1, "w2": 0, "w3": 0, "w4": 0}, 4),
    ],
)
def test_student_core_is_not_implemented(call):
    with pytest.raises(NotImplementedError):
        call()
