"""Data loaders for Project 08 (Smart Team Formation Optimizer).

Infrastructure only: no team assignment, objective scoring, Hill Climbing,
or Simulated Annealing happens here.

All loaded data describes synthetic educational students, not real ones.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

SYNTHETIC_DATA_NOTICE = (
    "All students, skills, roles, and availability in this project are synthetic "
    "educational data. This is NOT a real student roster."
)


def load_config(path: Path = DATA_DIR / "config.json") -> dict:
    """Load team-size bounds, roles, availability slots, and the objective term list."""
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_scenarios(path: Path = DATA_DIR / "scenarios.json") -> List[dict]:
    """Load the named demo scenarios (skill/schedule/role priority, weight trade-off,
    and the Hill Climbing local-optimum fixture)."""
    with path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    return raw["scenarios"]


def load_students(path: Path = DATA_DIR / "students_seed42.csv") -> List[Dict[str, object]]:
    """Load the committed synthetic student sample.

    Returns a list of dicts with `student_id`, `programming`, `mathematics`,
    `presentation` (ints), `preferred_role` (str), and `availability_vector`
    (str of '0'/'1' characters, one per `config["availability_slots"]` entry).
    """
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    students = []
    for row in rows:
        students.append(
            {
                "student_id": row["student_id"],
                "programming": int(row["programming"]),
                "mathematics": int(row["mathematics"]),
                "presentation": int(row["presentation"]),
                "preferred_role": row["preferred_role"],
                "availability_vector": row["availability_vector"],
            }
        )
    return students


def load_all(data_dir: Path = DATA_DIR) -> dict:
    """Convenience loader: reads config, scenarios, and the committed students at once."""
    data_dir = Path(data_dir)
    return {
        "config": load_config(data_dir / "config.json"),
        "scenarios": load_scenarios(data_dir / "scenarios.json"),
        "students": load_students(data_dir / "students_seed42.csv"),
    }


def find_scenario(scenarios: List[dict], scenario_id: str) -> dict:
    for scenario in scenarios:
        if scenario["id"] == scenario_id:
            return scenario
    raise KeyError(f"no scenario with id {scenario_id!r}")


def students_by_id(students: List[Dict[str, object]]) -> Dict[str, Dict[str, object]]:
    return {s["student_id"]: s for s in students}


def random_baseline(
    students: List[Dict[str, object]], team_size: int, seed: int
) -> Dict[str, List[str]]:
    """Partition students into teams of `team_size` uniformly at random.

    This is the required **baseline** for comparison, not an optimizer: it does
    not look at skill, role, or availability at all. It is provided as
    infrastructure because it involves no search or objective evaluation --
    your graded core is comparing Hill Climbing and Simulated Annealing
    *against* this baseline, not writing the baseline itself.
    """
    import random

    rng = random.Random(seed)
    ids = [s["student_id"] for s in students]
    rng.shuffle(ids)
    teams: Dict[str, List[str]] = {}
    for i in range(0, len(ids), team_size):
        team_id = f"team_random_{i // team_size + 1:02d}"
        teams[team_id] = ids[i : i + team_size]
    return teams
