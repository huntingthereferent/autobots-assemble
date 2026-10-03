from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable, Optional
import json


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class EvidenceRef:
    ref: str
    source: str
    note: str = ""


@dataclass(frozen=True)
class Relation:
    """Generic append-only relation with provenance.

    The network representation remains domain-neutral:
        subject --predicate--> object

    Evidence/witness metadata supports admission; it does not create a new
    domain object model.
    """

    subject: str
    predicate: str
    object: Any
    source: str
    observed_at: str = field(default_factory=utc_now)
    evidence: tuple[EvidenceRef, ...] = ()
    parents: tuple[str, ...] = ()

    @property
    def relation_id(self) -> str:
        payload = json.dumps(
            {
                "subject": self.subject,
                "predicate": self.predicate,
                "object": self.object,
                "source": self.source,
                "observed_at": self.observed_at,
                "evidence": [asdict(e) for e in self.evidence],
                "parents": self.parents,
            },
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        return "rel_" + sha256(payload).hexdigest()[:20]


@dataclass(frozen=True)
class Snapshot:
    seq: int
    frozen_at: str
    relations: tuple[Relation, ...]

    def find(self, *, subject: Optional[str] = None, predicate: Optional[str] = None) -> tuple[Relation, ...]:
        out = []
        for relation in self.relations:
            if subject is not None and relation.subject != subject:
                continue
            if predicate is not None and relation.predicate != predicate:
                continue
            out.append(relation)
        return tuple(out)

    def latest(self, subject: str, predicate: str) -> Optional[Relation]:
        matches = self.find(subject=subject, predicate=predicate)
        return matches[-1] if matches else None


class RelationLedger:
    """Append-only relation ledger.

    Old relations remain evidence. Movement never deletes history.
    """

    def __init__(self, relations: Iterable[Relation] = ()) -> None:
        self._relations = list(relations)
        self._seq = 0

    def append(self, *relations: Relation) -> Snapshot:
        if not relations:
            raise ValueError("movement requires at least one relation")
        for relation in relations:
            if not relation.source.strip():
                raise ValueError("relation source is required")
        self._relations.extend(relations)
        self._seq += 1
        return self.freeze()

    def freeze(self) -> Snapshot:
        return Snapshot(self._seq, utc_now(), tuple(self._relations))

    def append_jsonl(self, path: str | Path, *relations: Relation) -> Snapshot:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            for relation in relations:
                row = asdict(relation)
                row["relation_id"] = relation.relation_id
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        return self.append(*relations)
