"""Native-local, *in-process* CP30 owner/snapshot observation boundary.

Only the source-owning caller may supply live native RouteBoundTask objects. Native registry.verify may invalidate a bad pin in memory. This
module never turns GitHub declarations or signed bytes into OwnerPinRegistry
objects; it does not enroll owners, write journals, or spawn a worker.

An opt-in fresh audit invokes the recovered CP28 native audit_route / consume,
not the CP29 transfer receipt or CP30 independent-process identity protocol.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from hashlib import sha256
from importlib import import_module
import json
from pathlib import Path
import re
from typing import Any

_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}\Z")
_MODULES = ("ab_chatbot_certificate_handoff", "ab_chatbot_route_bound_task",
            "ab_chatbot_shared_route_certificate")


def _native(root: str | Path):
    """Resolve already-imported native modules, never execute a path from JSON."""
    folder = Path(root).resolve(strict=True)
    if not folder.is_dir() or folder.is_symlink():
        raise ValueError("native source root must be a real directory")
    result = {}
    for name in _MODULES:
        module = import_module(name)
        path = Path(getattr(module, "__file__", "")).resolve(strict=True)
        if path.parent != folder or path.name != name + ".py":
            raise ValueError("native CP30 module not loaded from selected source root")
        result[name] = module
    return result


def _snapshot(tasks: Mapping[str, Any], native: dict) -> tuple[dict, tuple]:
    contract, route = native[_MODULES[0]], native[_MODULES[1]]
    if not isinstance(tasks, dict) or not 1 <= len(tasks) <= 16:
        raise ValueError("live provider must return 1..16 distinct native tasks")
    if any(type(k) is not str or not _NAME.fullmatch(k) for k in tasks):
        raise ValueError("invalid live task identifier")
    values = list(tasks.values())
    if len({id(v) for v in values}) != len(values):
        raise ValueError("distinct task objects required")
    if any(type(t) is not contract.RouteBoundTask or not contract._bound(t) for t in values):
        raise ValueError("source must supply live, admitted native CP30 route tasks")
    first = values[0]
    if any(t._route is not first._route or t.route_name != first.route_name or
           t.expected != first.expected for t in values):
        raise ValueError("all tasks must select one exact live native route")
    chain = first._route
    pins = (chain.first.donor, chain.first.recipient, chain.final)
    scope_summary = []
    stable_handles = [id(chain)]
    for index, pin in enumerate(pins):
        pair = (pin.old, pin.new)
        tokens = pin._base._tokens
        if (len(tokens) != 2 or not all(pin.registry.verify(token, bridge)
                                         for token, bridge in zip(tokens, pair))):
            raise ValueError("native source owner pin is revoked, replaced or unproved")
        for bridge in pair:
            if (bridge.owner is None or bridge.origin_scope != "LOCAL_OWNER_VERIFIED" or
                    bridge._scope(bridge.snapshot) != "LOCAL_OWNER_VERIFIED"):
                raise ValueError("native snapshot is not live locally verified owner evidence")
            stable_handles.extend((id(pin.registry), id(bridge), id(bridge.owner), id(bridge.snapshot)))
        scope_summary.append({"position": ("donor", "middle", "final")[index],
                              "old_edges": len(pin.old.snapshot.edges),
                              "new_edges": len(pin.new.snapshot.edges),
                              "local_native_pins_valid": True})
    evidence = route._route_evidence(chain)
    # This is a local fingerprint of native in-memory source evidence, NOT an
    # external GitHub file digest, receipt or transferable authority.
    source_digest = sha256(json.dumps(evidence, sort_keys=True,
                       separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    return {"route": first.route_name, "route_fingerprint": first.expected,
            "local_evidence_sha256": source_digest, "scopes": scope_summary,
            "tasks": sorted(tasks), "source_kind": "native-in-process-owner-pin"}, \
           (tuple((key, id(tasks[key]), tasks[key].task_fingerprint) for key in sorted(tasks)),
            tuple(stable_handles), route._route_structure(chain), evidence)


def observe_native_owners(*, native_source_root: str | Path,
                          source_capture: Callable[[], Mapping[str, Any]],
                          allow_native_audit: bool = False) -> dict:
    """Double-capture exact native objects; optional *current* two-pass audit.

    The source_capture callback executes trusted in-process owner code. It must
    supply the SAME task and snapshot objects in both captures. External JSON,
    URLs and signed claims are never accepted as substitute owner objects.
    This is not a network API or a security boundary for untrusted Python.
    """
    if not callable(source_capture):
        raise ValueError("source-owned live capture callback required")
    if type(allow_native_audit) is not bool:
        raise ValueError("explicit boolean native-audit flag required")
    native = _native(native_source_root)
    tasks = source_capture()
    before, bound_before = _snapshot(tasks, native)
    outcomes = []
    audit_status = "NOT_REQUESTED"
    if allow_native_audit:
        first = next(iter(tasks.values()))
        shared = native[_MODULES[2]]
        audit = shared.audit_route(first)
        audit_status = audit.status
        if audit.status == "TWO_HOP_CHAIN_WITNESSED":
            for name, task in tasks.items():
                answer = shared.consume(task, audit)
                outcomes.append({"name": name, "status": answer.status,
                                 "obligation_count": len(answer.obligations),
                                 "all_obligations_admitted": answer.status == "TASK_COMPLETED_ON_SELECTED_ROUTE"})
    # A second owner callback must return the SAME task/snapshot handles. A
    # replacement or withdrawn owner is not a fresh witness for the old task.
    after_tasks = source_capture()
    after, bound_after = _snapshot(after_tasks, native)
    if before != after or bound_before != bound_after:
        raise ValueError("native source or owner task changed during live observation")
    successful_audit = allow_native_audit and audit_status == "TWO_HOP_CHAIN_WITNESSED"
    return {"status": ("NATIVE_LOCAL_ROUTE_FRESHLY_REAUDITED" if successful_audit else
                       "NATIVE_ROUTE_UNPROVED" if allow_native_audit else
                       "NATIVE_LOCAL_PINNED_SOURCE_OBSERVED"),
            **before, "audit_requested": allow_native_audit,
            "native_audit_status": audit_status,
            "fresh_native_two_pass_route_audit": successful_audit,
            "task_results": outcomes,
            "all_declared_tasks_completed": bool(outcomes) and all(
                row["all_obligations_admitted"] for row in outcomes),
            "same_live_native_objects_recaptured": True,
            "local_owner_pins_verified": True,
            "external_owner_identity_authenticated": False,
            "external_signed_observation_mapped_to_native": False,
            "cp30_independent_process_attestation_verified": False,
            "cp29_receipt_revalidated": False,
            "new_transition_observations": False,
            "runtime_handoff_admitted": False, "journal_modified": False,
            "note": "Native LOCAL_OWNER_VERIFIED objects only; no external source equivalence established."}
