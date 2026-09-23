"""Student AI core — Project 10 (Helpdesk Ticket Router).

Implement the two functions below. This is the graded AI core: the
starter package (`starter/tokenizer.py`, `starter/app.py`) only provides
optional text-cleanup helpers and a UI skeleton; neither trains nor fits
any model.

Do not:
- Fit and dump a solution model in this file at import time (no
  pre-trained pickle/joblib shipped alongside the starter).
- Call a hosted LLM to classify tickets.
- Hard-code a lookup table of ticket texts to labels.

You may use `sklearn` (already in requirements.txt) for the
representation and/or the model — that is expected, not forbidden. What
is forbidden is shipping the *result* of already having done that work.
"""

from __future__ import annotations

from typing import Any, List, Sequence

LABELS: Sequence[str] = ("Account", "Network", "Hardware", "Software", "Security", "Other")


def train_model(texts: List[str], labels: List[str]) -> Any:
    """Train a ticket classifier on ``texts`` / ``labels``.

    Args:
        texts: raw ticket text, one string per training example.
        labels: the matching label for each text, one of ``LABELS``.

    Returns:
        A trained model object. The object's shape is up to you (e.g. a
        ``sklearn`` ``Pipeline``, or a tuple of ``(vectorizer, classifier)``)
        as long as ``predict`` below can use it.
    """
    raise NotImplementedError(
        "Implement training: choose a representation (bag-of-words, "
        "TF-IDF, n-grams, ...) and a classifier (Naive Bayes, k-NN, SVM, "
        "...), fit it on (texts, labels), and return the trained model."
    )


def predict(model: Any, texts: List[str]) -> List[str]:
    """Predict a label from ``LABELS`` for each string in ``texts``.

    Args:
        model: the object returned by ``train_model``.
        texts: raw ticket text to classify.

    Returns:
        A list of predicted labels, one per input text, in the same
        order, each one of ``LABELS``.
    """
    raise NotImplementedError(
        "Implement prediction: use the trained model to score each text "
        "and return the predicted label (and — if you want to expose a "
        "confidence score in the UI — a per-class score is welcome too)."
    )
