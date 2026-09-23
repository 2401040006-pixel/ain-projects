"""Load the campus graph and answer neighbor queries.

This module only loads `data/nodes.csv` and `data/edges.csv` and exposes a
`Graph` object with `get_node()` and `neighbors()`. It intentionally does
**not** implement any search algorithm (no BFS, no Greedy Best-First Search,
no A*). That AI core is your own work in `student_core.py`.
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _to_bool(value: str) -> bool:
    return str(value).strip().lower() in ("true", "1", "yes")


@dataclass(frozen=True)
class Node:
    node_id: str
    name: str
    x: float
    y: float
    floor: int
    building: str
    node_type: str


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    distance: float
    travel_time: float
    crowd_level: str
    stairs: bool
    indoor: bool
    accessible: bool


class Graph:
    """Undirected campus graph: node lookup plus neighbor lists.

    Two hallway nodes on adjacent floors of the same building may appear as
    neighbors of each other more than once (e.g. once via a stairs edge and
    once via an elevator edge) -- `neighbors()` returns every incident edge,
    not a deduplicated set of neighbor ids.
    """

    def __init__(self, nodes: Dict[str, Node], adjacency: Dict[str, List[Edge]]):
        self._nodes = nodes
        self._adjacency = adjacency

    @property
    def node_ids(self) -> List[str]:
        return list(self._nodes.keys())

    def get_node(self, node_id: str) -> Node:
        try:
            return self._nodes[node_id]
        except KeyError as exc:
            raise KeyError(f"Unknown node id: {node_id!r}") from exc

    def neighbors(self, node_id: str) -> List[Edge]:
        """Return every Edge incident to `node_id` (undirected)."""
        if node_id not in self._nodes:
            raise KeyError(f"Unknown node id: {node_id!r}")
        return list(self._adjacency.get(node_id, []))

    def summary(self) -> Dict[str, object]:
        buildings = sorted({n.building for n in self._nodes.values()})
        floors = sorted({n.floor for n in self._nodes.values()})
        num_edges = sum(len(v) for v in self._adjacency.values()) // 2
        return {
            "num_nodes": len(self._nodes),
            "num_edges": num_edges,
            "buildings": buildings,
            "floors": floors,
        }


def load_nodes(path: Path) -> Dict[str, Node]:
    nodes: Dict[str, Node] = {}
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            node = Node(
                node_id=row["node_id"],
                name=row["name"],
                x=float(row["x"]),
                y=float(row["y"]),
                floor=int(row["floor"]),
                building=row["building"],
                node_type=row["node_type"],
            )
            nodes[node.node_id] = node
    return nodes


def load_edges(path: Path, nodes: Dict[str, Node]) -> Dict[str, List[Edge]]:
    adjacency: Dict[str, List[Edge]] = {node_id: [] for node_id in nodes}
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            edge = Edge(
                source=row["source"],
                target=row["target"],
                distance=float(row["distance"]),
                travel_time=float(row["travel_time"]),
                crowd_level=row["crowd_level"],
                stairs=_to_bool(row["stairs"]),
                indoor=_to_bool(row["indoor"]),
                accessible=_to_bool(row["accessible"]),
            )
            if edge.source not in nodes or edge.target not in nodes:
                raise ValueError(
                    f"Edge references unknown node: {edge.source} -> {edge.target}"
                )
            adjacency.setdefault(edge.source, []).append(edge)
            reverse = Edge(
                source=edge.target,
                target=edge.source,
                distance=edge.distance,
                travel_time=edge.travel_time,
                crowd_level=edge.crowd_level,
                stairs=edge.stairs,
                indoor=edge.indoor,
                accessible=edge.accessible,
            )
            adjacency.setdefault(edge.target, []).append(reverse)
    return adjacency


def load_graph(data_dir: Optional[Path] = None) -> Graph:
    data_dir = Path(data_dir) if data_dir else DEFAULT_DATA_DIR
    nodes = load_nodes(data_dir / "nodes.csv")
    adjacency = load_edges(data_dir / "edges.csv", nodes)
    return Graph(nodes, adjacency)


def load_scenarios(data_dir: Optional[Path] = None) -> dict:
    data_dir = Path(data_dir) if data_dir else DEFAULT_DATA_DIR
    with open(data_dir / "scenarios.json", encoding="utf-8") as fh:
        return json.load(fh)
