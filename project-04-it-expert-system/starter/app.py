"""Streamlit skeleton for Project 04 (IT Troubleshooting Expert System).

This page loads the knowledge base via `rule_loader.py` and shows a
symptom checklist. It does **not** run rule-based inference or build
an explanation on its own -- it only shows raw facts and then reports
that the core is not implemented. Fill `student_core.py` with your own
reasoning to make this page useful.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

import rule_loader
import student_core

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

st.set_page_config(page_title="IT Troubleshooting Expert System — starter", layout="wide")
st.title("IT Troubleshooting Expert System — starter")
st.markdown(
    "The **AI core is student work**. This page loads the knowledge base and "
    "lets you check off symptoms, but it must not run rule-based inference or "
    "generate an explanation on its own."
)

try:
    kb = rule_loader.load_all(DATA_DIR)
except rule_loader.SchemaError as exc:
    st.error(f"Knowledge base failed to load: {exc}")
    st.stop()

symptoms = kb["symptoms"]
domains = sorted({s["domain"] for s in symptoms})

with st.sidebar:
    st.header("Controls")
    domain_filter = st.selectbox("Domain", ["all"] + domains)
    scenario_labels = ["(none)"] + [s["id"] for s in kb["scenarios"]]
    scenario_choice = st.selectbox("Load a scenario fixture", scenario_labels)

visible_symptoms = [s for s in symptoms if domain_filter == "all" or s["domain"] == domain_filter]

preselected: list[str] = []
if scenario_choice != "(none)":
    scenario = next(s for s in kb["scenarios"] if s["id"] == scenario_choice)
    preselected = scenario["presented_symptoms"]
    st.caption(f"Scenario class: `{scenario['class']}` — {scenario['description']}")

st.subheader("Symptom checklist")
selected_symptoms = []
for symptom in visible_symptoms:
    checked = st.checkbox(
        f"{symptom['id']} ({symptom['domain']}) — {symptom['description']}",
        value=symptom["id"] in preselected,
        key=symptom["id"],
    )
    if checked:
        selected_symptoms.append(symptom["id"])

st.write(f"Selected symptoms: {selected_symptoms}")

if st.button("Diagnose"):
    try:
        results = student_core.infer(selected_symptoms, kb["rules"])
        st.write(results)
    except NotImplementedError:
        st.info(
            "Core not implemented. Fill `infer` and `explain` in "
            "`starter/student_core.py` in your own code."
        )

st.subheader("Reasoning")
st.caption(
    "Once implemented, this section should show which rule id(s) fired for "
    "each candidate cause, and flag ambiguous or contradictory symptom sets "
    "explicitly (see the class field in data/scenarios.json)."
)
