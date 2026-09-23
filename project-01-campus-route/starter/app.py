"""Streamlit skeleton for Project 01 (Smart Campus Route Planner).

Loads the campus graph and scenarios, and lets the user pick a start/end
node and preview constraints. It does **not** search for a route: BFS,
Greedy Best-First Search, and A* are your own work in `student_core.py`.
"""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
from graph import load_graph, load_scenarios  # noqa: E402
import student_core  # noqa: E402

st.set_page_config(page_title="Smart Campus Route Planner — starter", layout="wide")
st.title("Smart Campus Route Planner — starter")
st.markdown(
    "The **AI core is student work**. This page loads data and lets you pick "
    "a start/end node; it must not search, infer, optimize, or call a "
    "hosted model."
)

graph = load_graph()
scenarios = load_scenarios()
node_ids = sorted(graph.node_ids)

with st.sidebar:
    st.header("Graph summary")
    summary = graph.summary()
    st.metric("Nodes", summary["num_nodes"])
    st.metric("Edges", summary["num_edges"])
    st.write("Buildings:", ", ".join(summary["buildings"]))
    st.write("Floors:", ", ".join(str(f) for f in summary["floors"]))

    st.header("Controls")
    start_id = st.selectbox(
        "Start node",
        node_ids,
        index=0,
        format_func=lambda nid: f"{nid} — {graph.get_node(nid).name}",
    )
    end_id = st.selectbox(
        "End node",
        node_ids,
        index=len(node_ids) - 1,
        format_func=lambda nid: f"{nid} — {graph.get_node(nid).name}",
    )
    accessible_only = st.checkbox("Accessibility mode (avoid stairs-only edges)")
    algorithm = st.selectbox("Algorithm (not runnable yet)", ["bfs", "greedy", "astar"])
    st.caption(
        f"Accessibility mode: {'on' if accessible_only else 'off'} "
        "(the starter records this choice but does not enforce it)."
    )

map_path = Path(__file__).resolve().parent.parent / "data" / "campus_map.png"
if map_path.exists():
    with st.expander("Campus map (data/campus_map.png)", expanded=True):
        st.image(str(map_path), use_column_width=True)

st.subheader("Selected nodes")
col1, col2 = st.columns(2)
with col1:
    st.write(graph.get_node(start_id))
with col2:
    st.write(graph.get_node(end_id))

st.subheader("Scenarios (data/scenarios.json)")
st.json(scenarios)

st.subheader("Run")
if st.button("Find route"):
    try:
        if algorithm == "bfs":
            student_core.bfs(graph, start_id, end_id)
        elif algorithm == "greedy":
            student_core.greedy(graph, start_id, end_id, student_core.euclidean_heuristic)
        else:
            student_core.astar(graph, start_id, end_id, student_core.euclidean_heuristic)
    except NotImplementedError:
        st.info("Core not implemented. Fill `starter/student_core.py` in your own code.")
else:
    st.info("Core not implemented. Fill `starter/student_core.py` in your own code.")
