"""Rendering helpers for the Streamlit starter UI.

This module only draws the grid; it contains no AI logic. Kept separate
from ``environment/gridworld.py`` so the environment package has no UI
dependency.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

from environment.gridworld import (
    CELL_DANGER,
    CELL_GOAL,
    CELL_PICKUP,
    CELL_START,
    CELL_WALL,
    GridWorld,
)

_CELL_COLORS = {
    CELL_START: "#BFDBFE",   # soft blue — start
    "EMPTY": "#F8FAFC",
    CELL_WALL: "#334155",    # slate — wall
    CELL_PICKUP: "#FDE68A",  # amber — pickup
    CELL_GOAL: "#86EFAC",    # green — goal
    CELL_DANGER: "#FCA5A5",  # rose — danger (distinct from goal)
}

_CELL_LABELS = {
    CELL_START: "S",
    "EMPTY": "",
    CELL_WALL: "",
    CELL_PICKUP: "P",
    CELL_GOAL: "G",
    CELL_DANGER: "D",
}


def plot_grid(env: GridWorld) -> Figure:
    """Return a matplotlib Figure showing the current grid and agent."""
    grid = env.cell_grid()
    height, width = env.height, env.width

    fig, ax = plt.subplots(figsize=(min(1.0 * width, 9), min(1.0 * height, 9)))
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.invert_yaxis()
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect("equal")

    for r in range(height):
        for c in range(width):
            cell_type = grid[r][c]
            color = _CELL_COLORS.get(cell_type, "#f8fafc")
            ax.add_patch(Rectangle((c, r), 1, 1, facecolor=color, edgecolor="#cbd5e1", linewidth=0.8))
            label = _CELL_LABELS.get(cell_type, "")
            if label:
                ax.text(c + 0.5, r + 0.5, label, ha="center", va="center", fontsize=9, color="#1e293b")

    agent_r, agent_c = env.position
    ax.add_patch(
        Rectangle(
            (agent_c + 0.15, agent_r + 0.15),
            0.7,
            0.7,
            facecolor="#2563EB" if env.state[2] else "#3B82F6",
            edgecolor="#1E3A8A",
            linewidth=1.2,
        )
    )
    ax.text(
        agent_c + 0.5,
        agent_r + 0.5,
        "@",
        ha="center",
        va="center",
        fontsize=10,
        color="white",
        fontweight="bold",
    )

    fig.tight_layout()
    return fig
