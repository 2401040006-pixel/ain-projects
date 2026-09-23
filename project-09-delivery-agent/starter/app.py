"""Streamlit starter simulator — Project 09 (Delivery Agent).

This app is infrastructure only: it lets you pick a map and a reward
preset, then step a **random** policy through the grid so you can see the
environment work before you write any learning code. It deliberately does
**not** implement Q-learning; the "Train agent" button calls the student
core and shows the resulting ``NotImplementedError`` until you fill in
``starter/student_core.py``.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import streamlit as st

# Allow `streamlit run starter/app.py` to import the sibling `environment`
# package regardless of the current working directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from environment.gridworld import GridWorld, list_maps, list_reward_presets  # noqa: E402
from starter import student_core  # noqa: E402
from starter.visualization import plot_grid  # noqa: E402

st.set_page_config(page_title="Autonomous Campus Delivery Agent — starter", layout="wide")
st.title("Autonomous Campus Delivery Agent — starter")
st.markdown(
    "The **Q-learning core is student work**. This page only demonstrates a "
    "**random** policy walking the deterministic grid; it does not search, "
    "learn, or call a hosted model."
)


def _get_env(map_name: str, preset: str) -> GridWorld:
    key = (map_name, preset)
    if st.session_state.get("_env_key") != key:
        st.session_state["_env_key"] = key
        st.session_state["env"] = GridWorld(map_name=map_name, reward_preset=preset)
        st.session_state["episode_reward"] = 0.0
        st.session_state["log"] = []
    return st.session_state["env"]


with st.sidebar:
    st.header("Controls")
    map_name = st.selectbox("Map", list_maps(), index=0)
    preset = st.selectbox("Reward preset", list_reward_presets(), index=0)
    st.caption(
        "`bad_reward` removes the step cost and danger penalty (reward "
        "hacking demo). `improved_reward` restores both plus a small "
        "penalty for reaching GOAL without the package."
    )
    if st.button("Reset episode"):
        st.session_state["_env_key"] = None

env = _get_env(map_name, preset)

col_grid, col_info = st.columns([2, 1])

with col_grid:
    st.pyplot(plot_grid(env), clear_figure=True)
    st.caption(
        "Legend: **S** = START · **P** = PICKUP · **G** = GOAL · **D** = DANGER · "
        "dark cell = WALL · **@** = agent"
    )

with col_info:
    st.subheader("State")
    r, c, has_package = env.state
    st.write(f"Position: `({r}, {c})`")
    st.write(f"Carrying package: `{has_package}`")
    st.write(f"Steps taken: `{env.steps_taken}` / `{env.max_steps}`")
    st.write(f"Episode reward so far: `{st.session_state['episode_reward']:.1f}`")
    st.write(f"Episode done: `{env.is_terminal()}`")

    st.subheader("Random policy")
    step_disabled = env.is_terminal()
    if st.button("Step random policy", disabled=step_disabled):
        action = random.choice(env.actions)
        result = env.step(action)
        st.session_state["episode_reward"] += result.reward
        st.session_state["log"].insert(
            0, f"action={action} reward={result.reward:+.1f} info={result.info}"
        )
    if step_disabled:
        st.info("Episode finished. Click 'Reset episode' to run another one.")

    st.subheader("Train agent (Q-learning)")
    st.caption("Calls your `starter/student_core.q_learning`. Empty until you implement it.")
    episodes = st.number_input("Episodes", min_value=1, max_value=5000, value=200, step=50)
    alpha = st.slider("alpha (learning rate)", 0.0, 1.0, 0.1)
    gamma = st.slider("gamma (discount factor)", 0.0, 1.0, 0.9)
    epsilon = st.slider("epsilon (exploration rate)", 0.0, 1.0, 0.2)
    if st.button("Train"):
        try:
            training_env = GridWorld(map_name=map_name, reward_preset=preset)
            q_table = student_core.q_learning(
                training_env, episodes=int(episodes), alpha=alpha, gamma=gamma, epsilon=epsilon
            )
            st.success(f"Trained a Q-table with {len(q_table)} entries.")
        except NotImplementedError as exc:
            st.error(f"Not implemented yet: {exc}")

st.subheader("Recent steps")
for line in st.session_state["log"][:15]:
    st.text(line)
