"""Streamlit skeleton for Project 08 (Smart Team Formation Optimizer).

This page loads the committed students, lets the user pick a team size and
the four objective weights, and shows the random baseline. It does **not**
compute the objective or search for better teams: clicking "Optimize teams"
calls your `student_core.py` functions, which raise `NotImplementedError`
until you implement them.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

import loader
import student_core

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

st.set_page_config(page_title="Smart Team Formation Optimizer — starter", layout="wide")
st.title("Smart Team Formation Optimizer — starter")
st.markdown(
    "The **AI core is student work**. This page loads students and shows a "
    "random baseline, but it must not compute the objective, run Hill "
    "Climbing, or run Simulated Annealing on its own. Fill "
    "`student_core.py` in your own code."
)
st.caption(loader.SYNTHETIC_DATA_NOTICE)

config = loader.load_config()
scenarios = loader.load_scenarios()
students = loader.load_students()
by_id = loader.students_by_id(students)

with st.sidebar:
    st.header("Controls")
    team_size = st.slider(
        "Team size",
        min_value=config["team_size_min"],
        max_value=config["team_size_max"],
        value=config["team_size_min"],
    )
    st.subheader("Objective weights")
    st.caption("These are not fixed by the data pack -- choose and justify your own.")
    w1 = st.slider("w1 — skill imbalance", 0.0, 1.0, 0.25, 0.05)
    w2 = st.slider("w2 — schedule conflict", 0.0, 1.0, 0.25, 0.05)
    w3 = st.slider("w3 — role imbalance", 0.0, 1.0, 0.25, 0.05)
    w4 = st.slider("w4 — team-size penalty", 0.0, 1.0, 0.25, 0.05)
    weights = {"w1": w1, "w2": w2, "w3": w3, "w4": w4}

    st.subheader("Scenario")
    scenario_ids = [s["id"] for s in scenarios]
    scenario_id = st.selectbox("Named scenario (see data/scenarios.json)", scenario_ids)

st.metric("Students loaded", len(students))
with st.expander("Students"):
    st.dataframe(pd.DataFrame(students))

scenario = loader.find_scenario(scenarios, scenario_id)
st.subheader(f"Scenario: {scenario_id}")
st.caption(scenario.get("description", ""))
if "example_weights" in scenario:
    st.caption(f"Example weights for this scenario: {scenario['example_weights']}")

st.subheader("Random baseline")
baseline_teams = loader.random_baseline(students, team_size, seed=42)
st.caption(f"{len(baseline_teams)} teams of size {team_size} (uniform random, no optimization).")
with st.expander("Baseline teams"):
    st.json(baseline_teams)

st.subheader("Optimize teams")
strategy = st.radio("Strategy", ["hill_climbing", "simulated_annealing"], horizontal=True)
if st.button("Optimize teams"):
    try:
        if strategy == "hill_climbing":
            result = student_core.hill_climbing(students, config, weights, team_size)
        else:
            result = student_core.simulated_annealing(students, config, weights, team_size)
        st.success("Optimized teams:")
        st.json(result)
        score = student_core.objective(result, by_id, config, weights)
        baseline_score = student_core.objective(baseline_teams, by_id, config, weights)
        st.write(f"Objective (optimized) = {score:.3f} vs. baseline = {baseline_score:.3f}")
    except NotImplementedError:
        st.info(
            "Core not implemented. Fill `objective`, `hill_climbing`, and "
            "`simulated_annealing` in `starter/student_core.py` in your own code."
        )
