"""Source-agnostic continuation: provisional local success -> real attempt -> observation.

Never treats local tests, declared capability fit, or a returned label as native proof.
The caller supplies authorized capability adapters and an independent observer.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Iterable

VERDICTS = frozenset(('SUPPORTED', 'CONTRADICTED', 'UNKNOWN'))


@dataclass(frozen=True)
class Capability:
    name: str
    edition: str
    claims: tuple[str, ...]
    authorized: bool = False


@dataclass(frozen=True)
class Witness:
    verdict: str
    source_edition: str
    supported_relations: tuple[str, ...] = ()
    evidence_ref: str = ''
    independently_verified: bool = False


@dataclass(frozen=True)
class Movement:
    capability: str
    edition: str
    observed: str
    evidence_ref: str
    relations_admitted: tuple[str, ...]
    error: str = ''


@dataclass(frozen=True)
class ContinuationResult:
    status: str
    required: tuple[str, ...]
    admitted: tuple[str, ...]
    unresolved: tuple[str, ...]
    movements: tuple[Movement, ...]
    local_pass_assumed: bool


def continue_referent(required: Iterable[str], capabilities: Iterable[Capability], *,
                      attempt: Callable[[Capability], object],
                      observe: Callable[[Capability, object], Witness],
                      local_passed: bool = False, max_attempts: int = 8) -> ContinuationResult:
    """Choose an authorized move whose declared output reaches the *remaining* referent.

    Score(a) = number of unresolved required relations that a proposes to supply.
    Run and observe exactly once per (capability, source edition). A local PASS is
    a provisional assumption for selection, never evidence of crossing.
    """
    needs = tuple(required)
    options = tuple(capabilities)
    if (not needs or any(not isinstance(x, str) or not x for x in needs)
            or len(set(needs)) != len(needs)):
        raise ValueError('required relations must be nonempty and distinct')
    if type(max_attempts) is not int or not 1 <= max_attempts <= 64:
        raise ValueError('invalid attempt bound')
    identities = [(c.name, c.edition) for c in options]
    if len(identities) != len(set(identities)):
        raise ValueError('duplicate capability edition identity')
    if any(not c.name or not c.edition or not c.claims or len(set(c.claims)) != len(c.claims)
           for c in options):
        raise ValueError('incomplete capability')
    confirmed = set()
    attempted = set()
    history = []
    for _ in range(max_attempts):
        remaining = set(needs) - confirmed
        if not remaining:
            break
        possible = [c for c in options if c.authorized and (c.name, c.edition) not in attempted
                    and remaining.intersection(c.claims)]
        if not possible:
            break
        selected = min(possible, key=lambda c: (-len(remaining.intersection(c.claims)), c.name, c.edition))
        attempted.add((selected.name, selected.edition))
        try:
            raw = attempt(selected)  # Real attempt, not simulated approval.
        except Exception as exc:
            history.append(Movement(selected.name, selected.edition, 'ATTEMPT_ERROR', '', (),
                                    type(exc).__name__ + ': ' + str(exc)))
            continue
        try:
            witness = observe(selected, raw)  # Independently supplied native observer.
            if not isinstance(witness, Witness) or witness.verdict not in VERDICTS:
                raise ValueError('invalid observational verdict')
            if witness.source_edition != selected.edition:
                raise ValueError('observation source edition mismatch')
            if not set(witness.supported_relations).issubset(selected.claims):
                raise ValueError('observation exceeds declared capability')
            admissible = (witness.verdict == 'SUPPORTED' and witness.independently_verified
                          and bool(witness.evidence_ref))
            claimed = set(witness.supported_relations)
            admitted = tuple(x for x in needs if x in claimed and x not in confirmed) if admissible else ()
            confirmed.update(admitted)
            history.append(Movement(selected.name, selected.edition,
                                    witness.verdict if witness.independently_verified else 'UNKNOWN',
                                    witness.evidence_ref, admitted))
        except Exception as exc:
            history.append(Movement(selected.name, selected.edition, 'OBSERVATION_ERROR', '', (),
                                    type(exc).__name__ + ': ' + str(exc)))
    pending = tuple(x for x in needs if x not in confirmed)
    return ContinuationResult('CROSSED' if not pending else 'OPEN', needs,
                              tuple(x for x in needs if x in confirmed), pending,
                              tuple(history), local_passed is True)
