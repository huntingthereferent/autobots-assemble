"""Journal-backed B2 workstation continuation harness.

This is an invoked pass, NOT an autonomous daemon. It preserves actual native
handoffs and their journal. Observation records are claims until a caller-supplied
native verifier independently accepts them *again on every pass*. A spawned
coordination lane is NEVER a claim of a running model worker or a native PASS.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
from pathlib import Path
from typing import Callable, Mapping

from runtime.engine import HandoffRuntime
from runtime.handoff import EvidenceRecord, Handoff, HandoffEvent
from runtime.journal import RuntimeJournal

from .workstation_continuation import Lane, Observation, Proposal, propose_movements

_LANE = "workstation-continuation-lane/v1"
_OBS = "WORKSTATION_MOVEMENT_OBSERVED"
_OPEN = "WORKSTATION_HELP_OPEN"
_SAFE = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.")


def _nonblank(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 200:
        raise ValueError(name + " must be a nonempty bounded string")
    return value.strip()


def _id(value: str) -> str:
    v = _nonblank(value, "identifier")
    if len(v) > 80 or not set(v) <= _SAFE:
        raise ValueError("unsafe workstation lane identifier")
    return v


def _hash(*parts: str) -> str:
    return sha256("\x1f".join(parts).encode("utf8")).hexdigest()[:24]


class WorkstationContinuationHarness:
    """Admit durable coordination lanes only from freshly verified observations.

    verify_observation and verify_connection must be independent domain-native
    verification functions, not mere JSON/source-label checks. No default
    permissive verifier exists. A worker edition label cannot authorize code
    execution: separate native controls must still admit/execute a real job.
    """

    def __init__(self, data_dir: str | Path, *,
                 verify_observation: Callable[[Observation], bool],
                 verify_connection: Callable[[Observation, Observation], bool],
                 worker_editions: Mapping[str, str] | None = None,
                 max_new_lanes: int = 4, max_total_lanes: int = 32):
        if not callable(verify_observation) or not callable(verify_connection):
            raise ValueError("two independent verifier callbacks required")
        self.data_dir = Path(data_dir)
        self.verify_observation = verify_observation
        self.verify_connection = verify_connection
        self.worker_editions = dict(worker_editions or {})
        self.max_new_lanes = max_new_lanes
        self.max_total_lanes = max_total_lanes

    def _runtime(self) -> HandoffRuntime:
        return HandoffRuntime(event_store=RuntimeJournal(self.data_dir / "runtime.jsonl"))

    @staticmethod
    def _handoff_id(lane_id: str) -> str:
        return "whlane-" + _hash(lane_id)

    def seed_lane(self, lane_id: str, referent: str, *,
                  cp_lane: str = "", cp_slot: str = "") -> str:
        """Explicitly admit initial A/B or other source-owned lane identities."""
        lane_id, referent = _id(lane_id), _nonblank(referent, "referent")
        if bool(cp_lane) != bool(cp_slot):
            raise ValueError("CP lane and slot must be supplied together")
        runtime = self._runtime()
        hid = self._handoff_id(lane_id)
        meta = {"source_system": _LANE, "lane_id": lane_id,
                "parents": [], "birth_proposal_id": "",
                "worker_registration": "NONE", "cp_lane": cp_lane, "cp_slot": cp_slot}
        if hid in runtime.snapshot():
            prior = runtime.get(hid)
            if prior.referent != referent or prior.metadata != meta:
                raise ValueError("lane identity already bound to different source")
            return hid
        runtime.submit(Handoff(
            handoff_id=hid, referent=referent,
            from_actor="workstation-operator", to_actor="workstation-continuation",
            required_relation="preserve independently evidenced lane",
            metadata=meta, provenance=("workstation-continuation-seed:" + lane_id,),
            boundaries=("No execution or native proof follows from lane creation.",),
        ))
        return hid

    def observe(self, *, lane_id: str, kind: str, relation: str,
                witness_ref: str, capability: str = "") -> str:
        """Append an *unverified* observation claim to the existing native journal.

        The callback gate in tick() must authenticate its evidence each time;
        this intake method does not authorize branching or joining.
        """
        lane_id = _id(lane_id)
        relation = _nonblank(relation, "relation")
        witness_ref = _nonblank(witness_ref, "native witness reference")
        if kind not in ("BRANCH", "RELATION"):
            raise ValueError("unsupported observation kind")
        if kind == "BRANCH":
            capability = _nonblank(capability, "capability")
        elif capability:
            raise ValueError("relation observation cannot assign a capability")
        oid = "whobs-" + _hash(lane_id, kind, relation, capability, witness_ref)
        runtime = self._runtime()
        lane_hid = self._handoff_id(lane_id)
        try:
            handoff = runtime.get(lane_hid)
        except KeyError as exc:
            raise ValueError("unknown workstation continuation lane") from exc
        if handoff.metadata.get("source_system") != _LANE or handoff.metadata.get("lane_id") != lane_id:
            raise ValueError("not a workstation continuation lane")
        for event in runtime.event_store.for_handoff(lane_hid):
            if event.event_type == _OBS and event.data.get("observation_id") == oid:
                expected = {"observation_id": oid, "kind": kind,
                            "relation": relation, "capability": capability}
                if event.data != expected or len(event.evidence) != 1 or event.evidence[0].ref != witness_ref:
                    raise ValueError("observation ID collision")
                return oid
        state = runtime.state(lane_hid)
        runtime.event_store.append(HandoffEvent.create(
            handoff_id=lane_hid, event_type=_OBS, actor_id="workstation-observation-intake",
            data={"observation_id": oid, "kind": kind,
                  "relation": relation, "capability": capability},
            evidence=(EvidenceRecord(condition="movement observation candidate",
                                     kind="source", source="native-witness-ref",
                                     ref=witness_ref, depth="reported"),),
            parents=(state.last_event_id,) if state.last_event_id else (),
        ))
        return oid

    def _snapshot(self):
        runtime = self._runtime()
        source = [h for h in runtime._handoffs.values()
                  if h.metadata.get("source_system") == _LANE]
        ids = {h.metadata["lane_id"]: h for h in source}
        if len(ids) != len(source):
            raise ValueError("duplicate persisted lane identity")
        lanes = [Lane(id=h.metadata["lane_id"], referent=h.referent,
                      parents=tuple(h.metadata.get("parents") or ()),
                      status=runtime.state(h.handoff_id).status)
                 for h in source]
        events = runtime.event_store.all()
        observations = []
        for sequence, e in enumerate(events):
            h = runtime._handoffs.get(e.handoff_id)
            if e.event_type != _OBS or h is None or h.metadata.get("source_system") != _LANE:
                continue
            if len(e.evidence) != 1 or e.evidence[0].condition != "movement observation candidate":
                raise ValueError("malformed persisted observation")
            observations.append(Observation(
                id=e.data["observation_id"], lane_id=h.metadata["lane_id"],
                kind=e.data["kind"], relation=e.data["relation"],
                capability=e.data["capability"], witness_ref=e.evidence[0].ref,
                sequence=sequence))
        admitted = frozenset(h.metadata["birth_proposal_id"] for h in source
                            if h.metadata.get("birth_proposal_id"))
        return runtime, ids, lanes, observations, admitted

    def inspect(self) -> dict:
        """Read-only, including proof-dependent proposals; no journal mutation."""
        _, _, lanes, observations, admitted = self._snapshot()
        proposals = propose_movements(
            lanes=lanes, observations=observations,
            worker_editions=self.worker_editions,
            verify_observation=self.verify_observation,
            verify_connection=self.verify_connection,
            admitted_proposal_ids=admitted,
            max_new_lanes=self.max_new_lanes,
            max_total_lanes=self.max_total_lanes,
        )
        return {"lanes": [asdict(x) for x in lanes],
                "proposals": [asdict(x) for x in proposals],
                "execution_started": False, "native_checkpoint_pass": False}

    def _record_opening(self, runtime: HandoffRuntime, parent_id: str, proposal: Proposal) -> bool:
        hid = self._handoff_id(parent_id)
        prior = runtime.event_store.for_handoff(hid)
        if any(e.event_type == _OPEN and e.data.get("proposal_id") == proposal.id for e in prior):
            return False
        state = runtime.state(hid)
        runtime.event_store.append(HandoffEvent.create(
            handoff_id=hid, event_type=_OPEN, actor_id="workstation-continuation",
            data={"proposal_id": proposal.id, "kind": proposal.kind,
                  "capability": proposal.capability, "reason": proposal.reason},
            parents=(state.last_event_id,) if state.last_event_id else ()))
        return True

    def tick(self) -> dict:
        """One *invoked* move; allocate coordination lanes, NEVER execute workers.

        A matching native capability is only a proposal to staff a later job.
        BIRTH creates a READY coordination lane, not a live agent. The connecting
        lane retains BOTH independently evidenced parent histories.
        """
        runtime, by_id, lanes, observations, admitted = self._snapshot()
        proposals = propose_movements(
            lanes=lanes, observations=observations,
            worker_editions=self.worker_editions,
            verify_observation=self.verify_observation,
            verify_connection=self.verify_connection,
            admitted_proposal_ids=admitted,
            max_new_lanes=self.max_new_lanes,
            max_total_lanes=self.max_total_lanes,
        )
        born, opened = [], []
        for p in proposals:
            if p.kind == "OPEN_UNSTAFFED":
                if self._record_opening(runtime, p.parents[0], p):
                    opened.append(p.id)
                continue
            if p.worker_edition is None:
                raise ValueError("staffable movement missing edition")
            hid = "whlane-" + p.id
            if hid in runtime.snapshot():
                existing = runtime.get(hid)
                if existing.metadata.get("birth_proposal_id") != p.id:
                    raise ValueError("conflicting existing birth")
                continue
            parents = tuple(p.parents)
            if not all(k in by_id for k in parents):
                raise ValueError("movement lost a parent lane")
            cp_lane = by_id[parents[0]].metadata.get("cp_lane", "")
            cp_slot = by_id[parents[0]].metadata.get("cp_slot", "")
            # Unlike a native job, this lane does not inherit an authorization
            # to execute. Its worker registration remains a separate boundary.
            runtime.submit(Handoff(
                handoff_id=hid, referent=p.relation,
                from_actor="workstation-continuation",
                to_actor="workstation-source-admission",
                required_relation="admit source-pinned native worker or preserve wall",
                inputs={"source_observation_ids": list(p.observation_ids),
                        "parent_lane_ids": list(parents),
                        "requested_capability": p.capability},
                provenance=tuple("workstation-parent:" + q for q in parents),
                boundaries=("Coordination birth is NOT native worker admission.",
                            "No source execution without existing native controls.",
                            "A matching relation label is NOT a join witness."),
                metadata={"source_system": _LANE,
                          "lane_id": "derived-" + p.id,
                          "birth_proposal_id": p.id, "parents": list(parents),
                          "worker_registration": p.worker_edition,
                          "cp_lane": cp_lane if len(parents) == 1 else "",
                          "cp_slot": cp_slot if len(parents) == 1 else ""},
            ))
            born.append(hid)
        return {"born_coordination_lanes": born, "open_unstaffed": opened,
                "proposals_considered": len(proposals),
                "execution_started": False, "native_checkpoint_pass": False}

    def admit_native_help(self, coordination_handoff_id: str, *,
                          parent_version: str | None = None,
                          inputs_file: str | Path | None = None,
                          allow_native_admission: bool = False) -> dict:
        """Connect a BIRTH lane to the *existing* source-owned CP helper controls.

        This explicitly invoked operation is not native execution or a parent CP
        witness. Only a single-parent lane mapped to an existing domain CP is
        eligible. Unregistered capabilities remain OPEN_UNSTAFFED.
        """
        from .branch_help import open_and_staff_known
        runtime = self._runtime()
        handoff = runtime.get(_nonblank(coordination_handoff_id, "coordination ID"))
        meta = handoff.metadata
        if meta.get("source_system") != _LANE or not meta.get("birth_proposal_id"):
            raise ValueError("source is not a derived continuation lane")
        parents = meta.get("parents") or []
        if len(parents) != 1 or not meta.get("cp_lane") or not meta.get("cp_slot"):
            raise ValueError("native CP helper requires one domain-bound parent")
        capability = handoff.inputs.get("requested_capability")
        observation_ids = handoff.inputs.get("source_observation_ids") or []
        if len(observation_ids) != 1:
            raise ValueError("native CP help requires one source observation")
        _, _, _, observations, _ = self._snapshot()
        matches = [o for o in observations if o.id == observation_ids[0]]
        if (len(matches) != 1 or matches[0].kind != "BRANCH"
                or matches[0].lane_id != parents[0]
                or matches[0].capability != capability
                or matches[0].relation != handoff.referent
                or not self.verify_observation(matches[0])):
            raise ValueError("native help source observation not freshly verified")
        opening_key = "wh-" + meta["birth_proposal_id"]
        assigned = open_and_staff_known(
            data_dir=self.data_dir, lane=meta["cp_lane"], slot=meta["cp_slot"],
            capability=capability, opening_key=opening_key,
            reason="Witnessed workstation branch: " + handoff.referent,
            parent_version=parent_version, inputs_file=inputs_file,
            allow_native_admission=allow_native_admission,
        )
        child_job = assigned.get("child")
        if child_job:
            events = runtime.event_store.for_handoff(handoff.handoff_id)
            expected = {"opening_id": assigned["opening_id"],
                        "job_id": child_job["job_id"]}
            recorded = [e for e in events if e.event_type == "WORKSTATION_NATIVE_HELP_ASSIGNED"]
            if recorded and any(e.data != expected for e in recorded):
                raise ValueError("conflicting native assignment")
            if not recorded:
                state = runtime.state(handoff.handoff_id)
                runtime.event_store.append(HandoffEvent.create(
                    handoff_id=handoff.handoff_id,
                    event_type="WORKSTATION_NATIVE_HELP_ASSIGNED",
                    actor_id="workstation-continuation",
                    data=expected,
                    parents=(state.last_event_id,) if state.last_event_id else (),
                ))
        return {"coordination_handoff_id": handoff.handoff_id,
                "native_help": assigned, "execution_started": False,
                "native_checkpoint_pass": False}
