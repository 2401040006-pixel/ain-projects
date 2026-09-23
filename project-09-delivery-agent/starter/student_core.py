"""Student AI core — Project 09 (Delivery Agent).

Implement the two functions below. This is the graded AI core: the
environment (`environment/gridworld.py`) only provides deterministic
transitions and rewards; it does not choose actions or learn anything.

Do not:
- Ship a pre-trained/serialized Q-table (no ``qtable.json``, ``.pkl``, etc.).
- Call a hosted LLM to pick actions or to "learn" the policy.
- Hard-code the optimal action sequence for a specific map.

The starter Streamlit app (`starter/app.py`) already demonstrates a random
policy walking the grid. Your job is epsilon-greedy action selection and
the tabular Q-learning update loop.
"""

from __future__ import annotations

from typing import Dict, Iterable, Tuple

State = Tuple[int, int, bool]
QTable = Dict[Tuple[State, str], float]


def select_action(state: State, q_table: QTable, actions: Iterable[str], epsilon: float) -> str:
    """Choose an action for ``state`` using an epsilon-greedy policy.

    With probability ``epsilon``, return a uniformly random action from
    ``actions`` (exploration). Otherwise, return the action with the
    highest ``q_table[(state, action)]`` value, breaking ties consistently
    (exploitation). Unseen (state, action) pairs should be treated as
    Q-value 0.0.

    Args:
        state: current ``(row, col, has_package)`` state.
        q_table: mapping from ``(state, action)`` to a learned Q-value.
        actions: iterable of legal action names, e.g. ``GridWorld.actions``.
        epsilon: exploration probability in ``[0, 1]``.

    Returns:
        The chosen action name (must be one of ``actions``).
    """
    raise NotImplementedError(
        "Implement epsilon-greedy action selection: explore with probability "
        "epsilon, otherwise exploit the best known Q-value for this state."
    )


def q_learning(
    env,
    episodes: int,
    alpha: float,
    gamma: float,
    epsilon: float,
) -> QTable:
    """Train a tabular Q-learning agent on ``env``.

    Run ``episodes`` episodes. Each episode should call ``env.reset()``,
    then repeatedly call ``select_action`` and ``env.step`` until the
    episode is done, applying the standard Q-learning update:

        Q(s, a) <- Q(s, a) + alpha * (r + gamma * max_a' Q(s', a') - Q(s, a))

    Args:
        env: a ``environment.gridworld.GridWorld`` instance.
        episodes: number of training episodes to run.
        alpha: learning rate.
        gamma: discount factor.
        epsilon: exploration probability for the behavior policy.

    Returns:
        The learned Q-table mapping ``(state, action) -> value``. An empty
        or all-zero table is not a valid "trained" result; this function
        must actually run the update loop above.
    """
    raise NotImplementedError(
        "Implement the Q-learning update loop: run episodes, select actions "
        "with select_action(), step the environment, and update the Q-table."
    )
