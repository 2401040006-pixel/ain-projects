"""Empty AI core stubs for Project 01 (Smart Campus Route Planner).

Implement BFS, Greedy Best-First Search, and A* here, plus at least one
heuristic function. Every public function below raises `NotImplementedError`
until you replace its body with your own implementation. Do not call a
hosted LLM to produce a route: see the auto-zero note in the instructor
rubric.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from graph import Graph  # noqa: E402

# (path of node ids from start to goal inclusive, or None) and the number of
# nodes popped from the frontier while searching (used by the required
# experiment to compare algorithms/heuristics).
PathResult = Tuple[Optional[List[str]], int]

Heuristic = Callable[[Graph, str, str], float]


def bfs(graph: Graph, start: str, goal: str) -> PathResult:
    """Breadth-First Search. Return `(path, expanded_node_count)`.

    `path` is a list of node ids from `start` to `goal` inclusive, or `None`
    if no path exists. Treat every edge in `graph.neighbors()` as usable
    (BFS does not apply blocked-edge or accessibility constraints).
    """
    raise NotImplementedError("Implement bfs() in student_core.py")


def euclidean_heuristic(graph: Graph, node_id: str, goal_id: str) -> float:
    """Straight-line distance heuristic using node `x`, `y` coordinates."""
    raise NotImplementedError("Implement euclidean_heuristic() in student_core.py")


def manhattan_heuristic(graph: Graph, node_id: str, goal_id: str) -> float:
    """Manhattan (|dx| + |dy|) distance heuristic using node `x`, `y` coordinates."""
    raise NotImplementedError("Implement manhattan_heuristic() in student_core.py")


def greedy(graph: Graph, start: str, goal: str, heuristic: Heuristic) -> PathResult:
    """Greedy Best-First Search ordered only by `heuristic`.

    Return `(path, expanded_node_count)`, same contract as `bfs()`.
    """
    raise NotImplementedError("Implement greedy() in student_core.py")


def astar(
    graph: Graph,
    start: str,
    goal: str,
    heuristic: Heuristic,
    edge_weight: str = "distance",
    blocked_edges: Optional[List[List[str]]] = None,
    accessible_only: bool = False,
) -> PathResult:
    """A* search using `heuristic` and the edge attribute named by
    `edge_weight` (`"distance"` or `"travel_time"`) as the step cost.

    `blocked_edges` is an optional list of `[a, b]` pairs (undirected) that
    must not be used. `accessible_only`, when True, restricts the search to
    edges where `edge.accessible` is True. Return `(path, expanded_node_count)`.
    """
    raise NotImplementedError("Implement astar() in student_core.py")
