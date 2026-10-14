"""Independent finite-law replay for a worker's bounded required-edge report.

This verifier is intentionally independent of the copied worker's Python modules.
It checks a specific mathematical computation, not remote source identity.
"""
from __future__ import annotations

ACTION = ("A", "B")
VALID = frozenset(range(3))
KINDS = frozenset({"CONTRADICTED", "NOT_CONTRADICTED", "UNDECIDED"})
ROOT = (0, 0, 0)


def validate_inputs(inputs: object) -> dict:
    if not isinstance(inputs, dict) or set(inputs) != {"old_phi", "new_phi", "candidate_words", "required_state", "required_action"}:
        raise ValueError("expected finite prefilter fields only")
    def triple(value: object, name: str) -> tuple[int, int, int]:
        if not isinstance(value, (tuple, list)) or len(value) != 3 or any(type(v) is not int or v not in VALID for v in value):
            raise ValueError(f"{name} must be an F3 triple")
        return tuple(value)
    old, new = triple(inputs["old_phi"], "old_phi"), triple(inputs["new_phi"], "new_phi")
    source = triple(inputs["required_state"], "required_state")
    action = inputs["required_action"]
    if action not in ACTION:
        raise ValueError("required_action must be A or B")
    raw = inputs["candidate_words"]
    if not isinstance(raw, (list, tuple)) or not 1 <= len(raw) <= 16:
        raise ValueError("candidate_words requires 1..16 candidates")
    words = []
    for candidate in raw:
        if not isinstance(candidate, (list, tuple)) or not 1 <= len(candidate) <= 8:
            raise ValueError("candidate requires 1..8 seed words")
        if any(not isinstance(w, str) or not 1 <= len(w) <= 26 or set(w) - set(ACTION) for w in candidate):
            raise ValueError("seed words are 1..26 A/B symbols")
        words.append(tuple(candidate))
    canonical = {"old_phi": list(old), "new_phi": list(new), "candidate_words": [list(c) for c in words],
                 "required_state": list(source), "required_action": action}
    # An inconsistent seed has no valid finite result. Reject before admission.
    verdicts(canonical)
    return canonical


def _step(phi: tuple[int, int, int], state: tuple[int, int, int], action: str) -> tuple[int, int, int]:
    x, y, z = state
    if action == "A":
        return ((x + 1) % 3, y, z)
    return (x, (y + x + 1) % 3, (z + phi[y]) % 3)


def verdicts(inputs: dict) -> list[str]:
    old, new = tuple(inputs["old_phi"]), tuple(inputs["new_phi"])
    required = tuple(inputs["required_state"])
    action = inputs["required_action"]
    result = []
    for candidate in inputs["candidate_words"]:
        forward, reverse = {ROOT: ROOT}, {ROOT: ROOT}
        for word in candidate:
            left = right = ROOT
            for symbol in word:
                left, right = _step(old, left, symbol), _step(new, right, symbol)
                if (left in forward and forward[left] != right) or (right in reverse and reverse[right] != left):
                    raise ValueError("incompatible seed paths")
                forward[left] = right
                reverse[right] = left
        if required not in forward:
            result.append("UNDECIDED")
            continue
        left_target = _step(old, required, action)
        right_target = _step(new, forward[required], action)
        clash = (left_target in forward and forward[left_target] != right_target) or (right_target in reverse and reverse[right_target] != left_target)
        result.append("CONTRADICTED" if clash else "NOT_CONTRADICTED")
    return result
