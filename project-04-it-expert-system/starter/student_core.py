"""Graded AI core for Project 04 (IT Troubleshooting Expert System).

You implement this module. It must run rule-based inference over the
knowledge base loaded by `rule_loader.py` -- symptoms, causes, and
`if -> then` rules -- to suggest possible causes for a set of reported
symptoms, and to explain which rules fired to reach each conclusion.

Do not hand-code the answer for a specific scenario id: the functions
below must generalize to any symptom set built from the same `data/`
schema, including symptom sets that were never listed in
`scenarios.json`.

Forbidden shortcuts (do not paste or adapt any of these into this file
or elsewhere in `starter/`):

- a working general-purpose forward-chaining or rule-engine library
  call standing in for your own inference code;
- a hard-coded lookup table keyed by scenario id that bypasses
  reasoning over `rules.json`;
- calling a hosted LLM to guess the cause instead of reasoning over
  the rule set yourself.
"""

from __future__ import annotations

from typing import Any


def infer(reported_symptoms: list[str], rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Infer the set of possible causes for `reported_symptoms`.

    Parameters
    ----------
    reported_symptoms:
        A list of symptom ids the user has confirmed, e.g. from
        `data/symptoms.json` or the Streamlit checklist in `app.py`.
    rules:
        The list of rule records from `rule_loader.load_rules`
        (each with `id`, `if`, `then`).

    Returns
    -------
    A list of result records. Each record should identify a candidate
    cause id and the rule id(s) that fired for it. Return an empty
    list when no rule's `if` set is a subset of `reported_symptoms`
    (see the `missing_info` fixtures in `data/scenarios.json`) --
    do not guess a cause from partial information.

    Raises
    ------
    NotImplementedError
        Always, until you implement this function.
    """
    raise NotImplementedError("Implement rule-based inference for Project 04.")


def explain(cause_id: str, reported_symptoms: list[str], rules: list[dict[str, Any]]) -> list[str]:
    """Explain why `cause_id` was (or could be) inferred.

    Returns the ordered list of rule ids that connect
    `reported_symptoms` to `cause_id`, for the "show the reasoning"
    presentation probe. Also responsible for surfacing contradictory
    or ambiguous cases: if two or more causes are equally supported,
    or the reported symptoms conflict with each other (see the
    `contradictory_symptoms` fixtures), this function's caller should
    be able to detect that from your return value or a raised, typed
    exception you define -- not from a silent, arbitrary pick.

    Raises
    ------
    NotImplementedError
        Always, until you implement this function.
    """
    raise NotImplementedError("Implement explanation generation for Project 04.")
