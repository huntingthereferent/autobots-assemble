from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


@dataclass(frozen=True)
class Observation:
    observation_id: str
    person_ref: str
    referent: str
    observed: str
    supports: tuple[str, ...] = ()
    contradicts: tuple[str, ...] = ()
    support_conditions: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()
    observed_at: str = field(default_factory=utc_now)

    @classmethod
    def create(
        cls,
        *,
        person_ref: str,
        referent: str,
        observed: str,
        supports: tuple[str, ...] = (),
        contradicts: tuple[str, ...] = (),
        support_conditions: tuple[str, ...] = (),
        evidence_refs: tuple[str, ...] = (),
        provenance: tuple[str, ...] = (),
    ) -> "Observation":
        for name, value in (("person_ref", person_ref), ("referent", referent), ("observed", observed)):
            if not str(value).strip():
                raise ValueError(f"{name} is required")
        return cls(
            observation_id=new_id("obs"),
            person_ref=person_ref.strip(),
            referent=referent.strip(),
            observed=observed.strip(),
            supports=tuple(x.strip() for x in supports if x.strip()),
            contradicts=tuple(x.strip() for x in contradicts if x.strip()),
            support_conditions=tuple(x.strip() for x in support_conditions if x.strip()),
            evidence_refs=tuple(x.strip() for x in evidence_refs if x.strip()),
            provenance=tuple(x.strip() for x in provenance if x.strip()),
        )


@dataclass(frozen=True)
class LearnerRelation:
    relation_id: str
    person_ref: str
    referent: str
    supported: tuple[str, ...]
    unsupported: tuple[str, ...]
    support_conditions: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    provenance: tuple[str, ...]
    supersedes: str = ""
    formed_at: str = field(default_factory=utc_now)
