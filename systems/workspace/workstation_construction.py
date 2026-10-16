"""B9: proposal-only construction over the existing workstation RuntimeJournal.

Continuous handoff carries candidate requirements and provenance even when the
intermediate relation is unknown. These records NEVER certify a relation,
register a worker, authorize execution, or replace native observation.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Callable

from runtime.engine import HandoffRuntime
from runtime.handoff import Handoff, HandoffEvent
from runtime.journal import RuntimeJournal

SOURCE = "workstation-candidate-construction/v1"
OBSERVED = "WORKSTATION_CANDIDATE_OBSERVATION_RECORDED"
LINK = "WORKSTATION_CONSTRUCTION_LINK_PROPOSED"
SOURCE_SUGGESTED = "WORKSTATION_CONSTRUCTION_SOURCE_SUGGESTED"
_UNPROVEN = (
    "Candidate construction is not native evidence or authorization.",
    "The relationship remains proposed until independently observed.",
    "No B2 birth, cross-lane join, or native worker execution is implied.",
)


def _text(value: str, label: str, length: int = 240) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > length:
        raise ValueError(f"{label} must be a nonempty bounded string")
    return value.strip()


def _digest(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


def _key(*parts: str) -> str:
    return "whc-" + _digest(parts)[:32]


def _contract_verdict(value: str) -> str:
    """Read-only vocabulary mapping to the repository's 2026 handoff contract.

    Persisted records keep their original spelling and exact receipt digest;
    translating the projection is NEVER a replacement native determination.
    """
    return {"UNRESOLVED": "UNKNOWN", "UNDETERMINED": "PROPOSED"}.get(value, value)


@dataclass(frozen=True)
class Receipt:
    """A source-observer claim; native source must independently verify it."""
    candidate_id: str
    verdict: str  # SUPPORTED, CONTRADICTED, UNKNOWN (legacy UNRESOLVED retained)
    witness_ref: str
    native_source: str
    relation_scope: str
    source_report_sha256: str
    candidate_spec_sha256: str


class WorkstationConstruction:
    """Build possible prerequisite paths backward without declaring them true."""

    def __init__(self, data_dir: str | Path):
        self.data_dir = Path(data_dir)

    def _runtime(self) -> HandoffRuntime:
        return HandoffRuntime(event_store=RuntimeJournal(self.data_dir / "runtime.jsonl"))

    @staticmethod
    def _node(runtime: HandoffRuntime, node_id: str) -> Handoff:
        try:
            node = runtime.get(_text(node_id, "candidate ID", 120))
        except KeyError as exc:
            raise ValueError("unknown B9 candidate") from exc
        if node.metadata.get("source_system") != SOURCE:
            raise ValueError("not a B9 candidate; source-owned worker boundary preserved")
        return node

    def _admit(self, node: Handoff) -> str:
        runtime = self._runtime()
        if node.handoff_id in runtime._handoffs:
            if runtime.get(node.handoff_id) != node:
                raise ValueError("candidate identity collision or changed contract")
            return node.handoff_id
        runtime.submit(node)
        return node.handoff_id

    def goal(self, required_result: str, *, provenance: str) -> str:
        result, origin = _text(required_result, "required result"), _text(provenance, "provenance")
        gid = _key("GOAL", result, origin)
        return self._admit(Handoff(
            handoff_id=gid, referent=result,
            from_actor="workstation-construction", to_actor="workstation-candidate-review",
            required_relation="preserve required result and its possible prerequisites",
            inputs={"required_result": result},
            expected_output={"construction": "candidate prerequisites, NOT proof"},
            provenance=(origin,), boundaries=_UNPROVEN,
            metadata={"source_system": SOURCE, "node_kind": "GOAL", "goal_id": gid,
                      "downstream_id": "", "path_role": "ROOT", "capability_hint": ""},
        ))

    def candidate(self, downstream_id: str, requirement: str, *,
                  provenance: str, path_role: str = "REQUIRED",
                  capability_hint: str = "", input_contract: str = "") -> str:
        """Candidate could supply a downstream result, not necessarily does."""
        if path_role not in ("REQUIRED", "ALTERNATIVE"):
            raise ValueError("path role must distinguish required step vs alternative")
        req = _text(requirement, "candidate requirement")
        origin = _text(provenance, "candidate provenance")
        capability = _text(capability_hint, "capability hint") if capability_hint else ""
        inputs = _text(input_contract, "input contract") if input_contract else ""
        runtime = self._runtime()
        downstream = self._node(runtime, downstream_id)
        gid = downstream.metadata["goal_id"]
        cid = _key("CANDIDATE", downstream.handoff_id, path_role, req, origin, capability, inputs)
        return self._admit(Handoff(
            handoff_id=cid, referent=req,
            from_actor="workstation-construction", to_actor="workstation-candidate-review",
            required_relation="propose possible upstream relationship",
            inputs={"candidate_requirement": req, "input_contract": inputs,
                    "downstream_id": downstream.handoff_id},
            expected_output={"next": "source observation or further candidate construction"},
            provenance=(origin, "candidate-downstream:" + downstream.handoff_id),
            boundaries=_UNPROVEN,
            metadata={"source_system": SOURCE, "node_kind": "CANDIDATE", "goal_id": gid,
                      "downstream_id": downstream.handoff_id, "path_role": path_role,
                      "capability_hint": capability},
        ))

    @staticmethod
    def _arcs(runtime: HandoffRuntime, goal_id: str) -> set[tuple[str, str]]:
        nodes = {h.handoff_id: h for h in runtime._handoffs.values()
                 if h.metadata.get("source_system") == SOURCE
                 and h.metadata.get("goal_id") == goal_id}
        arcs = {(h.handoff_id, h.metadata["downstream_id"])
                for h in nodes.values() if h.metadata.get("downstream_id")}
        for event in runtime.event_store.all():
            if event.event_type == LINK and event.handoff_id in nodes:
                source = event.data.get("upstream_id")
                if source not in nodes:
                    raise ValueError("persisted candidate link references unavailable source")
                arcs.add((source, event.handoff_id))
        return arcs

    def propose_connection(self, upstream_id: str, downstream_id: str, *, reason: str) -> str:
        """Explore a possible source-to-requirement link, never a verified join."""
        explanation = _text(reason, "proposal rationale")
        runtime = self._runtime()
        up = self._node(runtime, upstream_id)
        down = self._node(runtime, downstream_id)
        if up.handoff_id == down.handoff_id or up.metadata["goal_id"] != down.metadata["goal_id"]:
            raise ValueError("candidate link must connect distinct nodes of one goal")
        link_id = "whlink-" + _digest((up.handoff_id, down.handoff_id, explanation))[:32]
        prior = [e for e in runtime.event_store.for_handoff(down.handoff_id)
                 if e.event_type == LINK and e.data.get("link_id") == link_id]
        data = {"link_id": link_id, "upstream_id": up.handoff_id,
                "reason": explanation, "relation_state": "PROPOSED_NOT_OBSERVED"}
        if prior:
            if len(prior) != 1 or prior[0].data != data:
                raise ValueError("candidate link collision")
            return link_id
        arcs = self._arcs(runtime, up.metadata["goal_id"])
        # New edge upstream -> downstream; reject an existing downstream -> upstream path.
        frontier = [down.handoff_id]
        visited: set[str] = set()
        while frontier:
            here = frontier.pop()
            if here == up.handoff_id:
                raise ValueError("candidate link would create a construction cycle")
            if here in visited:
                continue
            visited.add(here)
            frontier.extend(dst for src, dst in arcs if src == here)
        state = runtime.state(down.handoff_id)
        runtime.event_store.append(HandoffEvent.create(
            handoff_id=down.handoff_id, event_type=LINK,
            actor_id="workstation-candidate-construction", data=data,
            parents=(state.last_event_id,) if state.last_event_id else (),
        ))
        return link_id

    def suggest_source(self, candidate_id: str, *, worker_id: str,
                       edition_ref: str, source_locator: str, reason: str) -> str:
        """Connect a candidate to a possible source WITHOUT asserting availability.

        Even a known repository/source version does not prove the capability
        fits this step. Only the source-owning observation layer can determine
        that relation, and execution still requires separate native admission.
        """
        worker = _text(worker_id, "worker ID", 120)
        edition = _text(edition_ref, "edition reference", 200)
        locator = _text(source_locator, "source locator", 300)
        why = _text(reason, "source selection rationale")
        runtime = self._runtime()
        node = self._node(runtime, candidate_id)
        proposal_id = "whsource-" + _digest((node.handoff_id, worker, edition, locator, why))[:32]
        data = {"proposal_id": proposal_id, "worker_id": worker,
                "edition_ref": edition, "source_locator": locator, "reason": why,
                "source_presence": "NOT_VERIFIED_HERE",
                "capability_fit": "UNDETERMINED",
                "execution_authorized": False}
        previous = [e for e in runtime.event_store.for_handoff(node.handoff_id)
                    if e.event_type == SOURCE_SUGGESTED
                    and e.data.get("proposal_id") == proposal_id]
        if previous:
            if len(previous) != 1 or previous[0].data != data:
                raise ValueError("source suggestion collision")
            return proposal_id
        state = runtime.state(node.handoff_id)
        runtime.event_store.append(HandoffEvent.create(
            handoff_id=node.handoff_id, event_type=SOURCE_SUGGESTED,
            actor_id="workstation-candidate-construction", data=data,
            parents=(state.last_event_id,) if state.last_event_id else (),
        ))
        return proposal_id

    def inspect(self, goal_id: str) -> dict:
        """Projection of constructed proposals. Historical claims aren't live proof."""
        runtime = self._runtime()
        goal = self._node(runtime, goal_id)
        if goal.metadata["node_kind"] != "GOAL":
            raise ValueError("inspect requires root goal")
        nodes = [h for h in runtime._handoffs.values()
                 if h.metadata.get("source_system") == SOURCE
                 and h.metadata.get("goal_id") == goal_id]
        arcs = sorted(self._arcs(runtime, goal_id))
        projection = []
        for h in nodes:
            reports = [e for e in runtime.event_store.for_handoff(h.handoff_id)
                       if e.event_type == OBSERVED]
            source_options = [dict(e.data) for e in runtime.event_store.for_handoff(h.handoff_id)
                              if e.event_type == SOURCE_SUGGESTED]
            projection.append({
                "id": h.handoff_id, "requirement": h.referent,
                "kind": h.metadata["node_kind"], "path_role": h.metadata["path_role"],
                "capability_hint": h.metadata["capability_hint"],
                "downstream_id": h.metadata["downstream_id"],
                "historical_verdict": reports[-1].data["verdict"] if reports else "UNDETERMINED",
                "contract_state": _contract_verdict(reports[-1].data["verdict"] if reports else "UNDETERMINED"),
                "observation_count": len(reports), "source_options": source_options,
                "current_native_verification": False,
                "native_execution_admitted": False,
            })
        leaves = sorted(h.handoff_id for h in nodes
                        if h.handoff_id not in {b for a, b in arcs} and h.handoff_id != goal_id)
        return {"goal_id": goal_id, "source_system": SOURCE,
                "nodes": sorted(projection, key=lambda n: n["id"]),
                "candidate_links": arcs, "next_possible_upstream_nodes": leaves,
                "claims_native_completion": False, "execution_started": False}


    def next_construction_handoffs(self, goal_id: str, *, max_paths_per_leaf: int = 16,
                                   max_total_paths: int = 512,
                                   max_path_depth: int = 128,
                                   max_total_route_steps: int = 65536) -> dict:
        """Read-only candidate handoffs, including every upstream-to-goal route.

        This is a construction frontier, NOT an executable runtime handoff.
        A historical observation is not assumed to remain source-verified.
        Every possible route and worker hint retains its unproven status.
        """
        if type(max_paths_per_leaf) is not int or not 1 <= max_paths_per_leaf <= 256:
            raise ValueError("path bound must be an integer from 1 to 256")
        if type(max_total_paths) is not int or not 1 <= max_total_paths <= 4096:
            raise ValueError("total path bound must be an integer from 1 to 4096")
        if type(max_path_depth) is not int or not 1 <= max_path_depth <= 4096:
            raise ValueError("path depth bound must be an integer from 1 to 4096")
        if (type(max_total_route_steps) is not int or
                not 1 <= max_total_route_steps <= 65536):
            raise ValueError("total route step bound must be an integer from 1 to 65536")
        runtime = self._runtime()
        root = self._node(runtime, goal_id)
        if root.metadata.get("node_kind") != "GOAL":
            raise ValueError("construction handoffs require a root goal")
        source_nodes = {h.handoff_id: h for h in runtime._handoffs.values()
                        if h.metadata.get("source_system") == SOURCE
                        and h.metadata.get("goal_id") == goal_id}
        arcs = self._arcs(runtime, goal_id)
        downstream: dict[str, set[str]] = {hid: set() for hid in source_nodes}
        for up, down in arcs:
            if up not in source_nodes or down not in source_nodes:
                raise ValueError("constructed path escapes its source-owned goal")
            downstream[up].add(down)
        leaves = sorted(set(source_nodes) - {dest for _, dest in arcs})
        if not leaves:
            raise ValueError("construction frontier has no root-reachable leaf")
        # Build an immutable read-only observation projection for *every*
        # candidate. A historical result in a middle requirement must not be
        # silently dropped when the frontier only reports upstream leaves.
        history_by_node = {}
        for node_id, node in source_nodes.items():
            events = runtime.event_store.for_handoff(node_id)
            observed = [e for e in events if e.event_type == OBSERVED]
            suggestions = [e for e in events if e.event_type == SOURCE_SUGGESTED]
            latest = observed[-1].data.get("verdict") if observed else "UNDETERMINED"
            if latest not in ("UNDETERMINED", "SUPPORTED", "CONTRADICTED",
                              "UNKNOWN", "UNRESOLVED"):
                raise ValueError("unrecognized recorded candidate determination")
            history_by_node[node_id] = {
                "latest": latest,
                "receipts": tuple({
                    "observation_id": e.data.get("observation_id"),
                    "verdict": e.data.get("verdict"),
                    "contract_verdict": _contract_verdict(e.data.get("verdict")),
                    "relation_scope": e.data.get("relation_scope"),
                    "native_source": e.data.get("native_source"),
                    "witness_ref": e.data.get("witness_ref"),
                    "source_report_sha256": e.data.get("source_report_sha256"),
                    "current_native_verification": False,
                } for e in observed),
                "sources": tuple({
                    "worker_id": e.data.get("worker_id"),
                    "edition_ref": e.data.get("edition_ref"),
                    "source_locator": e.data.get("source_locator"),
                    "reason": e.data.get("reason"),
                    "capability_fit": "UNDETERMINED",
                    "execution_authorized": False,
                } for e in suggestions),
            }
        link_reasons: dict[tuple[str, str], list[str]] = {}
        for event in runtime.event_store.all():
            if event.event_type == LINK and event.handoff_id in source_nodes:
                pair = (event.data.get("upstream_id"), event.handoff_id)
                if pair not in arcs:
                    raise ValueError("recorded proposal is outside declared construction graph")
                link_reasons.setdefault(pair, []).append(event.data.get("reason", ""))

        handoffs = []
        total_paths = 0
        total_route_steps = 0
        for leaf in leaves:
            routes: list[tuple[str, ...]] = []
            # Iterative traversal: even very deep proposed paths cannot exhaust
            # Python recursion. Exceeding ANY limit rejects the whole frontier;
            # never return a silently truncated or selectively omitted route.
            stack = [(leaf, (leaf,))]
            while stack:
                here, path = stack.pop()
                if len(path) > max_path_depth:
                    raise ValueError("construction path depth bound exceeded")
                if here == goal_id:
                    routes.append(path)
                    total_paths += 1
                    if len(routes) > max_paths_per_leaf:
                        raise ValueError("candidate has no bounded path to required result")
                    if total_paths > max_total_paths:
                        raise ValueError("construction total path bound exceeded")
                    continue
                for nxt in sorted(downstream[here], reverse=True):
                    if nxt in path:
                        raise ValueError("candidate graph contains a cycle")
                    if len(path) == max_path_depth:
                        raise ValueError("construction path depth bound exceeded")
                    stack.append((nxt, (*path, nxt)))
            if not routes:
                raise ValueError("candidate has no bounded path to required result")
            node = source_nodes[leaf]
            current = history_by_node[leaf]
            last = current["latest"]
            next_kind = {
                "CONTRADICTED": "REVISE_OR_EXPLORE_ALTERNATIVE",
                "SUPPORTED": "RECHECK_OR_CONSTRUCT_REMAINDER",
                "UNKNOWN": "OBSERVE_OR_DECOMPOSE_FURTHER",
                "UNRESOLVED": "OBSERVE_OR_DECOMPOSE_FURTHER",
                "UNDETERMINED": "OBSERVE_OR_DECOMPOSE_FURTHER",
            }[last]
            source_hints = current["sources"]
            receipt_history = current["receipts"]

            # Every possible route is projected with the observation history
            # of *each* upstream requirement, not only that of the leaf.
            # Proposal-only links are explicitly distinguishable from native
            # child/downstream declarations. Neither form proves a join.
            scoped_routes = []
            for route in routes:
                total_route_steps += len(route) - 1
                if total_route_steps > max_total_route_steps:
                    raise ValueError("construction total route step bound exceeded")
                steps = []
                for upstream_id, downstream_id in zip(route, route[1:]):
                    upstream = source_nodes[upstream_id]
                    context = history_by_node[upstream_id]
                    direct = upstream.metadata.get("downstream_id") == downstream_id
                    steps.append({
                        "upstream_id": upstream_id,
                        "downstream_id": downstream_id,
                        "candidate_requirement": upstream.referent,
                        "input_contract": upstream.inputs.get("input_contract", ""),
                        "path_role": upstream.metadata.get("path_role"),
                        "provenance": tuple(upstream.provenance),
                        "relation_origin": ("DECLARED_CANDIDATE" if direct
                                            else "PROPOSED_CONNECTION"),
                        "proposal_reasons": tuple(link_reasons.get(
                            (upstream_id, downstream_id), ())),
                        "historical_verdict": context["latest"],
                        "contract_state": _contract_verdict(context["latest"]),
                        "historical_determinations": context["receipts"],
                        "suggested_sources": context["sources"],
                        "current_native_relation_verified": False,
                        "execution_authorized": False,
                    })
                if not steps:
                    route_state = "REQUIRES_CONSTRUCTION"
                elif any(any(x["contract_verdict"] == "CONTRADICTED"
                             for x in step["historical_determinations"])
                         for step in steps):
                    route_state = "HISTORICAL_CONTRADICTION_PRESENT"
                elif any(step["contract_state"] != "SUPPORTED" for step in steps):
                    route_state = "HISTORICALLY_UNDETERMINED"
                else:
                    route_state = "HISTORICAL_LOCAL_SUPPORT_ONLY"
                route_movement = {
                    "REQUIRES_CONSTRUCTION": "DECOMPOSE_REQUIRED_RESULT",
                    "HISTORICAL_CONTRADICTION_PRESENT": "REVISE_OR_EXPLORE_ALTERNATIVE",
                    "HISTORICALLY_UNDETERMINED": "OBSERVE_OR_DECOMPOSE_FURTHER",
                    "HISTORICAL_LOCAL_SUPPORT_ONLY": "RECHECK_OR_CONSTRUCT_REMAINDER",
                }[route_state]
                scoped_routes.append({
                    "candidate_ids": route,
                    "steps": tuple(steps),
                    "historical_route_state": route_state,
                    "next_construction_movement": route_movement,
                    "whole_route_verified": False,
                    "join_observed": False,
                    "execution_authorized": False,
                })
            handoffs.append({
                "candidate_id": leaf,
                "requirement": node.referent,
                "input_contract": node.inputs.get("input_contract", ""),
                "capability_hint": node.metadata.get("capability_hint", ""),
                "path_role": node.metadata.get("path_role"),
                "provenance": tuple(node.provenance),
                "candidate_spec_sha256": _digest(asdict(node)),
                "possible_routes_to_result": tuple(routes),
                "routes_with_observational_context": tuple(scoped_routes),
                "historical_observation": last,
                "contract_state": _contract_verdict(last),
                "historical_receipt_count": len(receipt_history),
                "historical_determinations": receipt_history,
                "suggested_sources": source_hints,
                "next_construction_movement": next_kind,
                "current_source_verified": False,
                "native_admission": False,
            })
        return {"goal_id": goal_id, "required_result": root.referent,
                "construction_handoffs": tuple(handoffs),
                "claim_scope": "candidate construction only",
                "whole_chain_verified": False, "execution_authorized": False}


class ObservationalDetermination:
    """Only source-native verification can record a scoped evidence determination.

    The caller MUST supply an independent verifier for the exact native source.
    Merely supplying a receipt, hash, or label cannot claim support.
    """

    def __init__(self, construction: WorkstationConstruction, *,
                 verify_native_receipt: Callable[[Receipt], bool]):
        if not callable(verify_native_receipt):
            raise ValueError("an independent source-native receipt verifier is required")
        self.graph = construction
        self.verify_native_receipt = verify_native_receipt

    def _verify(self, receipt: Receipt) -> Handoff:
        if not isinstance(receipt, Receipt) or receipt.verdict not in (
                "SUPPORTED", "CONTRADICTED", "UNKNOWN", "UNRESOLVED"):
            raise ValueError("unsupported or malformed observational determination")
        _text(receipt.witness_ref, "witness reference", 400)
        _text(receipt.native_source, "native source")
        _text(receipt.relation_scope, "observed relation scope")
        if (not isinstance(receipt.source_report_sha256, str)
                or len(receipt.source_report_sha256) != 64
                or any(x not in "0123456789abcdef" for x in receipt.source_report_sha256)):
            raise ValueError("source-owned report must have a SHA-256 content digest")
        runtime = self.graph._runtime()
        candidate = self.graph._node(runtime, receipt.candidate_id)
        if receipt.candidate_spec_sha256 != _digest(asdict(candidate)):
            raise ValueError("observation is not bound to this exact candidate specification")
        if not self.verify_native_receipt(receipt):
            raise ValueError("independent native observation verification rejected receipt")
        return candidate

    def record(self, receipt: Receipt) -> str:
        candidate = self._verify(receipt)
        runtime = self.graph._runtime()
        observation_id = "whdetermination-" + _digest(asdict(receipt))[:32]
        data = {"observation_id": observation_id, **asdict(receipt),
                "observation_scope": "candidate-local; not whole-chain admission"}
        prior = [e for e in runtime.event_store.for_handoff(candidate.handoff_id)
                 if e.event_type == OBSERVED and e.data.get("observation_id") == observation_id]
        if prior:
            if len(prior) != 1 or prior[0].data != data:
                raise ValueError("observation record conflict")
            return observation_id
        state = runtime.state(candidate.handoff_id)
        runtime.event_store.append(HandoffEvent.create(
            handoff_id=candidate.handoff_id, event_type=OBSERVED,
            actor_id="workstation-native-observation", data=data,
            parents=(state.last_event_id,) if state.last_event_id else (),
        ))
        return observation_id

    def recheck(self, candidate_id: str) -> dict:
        """Fresh source verification of historical receipts without changing history."""
        runtime = self.graph._runtime()
        node = self.graph._node(runtime, candidate_id)
        records = [e.data for e in runtime.event_store.for_handoff(node.handoff_id)
                   if e.event_type == OBSERVED]
        current = []
        for row in records:
            receipt = Receipt(**{k: row[k] for k in Receipt.__dataclass_fields__})
            try:
                self._verify(receipt)
                current.append({"verdict": receipt.verdict, "verified_now": True,
                                "observation_id": row["observation_id"]})
            except ValueError:
                current.append({"verdict": receipt.verdict, "verified_now": False,
                                "observation_id": row["observation_id"]})
        return {"candidate_id": node.handoff_id, "determinations": current,
                "whole_path_verified": False, "native_job_authorized": False}

    def receipt_for(self, candidate_id: str, *, verdict: str, witness_ref: str,
                    native_source: str, relation_scope: str,
                    source_report_sha256: str) -> Receipt:
        runtime = self.graph._runtime()
        node = self.graph._node(runtime, candidate_id)
        return Receipt(node.handoff_id, verdict, witness_ref, native_source,
                       relation_scope, source_report_sha256, _digest(asdict(node)))
