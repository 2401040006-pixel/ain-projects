"""Sanity tests for Project 04 (IT Troubleshooting Expert System).

These tests check that the provided data loads, that counts and
cross-references are valid, that the required demo fixtures exist, and
that the starter core is still unimplemented. They do **not** grade
any student's reasoning implementation.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
STARTER_DIR = PROJECT_ROOT / "starter"


def _load_module(module_name: str, file_path: Path):
    """Load a starter module under a project-unique name.

    `student_core.py` is a filename shared by every knowledge project in
    this kit, so importing it as a plain top-level `student_core` module
    would collide across projects when their tests run in the same
    pytest session. Loading by file path under a unique name avoids
    that collision regardless of test run order.
    """
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


rule_loader = _load_module("project04_rule_loader", STARTER_DIR / "rule_loader.py")
student_core = _load_module("project04_student_core", STARTER_DIR / "student_core.py")

REQUIRED_DEMO_CLASSES = {
    "single_cause",
    "ambiguous",
    "missing_info",
    "contradictory_symptoms",
}


def test_symptom_count_in_range():
    symptoms = rule_loader.load_symptoms(DATA_DIR / "symptoms.json")
    assert 20 <= len(symptoms) <= 30
    ids = [s["id"] for s in symptoms]
    assert len(ids) == len(set(ids))


def test_cause_count_in_range():
    causes = rule_loader.load_causes(DATA_DIR / "causes.json")
    assert 10 <= len(causes) <= 15
    ids = [c["id"] for c in causes]
    assert len(ids) == len(set(ids))


def test_rule_count_in_range_and_references_valid():
    symptoms = {s["id"] for s in rule_loader.load_symptoms(DATA_DIR / "symptoms.json")}
    causes = {c["id"] for c in rule_loader.load_causes(DATA_DIR / "causes.json")}
    rules = rule_loader.load_rules(DATA_DIR / "rules.json", symptoms, causes)
    assert 40 <= len(rules) <= 60
    for rule in rules:
        assert set(rule["if"]).issubset(symptoms)
        assert rule["then"] in causes


def test_scenario_count_and_required_demo_classes():
    symptoms = {s["id"] for s in rule_loader.load_symptoms(DATA_DIR / "symptoms.json")}
    scenarios = rule_loader.load_scenarios(DATA_DIR / "scenarios.json", symptoms)
    assert len(scenarios) == 15
    classes = {s["class"] for s in scenarios}
    assert REQUIRED_DEMO_CLASSES.issubset(classes)
    ids = [s["id"] for s in scenarios]
    assert len(ids) == len(set(ids))


def test_at_least_one_contradictory_scenario():
    symptoms = {s["id"] for s in rule_loader.load_symptoms(DATA_DIR / "symptoms.json")}
    scenarios = rule_loader.load_scenarios(DATA_DIR / "scenarios.json", symptoms)
    contradictory = [s for s in scenarios if s["class"] == "contradictory_symptoms"]
    assert len(contradictory) >= 1
    for scenario in contradictory:
        assert len(scenario["presented_symptoms"]) >= 2


def test_rule_loader_rejects_unknown_keys(tmp_path):
    bad_file = tmp_path / "symptoms.json"
    bad_file.write_text(
        json.dumps(
            {
                "symptoms": [
                    {
                        "id": "SYM999",
                        "domain": "wifi",
                        "description": "Bad symptom",
                        "unexpected_field": "should trigger rejection",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(rule_loader.SchemaError):
        rule_loader.load_symptoms(bad_file)


def test_rule_loader_rejects_unknown_symptom_reference(tmp_path):
    bad_file = tmp_path / "rules.json"
    bad_file.write_text(
        json.dumps({"rules": [{"id": "RBAD", "if": ["SYM_DOES_NOT_EXIST"], "then": "CAUSE01"}]}),
        encoding="utf-8",
    )
    with pytest.raises(rule_loader.SchemaError):
        rule_loader.load_rules(bad_file, symptom_ids={"SYM01"}, cause_ids={"CAUSE01"})


def test_load_all_smoke():
    kb = rule_loader.load_all(DATA_DIR)
    assert set(kb.keys()) == {"symptoms", "causes", "rules", "scenarios"}


@pytest.mark.parametrize(
    "call",
    [
        lambda: student_core.infer(["SYM01"], []),
        lambda: student_core.explain("CAUSE01", ["SYM01"], []),
    ],
)
def test_student_core_is_not_implemented(call):
    with pytest.raises(NotImplementedError):
        call()
