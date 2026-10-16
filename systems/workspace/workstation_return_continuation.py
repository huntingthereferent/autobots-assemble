"""B4: verified finite helper output -> next workstation movement.

Native results never decide arbitrary equivalence or W13/game completion.
Each derived movement remains backed by freshly reverified source and a
separate domain-scoped decision; text similarity does not prove a connection.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Callable, Mapping

from runtime.handoff import HandoffEvent
from .workstation_native_feedback import canonical_digest, _RETURN_EVENT, _ASSIGN_EVENT

_DERIVED = "WORKSTATION_RETURN_RELATION_ADMITTED"
_PREFIX = "native-return:"

@dataclass(frozen=True)
class VerifiedNativeReturn:
    lane_handoff_id: str
    lane_id: str
    job_id: str
    worker_id: str
    opening_id: str
    output_sha256: str
    evidence_sha256: str
    source_fingerprint: str
    result: dict
    native_inputs: dict


@dataclass(frozen=True)
class NextMovement:
    relation: str
    capability: str
    kind: str = "BRANCH"  # A two-lane join still needs its own native verifier.


def finite_prefilter_next(view: VerifiedNativeReturn) -> NextMovement | None:
    """Scoped rule, not an A/B theorem: inconclusive prefilters need native evidence.

    A NOT_CONTRADICTED verdict is not an admitted edge. A native observer is
    required before advancing any correspondence claim.
    """
    from .process_handoff import WORKER_ID
    if view.worker_id != WORKER_ID or view.result.get("kind") != "finite-prefilter-v1":
        return None
    verdicts = view.result.get("verdicts")
    if (type(verdicts) is not list or
            not all(x in ("CONTRADICTED", "NOT_CONTRADICTED", "UNDECIDED") for x in verdicts)):
        raise ValueError("unrecognized finite-prefilter native verdicts")
    remaining = [i for i, v in enumerate(verdicts) if v != "CONTRADICTED"]
    if not remaining:
        return None
    return NextMovement(
        relation="Acquire owner-native evidence for unresolved candidate " +
                 str(remaining[0]) + " of job " + view.job_id,
        capability="owner-native-correspondence-witness")


class WorkstationReturnContinuation:
    """Reverify B3 feedback and derive a new B2 observation on the original lane.

    A provider is bound to an exact native worker family, not a generic NLP
    similarity score. The provider is rerun on each later admission pass.
    """

    def __init__(self, harness, *,
                 providers: Mapping[str, Callable[[VerifiedNativeReturn], NextMovement | None]],
                 verify_relation: Callable[[VerifiedNativeReturn, NextMovement], bool],
                 verify_return: Callable[..., dict] | None = None,
                 reverify_job: Callable[..., dict] | None = None):
        if not callable(verify_relation) or not providers or not all(
            isinstance(k, str) and k.strip() and callable(v) for k, v in providers.items()
        ):
            raise ValueError("exact native worker providers and independent relation verifier required")
        if (verify_return is None) != (reverify_job is None):
            raise ValueError("both source-native verifier functions must be supplied together")
        if verify_return is None:
            from .branch_help import verify_return as native_verify_return
            from .controls import reverify_job as native_reverify_job
            verify_return, reverify_job = native_verify_return, native_reverify_job
        self.harness = harness
        self.providers = dict(providers)
        self.verify_relation = verify_relation
        self.verify_return = verify_return
        self.reverify_job = reverify_job
        self.base_verify_observation = harness.verify_observation

    def _view(self, lane_handoff_id: str) -> VerifiedNativeReturn:
        runtime = self.harness._runtime()
        lane = runtime.get(lane_handoff_id)
        if (lane.metadata.get("source_system") != "workstation-continuation-lane/v1"
                or not lane.metadata.get("birth_proposal_id")
                or len(lane.metadata.get("parents") or ()) != 1):
            raise ValueError("native return source must be an existing single-parent child lane")
        # A once-accepted B2 source cannot be reused after its authority
        # disappears. Recheck the exact parent observation, not its label.
        source_ids = lane.inputs.get("source_observation_ids")
        _, _, _, original_observations, _ = self.harness._snapshot()
        original = [o for o in original_observations
                    if o.id in (source_ids or ())]
        if (len(source_ids or ()) != 1 or len(original) != 1
                or original[0].kind != "BRANCH"
                or original[0].lane_id != lane.metadata["parents"][0]
                or original[0].capability != lane.inputs.get("requested_capability")
                or original[0].relation != lane.referent
                or not self.base_verify_observation(original[0])):
            raise ValueError("original parent movement is not freshly witnessed")
        events = runtime.event_store.for_handoff(lane_handoff_id)
        assigned = [e for e in events if e.event_type == _ASSIGN_EVENT]
        returned = [e for e in events if e.event_type == _RETURN_EVENT]
        if len(assigned) != 1 or len(returned) != 1:
            raise ValueError("one native admission and one verified feedback event required")
        a, record = assigned[0].data, returned[0].data
        if (record.get("opening_id") != a.get("opening_id")
                or record.get("job_id") != a.get("job_id")
                or record.get("parent_cp_witnessed") is not False):
            raise ValueError("feedback does not match the native assignment")
        job_id, opening_id = a["job_id"], a["opening_id"]
        confirmed = self.verify_return(data_dir=self.harness.data_dir, opening_id=opening_id)
        independently = self.reverify_job(data_dir=self.harness.data_dir, job_id=job_id)
        if (confirmed.get("state") != "RETURN_RECORDED_REVERIFY_BEFORE_USE"
                or confirmed.get("parent_cp_witnessed") is not False
                or confirmed.get("child", {}).get("job_id") != job_id
                or independently != {"job_id": job_id, "status": "COMPLETE",
                                     "reverified": True, "executed": False}):
            raise ValueError("native returned result no longer independently verified")
        runtime = self.harness._runtime()
        job, state = runtime.get(job_id), runtime.state(job_id)
        fp = job.metadata.get("edition_fingerprint")
        if (state.status != "COMPLETE"
                or job.metadata.get("source_system") != "process-workstation"
                or fp != record.get("source_fingerprint")
                or canonical_digest(state.output) != record.get("output_sha256")
                or canonical_digest([getattr(e, "__dict__", {}) for e in state.evidence]) !=
                    record.get("evidence_sha256")):
            raise ValueError("native source or result differs from witnessed feedback")
        worker = job.metadata.get("worker_id")
        if worker not in self.providers:
            raise ValueError("no domain-native continuation provider for this worker")
        return VerifiedNativeReturn(
            lane_handoff_id, lane.metadata["lane_id"], job_id, worker,
            opening_id, record["output_sha256"], record["evidence_sha256"],
            fp, dict(state.output), dict(job.inputs))

    @staticmethod
    def _ref(view: VerifiedNativeReturn, move: NextMovement) -> str:
        digest = sha256("\x1f".join((
            view.job_id, view.output_sha256, view.evidence_sha256,
            view.source_fingerprint, move.kind, move.capability, move.relation
        )).encode("utf8")).hexdigest()
        return _PREFIX + digest

    def _candidate(self, view: VerifiedNativeReturn) -> NextMovement | None:
        move = self.providers[view.worker_id](view)
        if move is None:
            return None
        if (not isinstance(move, NextMovement) or move.kind != "BRANCH"
                or not isinstance(move.relation, str) or not move.relation.strip()
                or len(move.relation) > 200 or not isinstance(move.capability, str)
                or not move.capability.strip() or len(move.capability) > 200):
            raise ValueError("invalid or unsupported domain continuation movement")
        if not self.verify_relation(view, move):
            return None
        return move

    def derive_next(self, lane_handoff_id: str) -> dict:
        """One invoked pass; unproven next relation does not mutate anything."""
        view = self._view(lane_handoff_id)
        move = self._candidate(view)
        if move is None:
            return {"state": "NO_ADMITTED_NEXT_RELATION", "observation_id": None}
        ref = self._ref(view, move)
        oid = self.harness.observe(lane_id=view.lane_id, kind=move.kind,
                                   relation=move.relation, capability=move.capability,
                                   witness_ref=ref)
        runtime = self.harness._runtime()
        old = [e for e in runtime.event_store.for_handoff(lane_handoff_id)
               if e.event_type == _DERIVED]
        payload = {"observation_id": oid, "job_id": view.job_id,
                   "output_sha256": view.output_sha256,
                   "source_fingerprint": view.source_fingerprint,
                   "witness_ref": ref, "relation": move.relation,
                   "capability": move.capability}
        if old:
            if len(old) != 1 or old[0].data != payload:
                raise ValueError("conflicting persisted next-relation derivation")
            return {"state": "ALREADY_RECORDED", "observation_id": oid}
        current = runtime.state(lane_handoff_id)
        runtime.event_store.append(HandoffEvent.create(
            handoff_id=lane_handoff_id, event_type=_DERIVED,
            actor_id="workstation-return-continuation",
            data=payload,
            parents=(current.last_event_id,) if current.last_event_id else (),
        ))
        return {"state": "NEXT_RELATION_RECORDED", "observation_id": oid}

    def verify_observation(self, observation) -> bool:
        """Fresh recheck used by next_pass; fails closed on native-return claims."""
        if not observation.witness_ref.startswith(_PREFIX):
            return bool(self.base_verify_observation(observation))
        runtime = self.harness._runtime()
        lane_hid = self.harness._handoff_id(observation.lane_id)
        matching = [e for e in runtime.event_store.for_handoff(lane_hid)
                    if e.event_type == _DERIVED
                    and e.data.get("observation_id") == observation.id]
        if len(matching) != 1:
            return False
        row = matching[0].data
        try:
            view = self._view(lane_hid)
            move = self._candidate(view)
        except (ValueError, KeyError):
            return False
        return bool(move and
                    row.get("job_id") == view.job_id and
                    row.get("output_sha256") == view.output_sha256 and
                    row.get("source_fingerprint") == view.source_fingerprint and
                    row.get("witness_ref") == observation.witness_ref ==
                    self._ref(view, move) and
                    row.get("relation") == observation.relation == move.relation and
                    row.get("capability") == observation.capability == move.capability and
                    observation.kind == move.kind)

    def next_pass(self) -> dict:
        """B2 movement driven by the freshly reverified B3 return."""
        return self.harness.tick(verify_observation=self.verify_observation)
