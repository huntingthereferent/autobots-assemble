"""Match witnessed external declaration bytes to ALREADY-cached CP30 native edges.

This is a source-content correspondence check, NOT owner equivalence, proof
of a full relation, CP29 receipt acceptance, or a CP30-independent attestation.
The source-owning process supplies real native RouteBoundTask objects. No
untrusted serialized document can create, repin or mutate native owner objects.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from .external_evidence import SCOPES, SourceEvidenceLedger
from .external_route_mapping import map_observed_sources, _strict_object, MAX_BYTES
from .native_owner_observation import _native, _snapshot


def _native_pair_match(scope: str, side: str, declaration: dict, bridge: Any) -> dict:
    """Compare only cached edges, without .step() calls that acquire new edges."""
    snap = bridge.snapshot
    if (declaration["source_label"] != snap.claimed_source or
            declaration["revision"] != snap.revision):
        raise ValueError(f"{scope}/{side}: external source label or revision differs from live native snapshot")
    edges = declaration["claimed_edges"]
    if type(edges) is not list or not edges:
        raise ValueError(f"{scope}/{side}: at least one exact observed edge required")
    cached = getattr(snap, "edges", None)
    if type(cached) is not dict:
        raise ValueError(f"{scope}/{side}: native snapshot lacks a cached edge witness")
    owner_view = getattr(snap, "owner_view", None)
    if owner_view is None or bridge.owner.select(snap.revision) is not owner_view:
        raise ValueError(f"{scope}/{side}: native cached edge is not attached to exact owner-held revision")
    for entry in edges:
        state = tuple(entry["state"])
        target = tuple(entry["target"])
        key = (state, entry["action"])
        if key not in cached:
            raise ValueError(f"{scope}/{side}: declared edge was not witnessed in native cache")
        if cached[key] != target or owner_view.step(state, entry["action"]) != target:
            raise ValueError(f"{scope}/{side}: declared edge contradicts native cached/owner-held target")
    return {"source_label": snap.claimed_source, "revision": snap.revision,
            "declared_edges_matched": len(edges),
            "native_cached_edges_at_capture": len(cached),
            "owner_view_digest": snap.digest,
            "full_native_transition_table_matched": False}


def bind_external_observation_to_native(*,
        data_dir: str | Path, challenge: str, observation_event: str,
        source_files: dict[str, str | Path], native_source_root: str | Path,
        source_capture: Callable[[], Mapping[str, Any]]) -> dict:
    """Read-only comparison inside trusted source process, with two native captures.

    Signed/public observations are independently checked by the existing mapper.
    No network, journal writes, task admission, pin issuance or route replay.
    """
    if not callable(source_capture):
        raise ValueError("explicit source-owned native capture callback required")
    if type(source_files) is not dict or set(source_files) != set(SCOPES):
        raise ValueError("exact donor/middle/final source-file copies required")
    native = _native(native_source_root)
    tasks = source_capture()
    before, bound_before = _snapshot(tasks, native)
    # Check the accepted observation and all six local files against its signed
    # digest and live enrollment state BEFORE interpreting any external claims.
    store = SourceEvidenceLedger(data_dir)
    initial_history = store.history()
    initial_tip = initial_history[-1]["event_hash"] if initial_history else None
    mapped = map_observed_sources(data_dir=data_dir, challenge=challenge,
                                  observation_event=observation_event,
                                  source_files=source_files)
    if (mapped["route"] != before["route"] or
            mapped["declared_route_fingerprint"] != before["route_fingerprint"]):
        raise ValueError("signed external route referent does not match selected native route")
    first = next(iter(tasks.values()))
    chain = first._route
    pins = (chain.first.donor, chain.first.recipient, chain.final)
    matches, hashes = {}, {}
    for scope, pin in zip(SCOPES, pins):
        file = Path(source_files[scope])
        if file.is_symlink() or not file.is_file() or file.stat().st_size > MAX_BYTES:
            raise ValueError("external observed source copy unavailable or unsafe")
        payload = file.read_bytes()
        if sha256(payload).hexdigest() != mapped["scopes"][scope]["source_sha256"]:
            raise ValueError("external declaration bytes changed since signed observation")
        obj = json.loads(payload, object_pairs_hook=_strict_object,
                         parse_constant=lambda _: (_ for _ in ()).throw(ValueError("invalid JSON constant")))
        matches[scope] = {side: _native_pair_match(scope, side, obj[side], getattr(pin, side))
                          for side in ("old", "new")}
        hashes[scope] = sha256(payload).hexdigest()
    # Recheck both sources after the comparison and reject a moving journal;
    # in-process identity cannot solve arbitrary multi-process race conditions.
    recaptured = source_capture()
    after, bound_after = _snapshot(recaptured, native)
    if before != after or bound_before != bound_after:
        raise ValueError("native owner, snapshot, task or route changed during external binding")
    for scope in SCOPES:
        file = Path(source_files[scope])
        if file.is_symlink() or sha256(file.read_bytes()).hexdigest() != hashes[scope]:
            raise ValueError("signed external declaration changed during native binding")
    final_history = store.history()
    if (final_history[-1]["event_hash"] if final_history else None) != initial_tip:
        raise ValueError("signed observation journal changed during native binding")
    count = sum(matches[s][side]["declared_edges_matched"]
                for s in SCOPES for side in ("old", "new"))
    return {"status": "EXTERNAL_DECLARED_EDGES_MATCH_NATIVE_LOCAL_CACHE",
            "challenge": challenge, "observation_event": observation_event,
            "route": before["route"], "native_route_fingerprint": before["route_fingerprint"],
            "declared_witness_sha256": mapped["declared_witness_sha256"],
            "scopes": matches, "matched_declared_edges": count,
            "matched_native_sides": 6,
            "external_bytes_match_signed_observation": True,
            "native_in_process_owner_pins_current_at_both_captures": True,
            "cached_edges_match_declared_transitions": True,
            "same_live_native_objects_recaptured": True,
            "external_source_identity_authenticated": False,
            "external_owner_equivalence_proved": False,
            "full_native_transition_tables_matched": False,
            "native_cp30_route_certificate_verified": False,
            "fresh_native_two_pass_route_audit": False,
            "cp30_independent_process_attestation_verified": False,
            "cp29_receipt_revalidated": False,
            "exact_task_authorized": False,
            "native_handoff_admitted": False,
            "new_transition_observations": False,
            "journal_modified": False,
            "note": "Exact signed claims match ALREADY-cached locally pinned transitions. No external owner equivalence, route proof, or task authorization follows."}
