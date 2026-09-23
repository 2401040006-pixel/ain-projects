"""Knowledge-base loaders for Project 04 (IT Troubleshooting Expert System).

This module is **infrastructure only**: it reads the JSON files under
`data/`, validates their shape and cross-references, and hands back
plain Python data structures. It does not perform any rule-based
inference, forward chaining, or explanation -- that is the graded core
the student implements in `student_core.py`.

Every loader rejects unknown top-level keys on each record, and
`load_rules` / `load_scenarios` reject symptom/cause ids that are not
defined in `symptoms.json` / `causes.json`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SchemaError(ValueError):
    """Raised when a JSON file does not match the documented schema."""


def _read_json(path: str | Path) -> Any:
    path = Path(path)
    with path.open("r", encoding="utf-8") as fh:
        try:
            return json.load(fh)
        except json.JSONDecodeError as exc:
            raise SchemaError(f"{path}: not valid JSON ({exc})") from exc


def _check_keys(record: dict, allowed: set[str], required: set[str], where: str) -> None:
    if not isinstance(record, dict):
        raise SchemaError(f"{where}: expected an object, got {type(record).__name__}")
    unknown = set(record.keys()) - allowed
    if unknown:
        raise SchemaError(f"{where}: unknown key(s) {sorted(unknown)}; allowed={sorted(allowed)}")
    missing = required - set(record.keys())
    if missing:
        raise SchemaError(f"{where}: missing required key(s) {sorted(missing)}")


SYMPTOM_KEYS = {"id", "domain", "description"}
SYMPTOM_REQUIRED = {"id", "domain", "description"}


def load_symptoms(path: str | Path) -> list[dict]:
    """Load and validate `symptoms.json`. Returns the list of symptom records."""
    data = _read_json(path)
    if "symptoms" not in data:
        raise SchemaError(f"{path}: top-level object must contain a 'symptoms' key")
    symptoms = data["symptoms"]
    for i, symptom in enumerate(symptoms):
        _check_keys(symptom, SYMPTOM_KEYS, SYMPTOM_REQUIRED, f"{path}#symptoms[{i}]")
    return symptoms


CAUSE_KEYS = {"id", "domain", "description", "recommended_action"}
CAUSE_REQUIRED = {"id", "domain", "description"}


def load_causes(path: str | Path) -> list[dict]:
    """Load and validate `causes.json`. Returns the list of cause records."""
    data = _read_json(path)
    if "causes" not in data:
        raise SchemaError(f"{path}: top-level object must contain a 'causes' key")
    causes = data["causes"]
    for i, cause in enumerate(causes):
        _check_keys(cause, CAUSE_KEYS, CAUSE_REQUIRED, f"{path}#causes[{i}]")
    return causes


RULE_KEYS = {"id", "if", "then", "comment"}
RULE_REQUIRED = {"id", "if", "then"}


def load_rules(path: str | Path, symptom_ids: set[str], cause_ids: set[str]) -> list[dict]:
    """Load and validate `rules.json`. Returns the list of rule records.

    Every symptom id in a rule's `if` list must exist in `symptom_ids`,
    and `then` must exist in `cause_ids`.
    """
    data = _read_json(path)
    if "rules" not in data:
        raise SchemaError(f"{path}: top-level object must contain a 'rules' key")
    rules = data["rules"]
    for i, rule in enumerate(rules):
        where = f"{path}#rules[{i}]"
        _check_keys(rule, RULE_KEYS, RULE_REQUIRED, where)
        for sym in rule["if"]:
            if sym not in symptom_ids:
                raise SchemaError(f"{where}: unknown symptom id '{sym}' in 'if'")
        if rule["then"] not in cause_ids:
            raise SchemaError(f"{where}: unknown cause id '{rule['then']}' in 'then'")
    return rules


SCENARIO_KEYS = {
    "id",
    "class",
    "domain",
    "presented_symptoms",
    "description",
    "expected_behavior",
    "reasoning_probe",
}
SCENARIO_REQUIRED = {"id", "class", "domain", "presented_symptoms"}


def load_scenarios(path: str | Path, symptom_ids: set[str]) -> list[dict]:
    """Load and validate `scenarios.json`. Returns the list of demo fixtures."""
    data = _read_json(path)
    if "scenarios" not in data:
        raise SchemaError(f"{path}: top-level object must contain a 'scenarios' key")
    scenarios = data["scenarios"]
    for i, scenario in enumerate(scenarios):
        where = f"{path}#scenarios[{i}]"
        _check_keys(scenario, SCENARIO_KEYS, SCENARIO_REQUIRED, where)
        for sym in scenario["presented_symptoms"]:
            if sym not in symptom_ids:
                raise SchemaError(f"{where}: unknown symptom id '{sym}' in 'presented_symptoms'")
    return scenarios


def load_all(data_dir: str | Path) -> dict[str, Any]:
    """Convenience loader: reads every KB file under `data_dir` at once."""
    data_dir = Path(data_dir)
    symptoms = load_symptoms(data_dir / "symptoms.json")
    causes = load_causes(data_dir / "causes.json")
    symptom_ids = {s["id"] for s in symptoms}
    cause_ids = {c["id"] for c in causes}
    rules = load_rules(data_dir / "rules.json", symptom_ids, cause_ids)
    scenarios = load_scenarios(data_dir / "scenarios.json", symptom_ids)
    return {
        "symptoms": symptoms,
        "causes": causes,
        "rules": rules,
        "scenarios": scenarios,
    }
