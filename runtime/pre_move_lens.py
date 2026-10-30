"""Evidence admission check for the ANY pre-movement lens.

This validates a *recorded comparison*, not mathematical truth or assistant thought.
It does not implement or redefine the A/B operation.
"""
from dataclasses import dataclass
from typing import Literal

Relation = Literal["equivalent", "analogous", "absent", "unverified"]


@dataclass(frozen=True)
class Comparison:
    subject: str
    source: str
    observed: str
    relation: Relation


@dataclass(frozen=True)
class LensResult:
    admitted: bool
    reasons: tuple[str, ...]


def check_before_move(
    *,
    proposed_move: str,
    ab_comparison: Comparison | None,
    production_comparison: Comparison | None,
    simplification: str,
    claim: str,
) -> LensResult:
    """Fail closed on missing comparisons or unsupported equivalence claims.

    'Admitted' means evidence fields are inspectable, NOT that the
    comparisons are correct or the movement is production-ready.
    """
    reasons = []
    if not proposed_move.strip():
        reasons.append("missing proposed movement")
    if not simplification.strip():
        reasons.append("missing A/B simplification or explicit unresolved gap")
    for name, item in (("A/B", ab_comparison), ("production", production_comparison)):
        if item is None:
            reasons.append(f"missing {name} comparison")
            continue
        if not all((item.subject.strip(), item.source.strip(), item.observed.strip())):
            reasons.append(f"incomplete {name} evidence")
        if item.relation not in ("equivalent", "analogous", "absent", "unverified"):
            reasons.append(f"invalid {name} relation")
    if claim in ("mathematically_proven", "production_ready"):
        reasons.append("strong claims require independent verification outside this lens")
    if production_comparison is not None and production_comparison.relation in (
        "absent", "unverified"
    ) and claim == "equivalent":
        reasons.append("cannot claim equivalence with absent/unverified production relation")
    if ab_comparison is not None and ab_comparison.relation in (
        "absent", "unverified"
    ) and claim == "equivalent":
        reasons.append("cannot claim equivalence with absent/unverified A/B relation")
    return LensResult(not reasons, tuple(reasons))
