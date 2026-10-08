"""Native-witness A/B evaluator using the existing lineage contract.

Reuses James's existing AgentMove, Handoff, and AgentLineage contracts.
This is a comparator, not a separate agent or an actuator.

A registered provider must supply an independently locatable before/after
observation. Unconnected tasks stay UNKNOWN rather than being fabricated.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from .agent_lineage import AgentMove
from .handoff import EvidenceRecord, ExecutionResult, Handoff, HandoffState


@dataclass(frozen=True)
class ObservedTransition:
    """One already performed native movement and its verifiable observations."""

    referent: str
    before: Mapping[str, Any]
    after: Mapping[str, Any]
    before_ref: str
    after_ref: str
    source: str
    action: str
    predicted_after: Mapping[str, Any] | None = None
    next_referent: str = ""
    evidence_kind: str = "measurement"


Observer = Callable[[Handoff, HandoffState], ObservedTransition | None]
_ABSENT = object()


def compare_observations(before: Mapping[str, Any], after: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return preserved and changed relations, including added/removed keys."""
    survived: dict[str, Any] = {}
    changed: dict[str, Any] = {}
    for key in sorted(set(before) | set(after)):
        old, new = before.get(key, _ABSENT), after.get(key, _ABSENT)
        if old == new:
            survived[key] = old
        else:
            changed[key] = {
                "before": None if old is _ABSENT else old,
                "after": None if new is _ABSENT else new,
                "before_present": old is not _ABSENT,
                "after_present": new is not _ABSENT,
            }
    return survived, changed


class NativeABEvaluator:
    """Adapter for EcosystemService(ab_evaluator=...) / AgentLineage.evaluate.

    Observer must NOT perform an uncontrolled non-idempotent action inside
    evaluate: it reads witnessed native transitions from the relevant provider.
    """

    def __init__(self, observe: Observer) -> None:
        self.observe = observe

    def has_observation(self, handoff_id: str) -> bool:
        """Readiness is optional for observers without a native capture queue."""
        available = getattr(self.observe, "has_capture", None)
        return bool(available(handoff_id)) if callable(available) else True

    @staticmethod
    def unresolved(reason: str, *, state: str = "UNKNOWN", detail: dict | None = None) -> AgentMove:
        return AgentMove(result=ExecutionResult(
            status=state,
            output={"ab_state": state, **(detail or {})},
            note=reason,
        ))

    def __call__(self, handoff: Handoff, state: HandoffState) -> AgentMove:
        if state.status != "READY":
            return self.unresolved("not a READY A/B movement", state="UNKNOWN")
        try:
            observation = self.observe(handoff, state)
        except Exception as exc:
            return self.unresolved(
                f"native observation unavailable: {type(exc).__name__}: {exc}"
            )
        if observation is None:
            return self.unresolved(
                "native observation unavailable: swallow/reground exact current referent first"
            )
        if not isinstance(observation, ObservedTransition):
            return self.unresolved("observer returned an unsupported witness shape")
        if observation.referent != handoff.referent:
            return self.unresolved("witness referent disagrees with current handoff referent")
        if not all((observation.source.strip(), observation.action.strip(),
                    observation.before_ref.strip(), observation.after_ref.strip())):
            return self.unresolved("native witness lacks source, action, or before/after locators")
        if observation.before_ref == observation.after_ref:
            return self.unresolved("cannot independently distinguish before and after observations")
        if observation.evidence_kind not in {"measurement", "source"}:
            return self.unresolved("simulation or unadmitted evidence cannot establish live movement")
        permitted = handoff.admissible_evidence.get("movement witness", ())
        if permitted and observation.evidence_kind not in permitted:
            return self.unresolved("native evidence kind is not admissible for this handoff")
        if any(c != "movement witness" for c in handoff.required_witnesses):
            return self.unresolved("other required handoff witnesses remain unverified")
        if not isinstance(observation.before, Mapping) or not isinstance(observation.after, Mapping):
            return self.unresolved("native before/after observations must be mappings")

        survived, changed = compare_observations(observation.before, observation.after)
        comparison = {
            "referent": handoff.referent,
            "action": observation.action,
            "before": dict(observation.before),
            "observed": dict(observation.after),
            "survived": survived,
            "changed": changed,
            "source": observation.source,
            "before_ref": observation.before_ref,
            "after_ref": observation.after_ref,
        }
        predicted = observation.predicted_after
        if predicted is not None:
            if not isinstance(predicted, Mapping):
                return self.unresolved("prediction must be a mapping", state="PARTIAL", detail=comparison)
            comparison["predicted"] = dict(predicted)
            comparison["prediction_matched"] = dict(predicted) == dict(observation.after)

        if not changed:
            return self.unresolved(
                "no observed movement; preservation recorded, not promoted to completion",
                state="PARTIAL", detail=comparison,
            )
        if predicted is not None and dict(predicted) != dict(observation.after):
            return self.unresolved(
                "prediction contradicted by native observation; counterexample preserved",
                state="PARTIAL", detail=comparison,
            )

        witness = EvidenceRecord(
            condition="movement witness",
            kind=observation.evidence_kind,
            source=observation.source,
            ref=observation.after_ref,
            note=f"before={observation.before_ref}; action={observation.action}; "
                 f"changed={tuple(changed)}; survived={tuple(survived)}",
            depth="observed",
        )
        return AgentMove(
            result=ExecutionResult(
                status="COMPLETE",
                evidence=(witness,),
                output={"ab_state": "MOVE", **comparison},
                note="native A/B movement verified",
            ),
            next_referent=observation.next_referent,
        )
