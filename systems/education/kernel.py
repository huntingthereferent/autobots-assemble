from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any
import json

from .model import Observation, LearnerRelation, new_id, utc_now


class EducationKernel:
    """Minimal education kernel.

    It keeps the current learner relation front-facing while preserving prior
    relations and observations as natural provenance. It does not infer a
    learner from name, grade, age, curriculum position, or prior label.
    """

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else None
        self._events: list[dict[str, Any]] = []
        self._observations: dict[str, Observation] = {}
        self._relations: dict[str, LearnerRelation] = {}
        self._current: dict[tuple[str, str], str] = {}
        if self.path and self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    event = json.loads(line)
                    self._events.append(event)
                    self._replay(event)

    def _append(self, event: dict[str, Any]) -> None:
        self._events.append(event)
        self._replay(event)
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, ensure_ascii=False) + "\n")

    def _replay(self, event: dict[str, Any]) -> None:
        payload = event["payload"]
        if event["event_type"] == "OBSERVATION_ADDED":
            self._observations[payload["observation_id"]] = Observation(
                **{
                    **payload,
                    "supports": tuple(payload.get("supports", ())),
                    "contradicts": tuple(payload.get("contradicts", ())),
                    "support_conditions": tuple(payload.get("support_conditions", ())),
                    "evidence_refs": tuple(payload.get("evidence_refs", ())),
                    "provenance": tuple(payload.get("provenance", ())),
                }
            )
        elif event["event_type"] == "LEARNER_REGROUNDED":
            relation = LearnerRelation(
                **{
                    **payload,
                    "supported": tuple(payload.get("supported", ())),
                    "unsupported": tuple(payload.get("unsupported", ())),
                    "support_conditions": tuple(payload.get("support_conditions", ())),
                    "evidence_refs": tuple(payload.get("evidence_refs", ())),
                    "provenance": tuple(payload.get("provenance", ())),
                }
            )
            self._relations[relation.relation_id] = relation
            self._current[(relation.person_ref, relation.referent)] = relation.relation_id

    def observe(self, observation: Observation) -> LearnerRelation:
        self._append({"event_type": "OBSERVATION_ADDED", "occurred_at": utc_now(), "payload": asdict(observation)})

        key = (observation.person_ref, observation.referent)
        previous_id = self._current.get(key)
        previous = self._relations.get(previous_id) if previous_id else None

        supported = set(previous.supported if previous else ())
        unsupported = set(previous.unsupported if previous else ())

        for relation in observation.contradicts:
            supported.discard(relation)
            unsupported.add(relation)
        for relation in observation.supports:
            unsupported.discard(relation)
            supported.add(relation)

        support_conditions = tuple(dict.fromkeys(
            (*(previous.support_conditions if previous else ()), *observation.support_conditions)
        ))
        evidence_refs = tuple(dict.fromkeys(
            (*(previous.evidence_refs if previous else ()), *observation.evidence_refs)
        ))
        provenance = list(observation.provenance)
        provenance.append(f"education-observation:{observation.observation_id}")
        if previous:
            provenance.append(f"education-relation:{previous.relation_id}")

        relation = LearnerRelation(
            relation_id=new_id("learnrel"),
            person_ref=observation.person_ref,
            referent=observation.referent,
            supported=tuple(sorted(supported)),
            unsupported=tuple(sorted(unsupported)),
            support_conditions=support_conditions,
            evidence_refs=evidence_refs,
            provenance=tuple(dict.fromkeys(provenance)),
            supersedes=previous.relation_id if previous else "",
        )
        self._append({"event_type": "LEARNER_REGROUNDED", "occurred_at": utc_now(), "payload": asdict(relation)})
        return relation

    def current(self, person_ref: str, referent: str) -> LearnerRelation | None:
        relation_id = self._current.get((person_ref, referent))
        return self._relations.get(relation_id) if relation_id else None

    def current_for_person(self, person_ref: str) -> tuple[LearnerRelation, ...]:
        rows = [
            self._relations[relation_id]
            for (person, _referent), relation_id in self._current.items()
            if person == person_ref
        ]
        return tuple(sorted(rows, key=lambda item: item.referent.casefold()))

    def observations_for_person(self, person_ref: str) -> tuple[Observation, ...]:
        rows = [
            item for item in self._observations.values()
            if item.person_ref == person_ref
        ]
        return tuple(sorted(rows, key=lambda item: item.observed_at))

    def relation(self, relation_id: str) -> LearnerRelation:
        return self._relations[relation_id]

    def observation(self, observation_id: str) -> Observation:
        return self._observations[observation_id]

    def events(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._events)
