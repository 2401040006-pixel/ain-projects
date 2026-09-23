"""Graded AI core for Project 06 — YOUR implementation goes here.

This module intentionally ships EMPTY. Implementing ``forward`` and ``viterbi`` is the graded
midterm AI core (hidden-state estimation in a Hidden Markov Model). Do not import a third-party
HMM library to replace these functions: write and explain your own implementation.
"""

from __future__ import annotations

from typing import Dict, List, Sequence, Tuple


def forward(observations: Sequence[str], hmm_config: dict) -> List[Dict[str, float]]:
    """Run the forward algorithm to compute per-step state-occupancy probabilities.

    Args:
        observations: the observed sensor readings in order, e.g. ``["LOW", "LOW", "MEDIUM"]``.
        hmm_config: the parsed contents of ``data/hmm_config.json`` (hidden states,
            initial distribution, transition matrix) plus whichever noise-adjusted
            emission matrix you compute for this run.

    Returns:
        A list with one dict per time step, each mapping hidden state -> probability
        of being in that state at that step given all observations up to and
        including it. Each dict's values must sum to (approximately) 1.0.

    Raises:
        NotImplementedError: until you replace this stub with your own forward-algorithm
            implementation.
    """
    raise NotImplementedError("Implement forward: this is part of the graded AI core.")


def viterbi(observations: Sequence[str], hmm_config: dict) -> Tuple[List[str], float]:
    """Run the Viterbi algorithm to find the single most likely hidden-state path.

    Args:
        observations: the observed sensor readings in order.
        hmm_config: same as in ``forward``.

    Returns:
        A tuple ``(path, probability)`` where ``path`` is the most likely sequence of
        hidden states (same length as ``observations``) and ``probability`` is that
        path's joint probability.

    Raises:
        NotImplementedError: until you replace this stub with your own Viterbi
            implementation.
    """
    raise NotImplementedError("Implement viterbi: this is part of the graded AI core.")


def accuracy_against_ground_truth(estimated_states: Sequence[str], true_states: Sequence[str]) -> float:
    """Compare an estimated hidden-state sequence to the synthetic ground truth.

    This is a helper for the required noise-level experiment, not the graded core itself.
    Implement it using your own estimator's output; do not hand-compute the numbers outside
    the code you submit.

    Raises:
        NotImplementedError: until you implement it.
    """
    raise NotImplementedError("Implement accuracy_against_ground_truth for the required experiment.")
