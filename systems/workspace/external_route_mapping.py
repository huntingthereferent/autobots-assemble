"""Read-only mapping of observed *external claims* to CP30's unmet native gates.

This does NOT create CP30 owner/pin objects or admit a route task. CP30's real
OwnerPinRegistry.issue requires a live LOCAL_OWNER_VERIFIED in-process bridge,
which a digest, public key or serialized external file cannot supply.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from .external_evidence import SourceEvidenceLedger, SCOPES, _parse_time

KIND = "cp30-external-finite-declaration/v1"
SIDES = ("old", "new")
MAX_BYTES = 1_048_576
MAX_AGE = timedelta(minutes=10)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _triple(v: Any) -> tuple[int, int, int]:
    if type(v) is not list or len(v) != 3 or any(type(x) is not int or x not in (0, 1, 2) for x in v):
        raise ValueError("external finite declaration must use F3 triples")
    return tuple(v)


def _step(phi: tuple[int, int, int], state: tuple[int, int, int], action: str) -> tuple[int, int, int]:
    x, y, z = state
    if action == "A":
        return ((x + 1) % 3, y, z)
    if action == "B":
        return (x, (y + x + 1) % 3, (z + phi[y]) % 3)
    raise ValueError("external finite declaration allows only A/B")


def _side(value: Any) -> dict:
    if type(value) is not dict or set(value) != {"source_label", "revision", "phi", "claimed_edges"}:
        raise ValueError("external finite source side contract invalid")
    label, rev = value["source_label"], value["revision"]
    if (type(label) is not str or not 1 <= len(label) <= 80 or
            any(not (c.isascii() and (c.isalnum() or c in "_.-")) for c in label) or
            type(rev) is not int or not 0 <= rev <= 1_000_000):
        raise ValueError("invalid claimed source label/revision")
    phi = _triple(value["phi"])
    edges = value["claimed_edges"]
    if type(edges) is not list or len(edges) > 64:
        raise ValueError("at most 64 claimed finite edges per side")
    unique = set()
    for item in edges:
        if type(item) is not dict or set(item) != {"state", "action", "target"}:
            raise ValueError("malformed claimed finite edge")
        state, target = _triple(item["state"]), _triple(item["target"])
        action = item["action"]
        if action not in ("A", "B"):
            raise ValueError("unknown claimed finite action")
        if (state, action) in unique:
            raise ValueError("duplicate claimed finite edge")
        unique.add((state, action))
        if _step(phi, state, action) != target:
            raise ValueError("claimed edge contradicts its own declared finite law")
    return {"source_label": label, "revision": rev, "law_phi": list(phi),
            "claim_edge_count": len(edges)}


def validate_declaration(data: Any, *, scope: str, challenge_record: dict) -> dict:
    """Check bounded content syntax and internal F3-law consistency, not witness truth."""
    expected = {"kind", "scope", "source_id", "challenge", "route",
                "route_fingerprint", "witness_sha256", "old", "new"}
    if type(data) is not dict or set(data) != expected or data.get("kind") != KIND:
        raise ValueError("external finite source declaration shape invalid")
    pinned = challenge_record["pinned_keys"][scope]
    for key, value in {"scope": scope, "source_id": pinned["source_id"],
                       "challenge": challenge_record["challenge"],
                       "route": challenge_record["route"],
                       "route_fingerprint": challenge_record["route_fingerprint"],
                       "witness_sha256": challenge_record["witness_sha256"]}.items():
        if data.get(key) != value:
            raise ValueError(f"external finite declaration differs from signed receiver binding: {key}")
    return {"scope": scope, "source_id": pinned["source_id"],
            "old": _side(data["old"]), "new": _side(data["new"])}


def _observation(store: SourceEvidenceLedger, challenge: str, expected_event: str):
    """Reject stale observation, revoked key or mismatched event; no ledger writes."""
    keys, challenges, accepted, events = store._state()
    if type(challenge) is not str or challenge not in accepted or challenge not in challenges:
        raise ValueError("mapping requires a previously accepted signed challenge")
    observations = [e for e in events if e["kind"] == "SOURCE_OBSERVED" and e["record"].get("challenge") == challenge]
    if len(observations) != 1 or observations[0]["event_hash"] != expected_event:
        raise ValueError("exact previously accepted GitHub observation event required")
    issued = challenges[challenge]
    seen = observations[0]
    now = _now()
    observed_at = _parse_time(seen["record"]["observed_at"])
    if now < observed_at - timedelta(seconds=30) or now - observed_at > MAX_AGE:
        raise ValueError("external observation too old for current declaration mapping")
    accepted_receipt = next(e for e in events if e["kind"] == "EVIDENCE_ACCEPTED" and e["record"]["challenge"] == challenge)
    accepted_at = _parse_time(accepted_receipt["record"]["accepted_at"])
    if observed_at < accepted_at - timedelta(seconds=30) or observed_at - accepted_at > MAX_AGE:
        raise ValueError("observed bytes do not belong to a recently accepted signed receipt")
    signed_index = next(e["seq"] for e in events if e["kind"] == "CHALLENGE_ISSUED" and e["record"]["challenge"] == challenge)
    if any(e["kind"] == "KEY_REVOKED" and e["record"].get("scope") in SCOPES and e["seq"] > signed_index for e in events):
        raise ValueError("external signer enrollment revoked or rotated")
    for scope in SCOPES:
        active = keys.get(scope)
        pin = issued["pinned_keys"][scope]
        if not active or active["source_id"] != pin["source_id"] or active["key_sha256"] != pin["key_sha256"]:
            raise ValueError("external signer enrollment differs from accepted challenge")
    return issued, seen


def _strict_object(pairs):
    row = {}
    for key, value in pairs:
        if key in row:
            raise ValueError("duplicate JSON member in observed source declaration")
        row[key] = value
    return row


def map_observed_sources(*, data_dir: str | Path, challenge: str,
                         observation_event: str, source_files: dict[str, str | Path]) -> dict:
    """Validate operator-provided copies of all observed files; no network or writes.

    A matching digest establishes only that the content corresponds to the
    prior observation; the declaration inside is still a claim, not a native
    CP30 owner-pinned snapshot or independently admitted route certificate.
    """
    if type(source_files) is not dict or set(source_files) != set(SCOPES):
        raise ValueError("exact donor/middle/final local copies required")
    store = SourceEvidenceLedger(data_dir)
    issued, observation = _observation(store, challenge, observation_event)
    summaries = {}
    for scope in SCOPES:
        path = Path(source_files[scope])
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
            raise ValueError("unsafe, absent or oversized local observed source file")
        raw = path.read_bytes()
        digest = sha256(raw).hexdigest()
        recorded = observation["record"]["observations"][scope]
        if len(raw) > MAX_BYTES or digest != recorded["sha256"] or digest != issued["source_digests"][scope] or len(raw) != recorded["size"]:
            raise ValueError(f"local {scope} bytes do not match signed public GitHub observation")
        try:
            data = json.loads(raw, object_pairs_hook=_strict_object, parse_constant=lambda _: (_ for _ in ()).throw(ValueError("invalid JSON constant")))
        except (UnicodeDecodeError, ValueError) as exc:
            raise ValueError("external source is not a valid JSON declaration") from exc
        summary = validate_declaration(data, scope=scope, challenge_record=issued)
        summaries[scope] = {**summary, "source_sha256": digest,
                            "observed_commit_sha1": recorded["commit_sha1"]}
    # Unlike CP30's in-process OwnerPinRegistry, external claims cannot bind
    # real local-owner objects, exact object identity or live source audit.
    return {"status": "EXTERNAL_DECLARATIONS_CHECKED_NATIVE_OWNER_UNPROVED",
            "challenge": challenge, "observation_event": observation_event,
            "route": issued["route"], "declared_route_fingerprint": issued["route_fingerprint"],
            "declared_witness_sha256": issued["witness_sha256"],
            "scopes": summaries, "external_bytes_match_signed_observation": True,
            "declared_f3_edges_match_claimed_laws": True,
            "live_local_owner_verified": False, "in_process_owner_pins_verified": False,
            "native_cp30_route_certificate_verified": False,
            "fresh_native_two_pass_route_audit": False,
            "exact_task_authorized": False, "native_handoff_admitted": False,
            "read_only": True,
            "limitations": [
                "Finite source declarations are signed/observed claims, not owner-verified CP30 objects.",
                "The three files do not establish CP30 route joins, admitted transitions or rooted paths.",
                "CP30 native owner pins require live local bindings to exact source snapshot objects.",
                "No new mathematical observations, native owner pins, tasks or jobs were admitted.",
            ]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only external finite-source declaration check")
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--challenge", required=True)
    parser.add_argument("--observation-event", required=True)
    for scope in SCOPES:
        parser.add_argument(f"--{scope}-file", type=Path, required=True)
    options = parser.parse_args(argv)
    row = map_observed_sources(data_dir=options.data_dir, challenge=options.challenge,
            observation_event=options.observation_event,
            source_files={scope:getattr(options, f"{scope}_file") for scope in SCOPES})
    print(json.dumps(row, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
