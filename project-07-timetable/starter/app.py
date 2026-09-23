"""Streamlit skeleton for Project 07 (University Timetable Scheduler).

This page loads one instance via `loaders.py`, lets the user pick which
instance to view and (optionally) which hard constraints to toggle for
display, and renders an empty day x slot grid. It does **not** search for a
schedule: clicking "Generate timetable" calls your `student_core.solve_csp`,
which raises `NotImplementedError` until you fill it in.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

import loaders
import student_core

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
INSTANCE_NAMES = [
    "feasible",
    "restricted_rooms",
    "extra_lecturer",
    "unsat",
]

st.set_page_config(page_title="Timetable Scheduler — starter", layout="wide")
st.title("Timetable Scheduler — starter")
st.markdown(
    "The **AI core is student work**. This page loads an instance and shows "
    "its resources and an empty grid, but it must not search for a "
    "schedule, detect satisfiability, or score soft constraints on its own. "
    "Fill `student_core.py::solve_csp` in your own code."
)

with st.sidebar:
    st.header("Controls")
    instance_name = st.selectbox("Instance", INSTANCE_NAMES, index=0)
    st.caption(
        "`unsat` is deliberately unsatisfiable -- your solver must report "
        "no solution for it, not crash or hang."
    )

instance_dir = DATA_DIR / f"instance_{instance_name}"
try:
    instance = loaders.load_instance(instance_dir)
except loaders.SchemaError as exc:
    st.error(f"Instance failed to load: {exc}")
    st.stop()

st.subheader(f"Instance: {instance_name}")
st.caption(instance["constraints"].get("description", ""))

col1, col2, col3, col4 = st.columns(4)
col1.metric("Courses", len(instance["courses"]))
col2.metric("Lecturers", len(instance["lecturers"]))
col3.metric("Rooms", len(instance["rooms"]))
col4.metric("Timeslots", len(instance["all_slots"]))

with st.expander("Courses"):
    st.dataframe(pd.DataFrame(instance["courses"]))
with st.expander("Lecturers"):
    st.dataframe(
        pd.DataFrame(
            [
                {"lecturer_id": lid, "name": l["name"], "available_slots": len(l["available_slots"])}
                for lid, l in instance["lecturers"].items()
            ]
        )
    )
with st.expander("Rooms"):
    st.dataframe(
        pd.DataFrame(
            [
                {"room_id": rid, "room_type": r["room_type"], "capacity": r["capacity"]}
                for rid, r in instance["rooms"].items()
            ]
        )
    )
with st.expander("Extra / hard constraints"):
    st.json(instance["constraints"])

st.subheader("Timetable grid (day x period)")
days = sorted({info["day"] for info in instance["slot_info"].values()})
periods = sorted({info["period"] for info in instance["slot_info"].values()})
grid = pd.DataFrame(index=[f"Period {p}" for p in periods], columns=days)
grid[:] = ""
st.caption("Empty until you generate a schedule below.")
st.dataframe(grid)

if st.button("Generate timetable"):
    try:
        solution = student_core.solve_csp(instance)
        if solution is None:
            st.warning("No legal assignment exists for this instance (correctly detected UNSAT).")
        else:
            is_valid, violations = loaders.validate_assignment(instance, solution)
            if not is_valid:
                st.error("Your solver returned an assignment that violates hard constraints:")
                st.write(violations)
            else:
                st.success("Legal assignment found.")
                st.json(solution)
    except NotImplementedError:
        st.info(
            "Core not implemented. Fill `solve_csp` in `starter/student_core.py` "
            "in your own code."
        )
