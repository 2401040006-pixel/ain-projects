# Data dictionary — Project 01 (Smart Campus Route Planner)

All data here is a **synthetic multi-building campus graph** for wayfinding
exercises. Coordinates are 2D schematic units used for graph visualization
and heuristic calculations.

## Regenerating

```bash
python scripts/generate_campus.py --seed 42
```

The default seed is **42**. Re-running with `--seed 42` reproduces
byte-identical `nodes.csv`, `edges.csv`, and `scenarios.json`, matching the
hashes committed in `SHA256SUMS`. `campus_map.png` is redrawn each run but is
not part of the hash check (pixel-identical output is not required).

## Files

| File | Purpose |
|---|---|
| `nodes.csv` | Every location in the campus graph (54 nodes) |
| `edges.csv` | Every connection between two locations (75 edges) |
| `scenarios.json` | Named demo/experiment queries (start, end, constraints) |
| `campus_map.png` | Detailed schematic wayfinding map of the campus |
| `SHA256SUMS` | sha256 of `nodes.csv`, `edges.csv`, `scenarios.json` |

## `nodes.csv`

```text
node_id,name,x,y,floor,building,node_type
```

- `node_id`: unique id, e.g. `N_GATE`, `N_C_101`, `W_CROSS_EAST`.
- `name`: human-readable label as stored in the CSV.
- `x`, `y`: schematic 2D coordinates (aligned with North $\uparrow$), used by `campus_map.png`
  and by any heuristic that needs straight-line distance.
- `floor`: integer floor number. `0` is reserved for outdoor plazas, roads, and parkings.
- `building`: building or zone name as stored in the CSV, or `Campus Grounds`
  for outdoor grounds, parkings, and walkways.
- `node_type`: one of `plaza`, `entrance`, `hallway`, `room`.

## `edges.csv`

```text
source,target,distance,travel_time,crowd_level,stairs,indoor,accessible
```

- `source`, `target`: `node_id` values. Edges are **undirected**: traverse
  either direction with the same cost and constraints.
- `distance`: schematic Euclidean distance between the two nodes (meters).
- `travel_time`: realistic travel time in seconds, penalizing stairs and crowd levels.
- `crowd_level`: one of `low`, `medium`, `high`.
- `stairs`: `True`/`False` — a stairs-only vertical connector.
- `indoor`: `True`/`False`.
- `accessible`: `True`/`False` — usable when accessibility mode is on.
  Elevator connectors (`stairs=False, accessible=True`) parallel stairs connectors
  between floors, so an accessible route exists across campus **except** for
  the deliberately isolated room `N_C_ATTIC`
  (see `scenarios.json`, scenario `S5_accessibility_no_path`) reachable only via
  a non-accessible steep staircase.

A node pair may appear more than once in `edges.csv` (for example a stairs
edge and an elevator edge between the same two floor nodes). Treat each
row as a distinct edge, not a deduplicated adjacency.

## `scenarios.json`

A JSON object with `seed`, `generated_by`, and a `scenarios` list. Each
scenario has an `id`, a `class` (`normal`, `difficult`, `failure`, or
`extra`), a `start`/`end` node id pair, a `constraints` object
(`blocked_edges`, `accessible_only`), and a `description`.

## Scale

Committed scale: **54 nodes**, **75 edges**, spanning **13 buildings and zones**
with **1-3 floors**. Meets the course requirement of 30-60 nodes and 50-120 edges.
