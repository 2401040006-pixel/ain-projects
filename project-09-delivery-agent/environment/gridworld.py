"""Deterministic pickup-and-deliver gridworld environment.

This module is infrastructure only: it loads maps, applies deterministic
transitions, and computes rewards from a documented reward table. It does
**not** implement Q-learning or any action-selection policy. Students
implement ``select_action`` and ``q_learning`` in ``starter/student_core.py``
and drive this environment with them.

State
-----
A state is the tuple ``(row, col, has_package)``. ``has_package`` becomes
``True`` the first time the agent steps on a PICKUP cell and stays ``True``
for the rest of the episode (packages are not consumed by DANGER).

Transitions
-----------
Transitions are fully deterministic: given a state and an action, the next
state is always the same. The only "random" part of the environment is
whatever policy chooses the action (e.g. a random policy, or an
epsilon-greedy policy over a learned Q-table). Moving into a WALL or off
the grid leaves the agent in place and applies ``wall_bump_cost``. Moving
onto a DANGER cell always applies ``danger_penalty``, deterministically,
every time — there is no probability roll involved.

Reward design
--------------
Rewards are not hard-coded constants: they are read from
``environment/config.json`` (or an explicit override), so the required
midterm experiment ("change at least two of alpha, gamma, epsilon, reward
design") can be run by swapping presets or fields without touching this
file. Reaching GOAL without the package pays ``goal_without_package_reward``
(not ``goal_reward``), which makes the pickup step a real trade-off against
the per-step cost rather than a shortcut-able formality.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ENV_DIR = Path(__file__).resolve().parent
MAPS_DIR = ENV_DIR / "maps"
CONFIG_PATH = ENV_DIR / "config.json"

CELL_START = "START"
CELL_EMPTY = "EMPTY"
CELL_WALL = "WALL"
CELL_PICKUP = "PICKUP"
CELL_GOAL = "GOAL"
CELL_DANGER = "DANGER"

VALID_CELL_TYPES = {
    CELL_START,
    CELL_EMPTY,
    CELL_WALL,
    CELL_PICKUP,
    CELL_GOAL,
    CELL_DANGER,
}

ACTIONS: Tuple[str, ...] = ("UP", "DOWN", "LEFT", "RIGHT")

_ACTION_DELTAS: Dict[str, Tuple[int, int]] = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1),
}

State = Tuple[int, int, bool]


def load_config(path: Path = CONFIG_PATH) -> dict:
    """Load the shared environment config (actions, rewards, presets)."""
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def list_maps(maps_dir: Path = MAPS_DIR) -> List[str]:
    """Return the sorted list of available map names (without .json)."""
    return sorted(p.stem for p in maps_dir.glob("*.json"))


def list_reward_presets(config: Optional[dict] = None) -> List[str]:
    """Return the reward preset names declared in config.json."""
    config = config if config is not None else load_config()
    return sorted(config.get("reward_presets", {}).keys())


def load_map(name: str, maps_dir: Path = MAPS_DIR) -> dict:
    """Load and validate a map definition by name (without .json suffix)."""
    map_path = maps_dir / f"{name}.json"
    if not map_path.exists():
        available = ", ".join(list_maps(maps_dir)) or "<none found>"
        raise FileNotFoundError(
            f"Unknown map '{name}': {map_path} does not exist. Available maps: {available}"
        )
    with open(map_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    _validate_map(data)
    return data


def _validate_map(data: dict) -> None:
    if "grid" not in data or "legend" not in data:
        raise ValueError("Map must define both 'grid' and 'legend'")
    legend = data["legend"]
    for symbol, cell_type in legend.items():
        if cell_type not in VALID_CELL_TYPES:
            raise ValueError(f"Unknown cell type '{cell_type}' for symbol '{symbol}'")
    rows = data["grid"]
    if not rows:
        raise ValueError("Map grid must have at least one row")
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("Grid rows must all have the same width")
    start_count = sum(
        row.count(symbol)
        for row in rows
        for symbol, cell_type in legend.items()
        if cell_type == CELL_START
    )
    if start_count != 1:
        raise ValueError(f"Grid must contain exactly one START cell, found {start_count}")
    pickup_count = sum(
        row.count(symbol)
        for row in rows
        for symbol, cell_type in legend.items()
        if cell_type == CELL_PICKUP
    )
    goal_count = sum(
        row.count(symbol)
        for row in rows
        for symbol, cell_type in legend.items()
        if cell_type == CELL_GOAL
    )
    if pickup_count < 1:
        raise ValueError("Grid must contain at least one PICKUP cell")
    if goal_count < 1:
        raise ValueError("Grid must contain at least one GOAL cell")


@dataclass
class StepResult:
    """Outcome of a single ``GridWorld.step`` call."""

    state: State
    reward: float
    done: bool
    info: Dict[str, object] = field(default_factory=dict)


class GridWorld:
    """A deterministic pickup-and-deliver gridworld.

    Parameters
    ----------
    map_name:
        Name of a map file under ``environment/maps/`` (without ``.json``).
    reward_preset:
        Name of a preset from ``config.json`` ``reward_presets`` (e.g.
        ``"default"``, ``"bad_reward"``, ``"improved_reward"``). Ignored if
        ``reward_overrides`` is also given a full reward table.
    reward_overrides:
        Optional dict merged on top of the chosen preset's reward table, for
        ad-hoc experiments (the required "change reward design" experiment).
    """

    actions: Tuple[str, ...] = ACTIONS

    def __init__(
        self,
        map_name: str = "easy",
        reward_preset: str = "default",
        reward_overrides: Optional[dict] = None,
        maps_dir: Path = MAPS_DIR,
        config_path: Path = CONFIG_PATH,
    ) -> None:
        self.map_name = map_name
        self.map_data = load_map(map_name, maps_dir=maps_dir)
        self.grid: List[str] = list(self.map_data["grid"])
        self.legend: Dict[str, str] = self.map_data["legend"]
        self.height = len(self.grid)
        self.width = len(self.grid[0])

        config = load_config(config_path)
        presets = config.get("reward_presets", {})
        if reward_preset not in presets:
            available = ", ".join(sorted(presets)) or "<none found>"
            raise ValueError(f"Unknown reward preset '{reward_preset}'. Available: {available}")
        self.reward_preset = reward_preset
        self.rewards: Dict[str, float] = {
            k: v for k, v in presets[reward_preset].items() if not k.startswith("_")
        }
        if reward_overrides:
            self.rewards.update(reward_overrides)
        self.danger_terminates_episode: bool = bool(
            self.rewards.pop("danger_terminates_episode", config.get("danger_terminates_episode", True))
        )
        self.max_steps = self.height * self.width * config.get("max_steps_multiplier", 6)

        self._start = self._find_unique(CELL_START)
        self._pickups = self._find_all(CELL_PICKUP)
        self._goals = self._find_all(CELL_GOAL)
        self._dangers = self._find_all(CELL_DANGER)

        self._pos = self._start
        self._has_package = False
        self._picked_up: set = set()
        self._steps = 0
        self._done = False
        self.reset()

    # -- map introspection ------------------------------------------------
    def cell_type(self, row: int, col: int) -> str:
        symbol = self.grid[row][col]
        return self.legend.get(symbol, CELL_EMPTY)

    def _find_unique(self, cell_type: str) -> Tuple[int, int]:
        matches = self._find_all(cell_type)
        if len(matches) != 1:
            raise ValueError(f"Expected exactly one {cell_type} cell, found {len(matches)}")
        return matches[0]

    def _find_all(self, cell_type: str) -> List[Tuple[int, int]]:
        found = []
        for r, row in enumerate(self.grid):
            for c, symbol in enumerate(row):
                if self.legend.get(symbol, CELL_EMPTY) == cell_type:
                    found.append((r, c))
        return found

    @property
    def danger_cells(self) -> List[Tuple[int, int]]:
        return list(self._dangers)

    @property
    def pickup_cells(self) -> List[Tuple[int, int]]:
        return list(self._pickups)

    @property
    def goal_cells(self) -> List[Tuple[int, int]]:
        return list(self._goals)

    # -- episode lifecycle -------------------------------------------------
    def reset(self) -> State:
        """Reset the agent to START with no package and zero steps."""
        self._pos = self._start
        self._has_package = False
        self._picked_up = set()
        self._steps = 0
        self._done = False
        return self.state

    @property
    def state(self) -> State:
        return (self._pos[0], self._pos[1], self._has_package)

    @property
    def position(self) -> Tuple[int, int]:
        return self._pos

    @property
    def steps_taken(self) -> int:
        return self._steps

    def is_terminal(self) -> bool:
        return self._done

    def step(self, action: str) -> StepResult:
        """Apply ``action`` and return the resulting ``StepResult``.

        Deterministic: the same (state, action) pair always produces the
        same next state and reward for a fixed reward table.
        """
        if self._done:
            raise RuntimeError("Episode has ended; call reset() before stepping again.")
        if action not in _ACTION_DELTAS:
            raise ValueError(f"Unknown action '{action}'. Valid actions: {self.actions}")

        dr, dc = _ACTION_DELTAS[action]
        r, c = self._pos
        nr, nc = r + dr, c + dc

        reward = float(self.rewards["step_cost"])
        info: Dict[str, object] = {
            "bumped_wall": False,
            "picked_up": False,
            "delivered": False,
            "hit_danger": False,
            "timed_out": False,
        }

        out_of_bounds = not (0 <= nr < self.height and 0 <= nc < self.width)
        if out_of_bounds or self.cell_type(nr, nc) == CELL_WALL:
            nr, nc = r, c
            reward += self.rewards["wall_bump_cost"]
            info["bumped_wall"] = True

        self._pos = (nr, nc)
        cell = self.cell_type(nr, nc)

        if cell == CELL_PICKUP and (nr, nc) not in self._picked_up:
            self._picked_up.add((nr, nc))
            self._has_package = True
            reward += self.rewards["pickup_reward"]
            info["picked_up"] = True
        elif cell == CELL_DANGER:
            reward += self.rewards["danger_penalty"]
            info["hit_danger"] = True
            if self.danger_terminates_episode:
                self._done = True
        elif cell == CELL_GOAL:
            if self._has_package:
                reward += self.rewards["goal_reward"]
                info["delivered"] = True
                self._done = True
            else:
                reward += self.rewards.get("goal_without_package_reward", 0)

        self._steps += 1
        if not self._done and self._steps >= self.max_steps:
            self._done = True
            info["timed_out"] = True

        return StepResult(state=self.state, reward=reward, done=self._done, info=info)

    # -- rendering helpers ---------------------------------------------------
    def render_ascii(self) -> str:
        """Return a plain-text rendering with '@' marking the agent."""
        rows = []
        for r, row in enumerate(self.grid):
            chars = []
            for c, symbol in enumerate(row):
                chars.append("@" if (r, c) == self._pos else symbol)
            rows.append("".join(chars))
        return "\n".join(rows)

    def cell_grid(self) -> List[List[str]]:
        """Return the grid as a 2D list of cell-type strings (for plotting)."""
        return [[self.cell_type(r, c) for c in range(self.width)] for r in range(self.height)]
