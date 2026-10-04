"""A/B-constrained ARC3 witness-compression action selector.

This module does not generate game semantics. It only ranks already-admissible,
exact predictions supplied by the forward-match layer.

A prediction value of None means the candidate cannot make an exact observable
prediction for that action under the current evidence/correspondence contract.
"""

from __future__ import annotations

from itertools import combinations
from typing import Hashable, Mapping


Prediction = Hashable | None


def score_action(predictions: Mapping[str, Prediction]) -> dict[str, float | int]:
    """Score one action by how many live candidate pairs it can distinguish.

    Each key is a live candidate-model/relation id. Each value is the exact
    observable outcome predicted for this action, or None when the current
    evidence contract cannot support an exact prediction.

    The central quantity is separated_pairs: the number of candidate pairs
    that predict different observable outcomes. Missing predictions do not
    count as separated.
    """
    candidate_ids = list(predictions)
    total_pairs = len(candidate_ids) * (len(candidate_ids) - 1) // 2

    separated_pairs = 0
    same_prediction_pairs = 0
    unknown_pairs = 0

    for left, right in combinations(candidate_ids, 2):
        a = predictions[left]
        b = predictions[right]
        if a is None or b is None:
            unknown_pairs += 1
        elif a != b:
            separated_pairs += 1
        else:
            same_prediction_pairs += 1

    predicted_count = sum(value is not None for value in predictions.values())
    candidate_count = len(candidate_ids)

    return {
        "candidate_count": candidate_count,
        "predicted_count": predicted_count,
        "total_pairs": total_pairs,
        "separated_pairs": separated_pairs,
        "same_prediction_pairs": same_prediction_pairs,
        "unknown_pairs": unknown_pairs,
        "separation_rate": (
            separated_pairs / total_pairs if total_pairs else 0.0
        ),
        "coverage": (
            predicted_count / candidate_count if candidate_count else 0.0
        ),
    }


def rank_actions(
    action_predictions: Mapping[str, Mapping[str, Prediction]],
    *,
    goal_progress: Mapping[str, float] | None = None,
) -> list[dict[str, object]]:
    """Rank actions without collapsing witness value into task-goal value.

    Primary ordering:
      1. separation_rate
      2. separated_pairs
      3. prediction coverage

    goal_progress is only a final tie-breaker. It never upgrades an
    unsupported prediction or creates a correspondence.
    """
    goal_progress = goal_progress or {}
    rows: list[dict[str, object]] = []

    for action, predictions in action_predictions.items():
        score = score_action(predictions)
        rows.append(
            {
                "action": action,
                **score,
                "goal_progress": float(goal_progress.get(action, 0.0)),
            }
        )

    return sorted(
        rows,
        key=lambda row: (
            float(row["separation_rate"]),
            int(row["separated_pairs"]),
            float(row["coverage"]),
            float(row["goal_progress"]),
        ),
        reverse=True,
    )
