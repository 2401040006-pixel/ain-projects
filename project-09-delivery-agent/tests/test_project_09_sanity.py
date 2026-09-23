"""Sanity tests for Project 09 (Delivery Agent).

These tests check that the environment loads, that a random policy can
walk every map to completion, and that the graded AI core
(``starter/student_core.py``) is still empty. They do not grade a
student's Q-learning implementation.
"""

from __future__ import annotations

import importlib.util
import random
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _load_module(unique_name: str, path: Path):
    """Load a module from an explicit file path under a project-unique
    name. Project 9 and Project 10 both ship a `starter` package; loading
    by path (instead of `sys.path` + `import starter`) avoids a module-name
    collision when both projects' tests run in the same pytest session."""
    spec = importlib.util.spec_from_file_location(unique_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[unique_name] = module  # required for dataclasses' postponed-annotation lookup
    spec.loader.exec_module(module)
    return module


_gridworld = _load_module("project09_environment_gridworld", PROJECT_ROOT / "environment" / "gridworld.py")
GridWorld = _gridworld.GridWorld
list_maps = _gridworld.list_maps
list_reward_presets = _gridworld.list_reward_presets
load_config = _gridworld.load_config
load_map = _gridworld.load_map

student_core = _load_module("project09_starter_student_core", PROJECT_ROOT / "starter" / "student_core.py")

MAPS = ["easy", "medium", "hard"]


def test_all_expected_maps_exist():
    assert set(MAPS).issubset(set(list_maps()))


@pytest.mark.parametrize("map_name", MAPS)
def test_map_loads_and_validates(map_name):
    data = load_map(map_name)
    assert data["grid"], f"{map_name}: grid must not be empty"
    width = len(data["grid"][0])
    assert all(len(row) == width for row in data["grid"]), f"{map_name}: ragged grid rows"


def test_easy_map_has_no_danger():
    env = GridWorld(map_name="easy", reward_preset="default")
    assert env.danger_cells == [], "easy map must have no DANGER cells"


@pytest.mark.parametrize("map_name", ["medium", "hard"])
def test_danger_maps_document_danger_zones(map_name):
    env = GridWorld(map_name=map_name, reward_preset="default")
    assert len(env.danger_cells) >= 1, f"{map_name} map must include at least one DANGER cell"


def test_reward_presets_include_bad_and_improved():
    presets = set(list_reward_presets())
    assert {"default", "bad_reward", "improved_reward"}.issubset(presets)


def test_config_has_four_actions():
    config = load_config()
    assert set(config["actions"]) == {"UP", "DOWN", "LEFT", "RIGHT"}


@pytest.mark.parametrize("map_name", MAPS)
def test_random_policy_can_walk_the_grid_to_completion(map_name):
    """A uniformly random policy must reach a terminal state (GOAL, DANGER
    termination, or timeout) within max_steps, on every map. This is the
    project's stated success criterion: "random agent can walk the grid"."""
    random.seed(0)
    env = GridWorld(map_name=map_name, reward_preset="default")
    steps = 0
    while not env.is_terminal() and steps < env.max_steps:
        env.step(random.choice(env.actions))
        steps += 1
    assert env.is_terminal(), f"{map_name}: random policy never reached a terminal state"


def test_environment_is_deterministic_given_fixed_actions():
    """Same action sequence from a fresh reset must produce identical
    states and rewards both times (no hidden randomness in transitions)."""
    action_sequence = ["RIGHT", "RIGHT", "DOWN", "DOWN", "LEFT", "UP", "RIGHT", "DOWN"]

    def run(env):
        env.reset()
        trace = []
        for action in action_sequence:
            if env.is_terminal():
                break
            result = env.step(action)
            trace.append((result.state, result.reward, result.done))
        return trace

    env_a = GridWorld(map_name="medium", reward_preset="default")
    env_b = GridWorld(map_name="medium", reward_preset="default")
    assert run(env_a) == run(env_b)


def test_wall_bump_keeps_agent_in_place():
    env = GridWorld(map_name="easy", reward_preset="default")
    # (0, 0) moving UP goes off-grid -> treated like a wall bump, stays put.
    result = env.step("UP")
    assert result.state[:2] == (0, 0)
    assert result.info["bumped_wall"] is True


def test_goal_without_package_does_not_pay_goal_reward():
    """On the easy map, START (0,0) -> GOAL (4,6) via row 0 then column 6
    never touches PICKUP (2,2), so reaching GOAL there must not pay the
    full goal_reward."""
    env = GridWorld(map_name="easy", reward_preset="default")
    assert env.goal_cells[0] == (4, 6)
    result = None
    for _ in range(6):
        result = env.step("RIGHT")
    for _ in range(4):
        result = env.step("DOWN")
    assert env.state == (4, 6, False)
    assert result.info["delivered"] is False
    assert result.reward != env.rewards["goal_reward"]


def test_bad_reward_preset_removes_step_and_danger_cost():
    env = GridWorld(map_name="medium", reward_preset="bad_reward")
    assert env.rewards["step_cost"] == 0
    assert env.rewards["danger_penalty"] == 0


def test_improved_reward_preset_restores_costs():
    env = GridWorld(map_name="medium", reward_preset="improved_reward")
    assert env.rewards["step_cost"] < 0
    assert env.rewards["danger_penalty"] < 0
    assert env.danger_terminates_episode is True


# -- forbidden-core guards ---------------------------------------------------


def test_select_action_is_not_implemented():
    with pytest.raises(NotImplementedError):
        student_core.select_action((0, 0, False), {}, ("UP", "DOWN", "LEFT", "RIGHT"), 0.1)


def test_q_learning_is_not_implemented():
    env = GridWorld(map_name="easy", reward_preset="default")
    with pytest.raises(NotImplementedError):
        student_core.q_learning(env, episodes=1, alpha=0.1, gamma=0.9, epsilon=0.1)


def test_no_pygame_import_anywhere_in_project():
    project_root = PROJECT_ROOT
    this_file = Path(__file__).resolve()
    offenders = []
    for path in project_root.rglob("*.py"):
        if ".venv" in path.parts or path.resolve() == this_file:
            continue
        text = path.read_text(encoding="utf-8")
        if "import pygame" in text or "pygame" in path.name:
            offenders.append(str(path))
    assert not offenders, f"pygame must not be used in Project 09: {offenders}"


def test_no_trained_weight_artifacts_in_project():
    project_root = PROJECT_ROOT
    forbidden_suffixes = (".pkl", ".pt", ".joblib")
    offenders = [
        str(p)
        for p in project_root.rglob("*")
        if p.is_file() and (p.suffix in forbidden_suffixes or p.name == "qtable.json")
    ]
    assert not offenders, f"No trained weights/Q-tables may ship in the starter tree: {offenders}"


def test_requirements_do_not_include_pygame():
    requirements_path = PROJECT_ROOT / "requirements.txt"
    text = requirements_path.read_text(encoding="utf-8").lower()
    assert "pygame" not in text
