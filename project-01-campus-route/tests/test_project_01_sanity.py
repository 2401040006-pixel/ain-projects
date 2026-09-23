"""Sanity tests for Project 01 (Smart Campus Route Planner).

These tests check data integrity, loader behavior, and that the starter
does NOT ship a working search core. They do not grade the student's AI.
"""
from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path

import pytest

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
STARTER_DIR = PROJECT_DIR / "starter"

sys.path.insert(0, str(STARTER_DIR))

import graph as graph_module  # noqa: E402


def _load_module(name: str, path: Path):
    """Load a module under a unique name so `starter/student_core.py`
    (which also exists in project-02) never collides via `sys.modules`
    when both projects' sanity tests run in the same pytest session."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


student_core = _load_module("project01_student_core", STARTER_DIR / "student_core.py")


# ---------------------------------------------------------------------------
# Data files
# ---------------------------------------------------------------------------


def test_data_files_exist():
    for name in ["nodes.csv", "edges.csv", "scenarios.json", "campus_map.png", "SHA256SUMS", "README.md"]:
        assert (DATA_DIR / name).exists(), f"missing data/{name}"


def test_nodes_csv_schema_and_size():
    with open(DATA_DIR / "nodes.csv", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        assert reader.fieldnames == [
            "node_id",
            "name",
            "x",
            "y",
            "floor",
            "building",
            "node_type",
        ]
        rows = list(reader)
    assert 30 <= len(rows) <= 60, f"expected 30-60 nodes, got {len(rows)}"
    ids = [r["node_id"] for r in rows]
    assert len(ids) == len(set(ids)), "duplicate node_id values"


def test_edges_csv_schema_and_size():
    with open(DATA_DIR / "edges.csv", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        assert reader.fieldnames == [
            "source",
            "target",
            "distance",
            "travel_time",
            "crowd_level",
            "stairs",
            "indoor",
            "accessible",
        ]
        rows = list(reader)
    assert 50 <= len(rows) <= 120, f"expected 50-120 edges, got {len(rows)}"


def test_edges_reference_known_nodes():
    with open(DATA_DIR / "nodes.csv", newline="", encoding="utf-8") as fh:
        node_ids = {row["node_id"] for row in csv.DictReader(fh)}
    with open(DATA_DIR / "edges.csv", newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            assert row["source"] in node_ids
            assert row["target"] in node_ids


def test_scenarios_json_covers_required_classes():
    with open(DATA_DIR / "scenarios.json", encoding="utf-8") as fh:
        data = json.load(fh)
    scenarios = data["scenarios"]
    ids = {s["id"] for s in scenarios}
    for required_id in [
        "S1_normal_route",
        "S2_blocked_edge",
        "S3_accessibility_mode",
        "S4_heuristic_comparison",
        "S5_accessibility_no_path",
    ]:
        assert required_id in ids, f"missing scenario id {required_id}"

    normal = next(s for s in scenarios if s["id"] == "S1_normal_route")
    blocked = next(s for s in scenarios if s["id"] == "S2_blocked_edge")
    accessible = next(s for s in scenarios if s["id"] == "S3_accessibility_mode")
    comparison = next(s for s in scenarios if s["id"] == "S4_heuristic_comparison")

    assert "blocked_edges" in blocked["constraints"]
    assert accessible["constraints"].get("accessible_only") is True
    assert len(comparison.get("heuristics", [])) >= 2
    assert normal["start"] and normal["end"]


def test_sha256sums_match_committed_data():
    import hashlib

    expected = {}
    with open(DATA_DIR / "SHA256SUMS", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            digest, name = line.split("  ", 1)
            expected[name] = digest

    for name in ["nodes.csv", "edges.csv", "scenarios.json"]:
        actual = hashlib.sha256((DATA_DIR / name).read_bytes()).hexdigest()
        assert actual == expected[name], f"{name} does not match SHA256SUMS"


# ---------------------------------------------------------------------------
# Starter graph loader (no search allowed here)
# ---------------------------------------------------------------------------


def test_graph_loads_and_has_neighbors():
    g = graph_module.load_graph()
    summary = g.summary()
    assert 30 <= summary["num_nodes"] <= 60
    assert 50 <= summary["num_edges"] <= 120

    any_node = g.node_ids[0]
    neighbors = g.neighbors(any_node)
    assert isinstance(neighbors, list)
    for edge in neighbors:
        assert edge.source == any_node or edge.target == any_node


def test_graph_unknown_node_raises_keyerror():
    g = graph_module.load_graph()
    with pytest.raises(KeyError):
        g.get_node("N999_does_not_exist")


def test_graph_module_has_no_search_functions():
    forbidden = {"bfs", "greedy", "astar", "dfs"}
    defined = {name for name in dir(graph_module) if not name.startswith("_")}
    leaked = forbidden & defined
    assert not leaked, f"starter/graph.py must not define search functions: {leaked}"


# ---------------------------------------------------------------------------
# Starter core stubs (must be empty)
# ---------------------------------------------------------------------------


def test_student_core_stubs_raise_not_implemented():
    g = graph_module.load_graph()
    node_ids = g.node_ids
    start, goal = node_ids[0], node_ids[-1]

    with pytest.raises(NotImplementedError):
        student_core.bfs(g, start, goal)

    with pytest.raises(NotImplementedError):
        student_core.euclidean_heuristic(g, start, goal)

    with pytest.raises(NotImplementedError):
        student_core.manhattan_heuristic(g, start, goal)

    with pytest.raises(NotImplementedError):
        student_core.greedy(g, start, goal, lambda graph, a, b: 0.0)

    with pytest.raises(NotImplementedError):
        student_core.astar(g, start, goal, lambda graph, a, b: 0.0)


def test_no_pygame_dependency():
    requirements = (PROJECT_DIR / "requirements.txt").read_text(encoding="utf-8").lower()
    assert "pygame" not in requirements, "project 01 must not require pygame"
