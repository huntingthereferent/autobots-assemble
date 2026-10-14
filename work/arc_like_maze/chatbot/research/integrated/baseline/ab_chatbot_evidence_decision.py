"""Bounded evidence decision for the standalone A/B chatbot feasibility probes.

This module does NOT implement a general chatbot. It distinguishes a rooted
behavioral correspondence (conditional on a known candidate grammar) from a
verified, fully observed transition law on the named finite-state domain.

Run alongside ab_chatbot_relation_probe.py and ab_chatbot_admission_probe.py.
"""
from dataclasses import dataclass
from itertools import product
from typing import Callable

from ab_chatbot_relation_probe import FiniteSystem, build_probes, identify
from ab_chatbot_admission_probe import (
    Admission, State, check_full_state_law,
)

Probe = tuple[str, str]
RootOracle = Callable[[Probe], bool]
StepOracle = Callable[[State, str], State]
NINE = tuple(FiniteSystem((0, a, b)) for a, b in product(range(3), repeat=2))
PROBES = build_probes(NINE)


@dataclass(frozen=True)
class EvidenceDecision:
    status: str
    # Rooted observations classify only relative to the original nine candidates.
    behavioral_candidates: tuple[tuple[int, int, int], ...]
    rooted_observations: tuple[tuple[Probe, bool], ...]
    admission: Admission | None
    reason: str

    @property
    def full_state_verified(self) -> bool:
        return self.status in {"VERIFIED_NINE_LAW", "VERIFIED_OTHER_27_LAW"}


def assess(
    observe_root: RootOracle,
    observe_step: StepOracle | None = None,
    *,
    max_full_state_calls: int = 54,
    requested_claim: str = "full_state_law",
) -> EvidenceDecision:
    """Use cheap rooted relations first, then FULL-state evidence if available.

    The rooted observer and step observer are independent inputs. A proof cannot
    be promoted if the two contradict each other. Every positive transition-law
    claim assumes a total deterministic step oracle on labeled F3^3 states.
    """
    if requested_claim not in {"behavioral_class", "full_state_law"}:
        raise ValueError("unsupported requested claim")
    if max_full_state_calls < 0:
        raise ValueError("negative transition-query budget")
    class RootAdapter:
        def equal_ends(self, pair: Probe) -> bool:
            return bool(observe_root(pair))

    remaining, history = identify(NINE, RootAdapter(), PROBES)
    rooted = tuple((p, bool(answer)) for p, answer, _ in history)
    matched = tuple(NINE[i].phi for i in remaining)

    if requested_claim == "behavioral_class":
        return EvidenceDecision(
            "CONDITIONAL_BEHAVIORAL_CLASS", matched, rooted, None,
            "Rooted queries distinguish a class only under assumed nine-family "
            "membership; full-state observations are not needed for this claim.",
        )

    if observe_step is None:
        return EvidenceDecision(
            "UNKNOWN_FULL_STATE", matched, rooted, None,
            "Rooted endpoint equalities establish only a conditional behavioral class; "
            "no full-state transition oracle was supplied.",
        )

    admission = check_full_state_law(observe_step, max_calls=max_full_state_calls)
    if admission.status == "UNKNOWN_BUDGET":
        return EvidenceDecision(
            "UNKNOWN_FULL_STATE", matched, rooted, admission,
            "Not every A/B transition on the declared 27-state domain was checked.",
        )
    if admission.status == "OUTSIDE_27_GRAMMAR":
        return EvidenceDecision(
            "REJECTED_27_GRAMMAR", matched, rooted, admission,
            "Full-state transition evidence contradicts the declared 27-law grammar.",
        )
    if admission.status != "VERIFIED_27_GRAMMAR":
        raise ValueError(f"Unknown admission status: {admission.status}")

    verified = FiniteSystem(admission.inferred_phi)
    inconsistent = tuple(p for p, equal in rooted if verified.equal_ends(p) != equal)
    if inconsistent:
        return EvidenceDecision(
            "INCONSISTENT_OBSERVERS", matched, rooted, admission,
            "Verified step oracle contradicts rooted observations on: " + repr(inconsistent),
        )
    if verified.phi[0] != 0:
        return EvidenceDecision(
            "VERIFIED_OTHER_27_LAW", matched, rooted, admission,
            "The transition law is verified in the 27-law family but not in the "
            "nine-law subfamily (phi(0) != 0). Rooted matches remain conditional.",
        )
    if verified.phi not in matched:
        return EvidenceDecision(
            "INCONSISTENT_OBSERVERS", matched, rooted, admission,
            "Verified law fails the stated rooted behavioral classification.",
        )
    return EvidenceDecision(
        "VERIFIED_NINE_LAW", matched, rooted, admission,
        "All 54 named transitions match the reconstructed nine-family law; "
        "rooted observations agree. This does not establish arbitrary black-box laws.",
    )


def main() -> None:
    from ab_chatbot_admission_probe import OffOrbitAlteration

    inside = FiniteSystem((0, 1, 2))
    outside_nine = FiniteSystem((1, 0, 0))
    altered = OffOrbitAlteration()
    cases = [
        ("behavior only", assess(inside.equal_ends, inside.step, requested_claim="behavioral_class")),
        ("root only", assess(inside.equal_ends)),
        ("fully verified", assess(inside.equal_ends, inside.step)),
        ("different admitted family", assess(outside_nine.equal_ends, outside_nine.step)),
        ("budget 53", assess(inside.equal_ends, inside.step, max_full_state_calls=53)),
        ("off-reachable alteration", assess(altered.equal_ends, altered.step)),
        ("contradictory oracles", assess(inside.equal_ends, outside_nine.step)),
    ]
    for label, result in cases:
        n = result.admission.calls if result.admission else 0
        print(f"{label:26} {result.status:27} rooted={len(result.rooted_observations)} full-state={n}")
    assert [r.status for _, r in cases] == [
        "CONDITIONAL_BEHAVIORAL_CLASS", "UNKNOWN_FULL_STATE",
        "VERIFIED_NINE_LAW", "VERIFIED_OTHER_27_LAW",
        "UNKNOWN_FULL_STATE", "REJECTED_27_GRAMMAR", "INCONSISTENT_OBSERVERS",
    ]


if __name__ == "__main__":
    main()
