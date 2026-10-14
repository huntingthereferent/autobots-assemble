"""Trust-anchor-relative authority delegation over EXACT matched CP30 snapshots.

This is a read-only, source-owned, in-process corroboration contract, NOT proof
of a natural person's identity, legal ownership, independent transition audit,
CP29/CP30 receipt validation, or task admission. The authority public key must
be authenticated *outside* this module. This code never issues trust anchors,
produces private keys, or constructs CP30 owner pins from public declarations.
"""
from __future__ import annotations

import base64
import binascii
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
from typing import Any, Callable, Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .external_evidence import SCOPES, SourceEvidenceLedger, _canonical
from .external_route_mapping import map_observed_sources, _parse_time, _strict_object
from .external_native_binding import bind_external_observation_to_native
from .native_owner_observation import _native, _snapshot

KIND = "cp30-external-native-authority-binding/v1"
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}\Z")
_HEX64 = re.compile(r"[a-f0-9]{64}\Z")
_MAX_SECONDS = 300
_FIELDS = {"kind", "authority_id", "authority_key_sha256", "challenge",
           "observation_event", "route", "route_fingerprint", "witness_sha256",
           "native_evidence_sha256", "native_process_identity_sha256", "scopes", "issued_at", "expires_at",
           "authority_scope"}


def _id(value: Any) -> str:
    if type(value) is not str or not _ID.fullmatch(value):
        raise ValueError("invalid authority identifier")
    return value


def _key(public_key: str) -> bytes:
    if type(public_key) is not str or len(public_key) > 128:
        raise ValueError("authority anchor must be an Ed25519 public key")
    try:
        raw = base64.b64decode(public_key, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("invalid Ed25519 authority anchor") from exc
    if len(raw) != 32 or base64.b64encode(raw).decode("ascii") != public_key:
        raise ValueError("authority public key must be canonical Ed25519")
    return raw


def _signature(raw: Any) -> bytes:
    if type(raw) is not str or len(raw) > 128:
        raise ValueError("invalid authority signature")
    try:
        decoded = base64.b64decode(raw, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("invalid authority signature encoding") from exc
    if len(decoded) != 64 or base64.b64encode(decoded).decode("ascii") != raw:
        raise ValueError("invalid authority signature size")
    return decoded


class AuthorityAnchorLedger:
    """Explicit receiver/operator-pinned root keys, separate from source signers.

    A local hash-chained file is NOT a globally trusted identity source or
    tamper-proof storage. The human/organization must verify the reference
    outside this application and protect the journal against local writers.
    """

    def __init__(self, data_dir: str | Path):
        self.path = Path(data_dir).resolve() / "cp30_authority_anchors.jsonl"

    def history(self) -> list[dict]:
        if not self.path.exists():
            return []
        if self.path.is_symlink() or not self.path.is_file() or self.path.stat().st_size > 250_000:
            raise ValueError("unsafe or oversized authority anchor journal")
        records, last, active = [], None, {}
        for index, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), 1):
            try:
                row = json.loads(line, object_pairs_hook=_strict_object)
            except ValueError as exc:
                raise ValueError("invalid authority anchor journal JSON") from exc
            if (type(row) is not dict or set(row) != {"sequence", "previous_hash", "kind", "record", "event_hash"}
                    or type(row["sequence"]) is not int or row["sequence"] != index
                    or row["previous_hash"] != last
                    or row["kind"] not in ("AUTHORITY_PINNED", "AUTHORITY_REVOKED")
                    or type(row["record"]) is not dict or
                    row["event_hash"] != sha256(_canonical({k: v for k, v in row.items()
                                                          if k != "event_hash"})).hexdigest()):
                raise ValueError("invalid authority anchor journal history")
            rec = row["record"]
            if row["kind"] == "AUTHORITY_PINNED":
                if set(rec) != {"authority_id", "public_key", "fingerprint", "operator", "verification_reference", "pinned_at"}:
                    raise ValueError("invalid authority pin record")
                _id(rec["authority_id"]); _id(rec["operator"])
                key = _key(rec["public_key"])
                if rec["fingerprint"] != sha256(key).hexdigest() or rec["authority_id"] in active:
                    raise ValueError("overlapping or malformed authority anchor pin")
                if not isinstance(rec["verification_reference"], str) or not 1 <= len(rec["verification_reference"]) <= 200:
                    raise ValueError("missing out-of-band verification reference")
                _parse_time(rec["pinned_at"])
                active[rec["authority_id"]] = rec
            else:
                if set(rec) != {"authority_id", "fingerprint", "operator", "revoked_at"}:
                    raise ValueError("invalid authority revocation record")
                _id(rec["authority_id"]); _id(rec["operator"])
                _parse_time(rec["revoked_at"])
                if (rec["authority_id"] not in active or
                        active[rec["authority_id"]]["fingerprint"] != rec["fingerprint"]):
                    raise ValueError("authority revocation has no exact active anchor")
                del active[rec["authority_id"]]
            records.append(row)
            last = row["event_hash"]
        return records

    def current(self) -> dict[str, dict]:
        active = {}
        for event in self.history():
            rec = event["record"]
            if event["kind"] == "AUTHORITY_PINNED":
                active[rec["authority_id"]] = rec
            else:
                active.pop(rec["authority_id"])
        return active

    def _append(self, kind: str, record: dict) -> dict:
        rows = self.history()
        entry = {"sequence": len(rows) + 1,
                 "previous_hash": rows[-1]["event_hash"] if rows else None,
                 "kind": kind, "record": record}
        entry["event_hash"] = sha256(_canonical(entry)).hexdigest()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.is_symlink():
            raise ValueError("unsafe authority journal symlink")
        with self.path.open("a", encoding="utf-8") as sink:
            sink.write(_canonical(entry).decode("ascii") + "\n")
            sink.flush()
            os.fsync(sink.fileno())
        return entry

    def pin(self, *, authority_id: str, public_key: str, confirm_fingerprint: str,
            operator: str, verification_reference: str) -> dict:
        _id(authority_id); _id(operator)
        raw = _key(public_key)
        fingerprint = sha256(raw).hexdigest()
        if fingerprint != confirm_fingerprint:
            raise PermissionError("exact independently checked root fingerprint required")
        if type(verification_reference) is not str or not 1 <= len(verification_reference) <= 200:
            raise ValueError("out-of-band verification reference required")
        if authority_id in self.current():
            raise ValueError("authority anchor already pinned; explicit revocation required")
        rec = {"authority_id": authority_id, "public_key": public_key,
               "fingerprint": fingerprint, "operator": operator,
               "verification_reference": verification_reference,
               "pinned_at": datetime.now(timezone.utc).isoformat()}
        return self._append("AUTHORITY_PINNED", rec)["record"]

    def revoke(self, *, authority_id: str, confirm_fingerprint: str, operator: str) -> dict:
        _id(authority_id); _id(operator)
        pinned = self.current().get(authority_id)
        if pinned is None or pinned["fingerprint"] != confirm_fingerprint:
            raise ValueError("exact active authority anchor required")
        rec = {"authority_id": authority_id, "fingerprint": confirm_fingerprint,
               "operator": operator, "revoked_at": datetime.now(timezone.utc).isoformat()}
        return self._append("AUTHORITY_REVOKED", rec)["record"]

    def require_current(self, authority_id: str, public_key: str, fingerprint: str) -> None:
        pinned = self.current().get(authority_id)
        if (pinned is None or pinned["fingerprint"] != fingerprint or
                pinned["public_key"] != public_key):
            raise PermissionError("no current operator-pinned authority root for supplied key")


def _snapshot_scope(tasks: Mapping[str, Any]) -> dict:
    first = next(iter(tasks.values()))
    chain = first._route
    pins = (chain.first.donor, chain.first.recipient, chain.final)
    scopes = {}
    for scope, pair in zip(SCOPES, pins):
        sides = {}
        for side in ("old", "new"):
            snapshot = getattr(pair, side).snapshot
            digest = snapshot.digest
            if type(digest) is not str or not _HEX64.fullmatch(digest):
                raise ValueError("native source snapshot has invalid content digest")
            sides[side] = {"source_label": snapshot.claimed_source,
                           "revision": snapshot.revision,
                           "snapshot_digest": digest}
        scopes[scope] = sides
    return scopes


def _current_material(*, data_dir: str | Path, challenge: str,
                      observation_event: str, source_files: dict[str, str | Path],
                      native_source_root: str | Path,
                      source_capture: Callable[[], Mapping[str, Any]]) -> dict:
    """No writes, network, owner-pin issuance or newly observed transitions."""
    store = SourceEvidenceLedger(data_dir)
    history_before = store.history()
    tip_before = history_before[-1]["event_hash"] if history_before else None
    mapped = map_observed_sources(data_dir=data_dir, challenge=challenge,
                                  observation_event=observation_event,
                                  source_files=source_files)
    native = _native(native_source_root)
    first_tasks = source_capture()
    first, handles = _snapshot(first_tasks, native)
    scopes = _snapshot_scope(first_tasks)
    # Nontransferable process-local identity: signed only for this running
    # native object graph. It is neither a source-content digest nor an owner ID.
    process_identity = sha256(_canonical({
        "process_pid": os.getpid(),
        "task_handles": [[name, id(task)] for name, task in sorted(first_tasks.items())],
        "native_object_handles": list(handles[1]),
    })).hexdigest()
    comparison = bind_external_observation_to_native(
        data_dir=data_dir, challenge=challenge, observation_event=observation_event,
        source_files=source_files, native_source_root=native_source_root,
        source_capture=source_capture)
    second_tasks = source_capture()
    second, other_handles = _snapshot(second_tasks, native)
    if (first != second or handles != other_handles or
            _snapshot_scope(second_tasks) != scopes):
        raise ValueError("native source identities changed during authority binding")
    if (comparison["native_route_fingerprint"] != first["route_fingerprint"] or
            comparison["route"] != first["route"] or
            comparison["matched_native_sides"] != 6):
        raise ValueError("no exact external-to-native evidence correspondence")
    active, challenges, accepted, events = store._state()
    if (events[-1]["event_hash"] if events else None) != tip_before:
        raise ValueError("evidence journal changed during authority binding")
    if challenge not in accepted or challenge not in challenges:
        raise ValueError("source evidence challenge no longer accepted")
    pinned = challenges[challenge]["pinned_keys"]
    result_scopes = {}
    for scope in SCOPES:
        enrollment = active.get(scope)
        if (enrollment is None or enrollment["key_sha256"] != pinned[scope]["key_sha256"]
                or enrollment["source_id"] != pinned[scope]["source_id"]):
            raise ValueError("source key no longer enrolled for declared scope")
        result_scopes[scope] = {
            "source_id": enrollment["source_id"],
            "source_key_sha256": enrollment["key_sha256"],
            "observed_file_sha256": mapped["scopes"][scope]["source_sha256"],
            "native_sides": scopes[scope],
        }
    # The journal must not change between the content check and the authority
    # material snapshot. The previous binder also checks its own journal tip.
    # Under arbitrary concurrent writers, caller still needs transaction locking.
    checked = [e for e in events if e["kind"] == "SOURCE_OBSERVED" and
               e["record"].get("challenge") == challenge]
    if len(checked) != 1 or checked[0]["event_hash"] != observation_event:
        raise ValueError("external observation changed during authority binding")
    return {
        "challenge": challenge,
        "observation_event": observation_event,
        "route": first["route"],
        "route_fingerprint": first["route_fingerprint"],
        "witness_sha256": mapped["declared_witness_sha256"],
        "native_evidence_sha256": first["local_evidence_sha256"],
        "native_process_identity_sha256": process_identity,
        "scopes": result_scopes,
    }


def prepare_authority_binding(*, data_dir: str | Path, challenge: str,
                              observation_event: str, source_files: dict[str, str | Path],
                              native_source_root: str | Path,
                              source_capture: Callable[[], Mapping[str, Any]],
                              authority_id: str, authority_public_key: str,
                              anchor_fingerprint: str, ttl_seconds: int = 180) -> dict:
    """Construct an *unsigned* exact, short-lived request for external review.

    Source owners must arrange signing out-of-process; preparing proves neither
    trust-anchor validity nor signing authority. Never exports private keys.
    """
    _id(authority_id)
    raw = _key(authority_public_key)
    fp = sha256(raw).hexdigest()
    if type(anchor_fingerprint) is not str or anchor_fingerprint != fp:
        raise PermissionError("independently confirmed authority anchor fingerprint required")
    AuthorityAnchorLedger(data_dir).require_current(authority_id, authority_public_key, fp)
    if type(ttl_seconds) is not int or not 30 <= ttl_seconds <= _MAX_SECONDS:
        raise ValueError("authority grants must last 30..300 seconds")
    material = _current_material(data_dir=data_dir, challenge=challenge,
                     observation_event=observation_event, source_files=source_files,
                     native_source_root=native_source_root, source_capture=source_capture)
    if fp in {material["scopes"][s]["source_key_sha256"] for s in SCOPES}:
        raise ValueError("authority anchor must differ from every source signer key")
    now = datetime.now(timezone.utc)
    return {"kind": KIND, "authority_id": authority_id,
            "authority_key_sha256": fp, **material,
            "authority_scope": "key-holder delegation for these six native snapshot digests only",
            "issued_at": now.isoformat(),
            "expires_at": (now + timedelta(seconds=ttl_seconds)).isoformat()}


def verify_authority_binding(*, data_dir: str | Path, challenge: str,
                             observation_event: str, source_files: dict[str, str | Path],
                             native_source_root: str | Path,
                             source_capture: Callable[[], Mapping[str, Any]],
                             authority_id: str, authority_public_key: str,
                             anchor_fingerprint: str, signed_grant: dict) -> dict:
    """Replay current native/external checks, verify separately supplied anchor.

    Positive status verifies a delegation FROM the independently chosen trust
    anchor, not legal/real-world ownership. No task execution or admission.
    """
    _id(authority_id)
    raw = _key(authority_public_key)
    fp = sha256(raw).hexdigest()
    if type(anchor_fingerprint) is not str or anchor_fingerprint != fp:
        raise PermissionError("trusted authority key fingerprint not confirmed")
    AuthorityAnchorLedger(data_dir).require_current(authority_id, authority_public_key, fp)
    if type(signed_grant) is not dict or set(signed_grant) != {"statement", "signature"}:
        raise ValueError("signed grant must include exact statement and signature")
    statement = signed_grant["statement"]
    if type(statement) is not dict or set(statement) != _FIELDS or statement["kind"] != KIND:
        raise ValueError("authority binding statement has invalid fields")
    if statement["authority_id"] != authority_id or statement["authority_key_sha256"] != fp:
        raise ValueError("authority ID/key mismatch")
    if statement["authority_scope"] != "key-holder delegation for these six native snapshot digests only":
        raise ValueError("authority grant has unsupported scope")
    if len(_canonical(statement)) > 12000:
        raise ValueError("oversized authority delegation")
    issued = _parse_time(statement["issued_at"])
    expires = _parse_time(statement["expires_at"])
    now = datetime.now(timezone.utc)
    if (issued > now + timedelta(seconds=30) or now < issued - timedelta(seconds=30) or
            expires <= now or not timedelta(seconds=30) <= expires - issued <= timedelta(seconds=_MAX_SECONDS)):
        raise ValueError("stale, future or invalid authority delegation lifetime")
    signature = _signature(signed_grant["signature"])
    try:
        Ed25519PublicKey.from_public_bytes(raw).verify(signature, _canonical(statement))
    except InvalidSignature as exc:
        raise ValueError("authority delegation signature unproved") from exc
    # Signature verification is not enough: compare every scope with *current*
    # previously signed/observed GitHub bytes and current live native objects.
    anchors_before = AuthorityAnchorLedger(data_dir).history()
    current = _current_material(data_dir=data_dir, challenge=challenge,
                         observation_event=observation_event, source_files=source_files,
                         native_source_root=native_source_root, source_capture=source_capture)
    if any(statement.get(k) != v for k, v in current.items()):
        raise ValueError("authority delegation differs from current signed/native evidence")
    anchors_after = AuthorityAnchorLedger(data_dir).history()
    if anchors_before != anchors_after:
        raise ValueError("authority anchor journal changed during verification")
    AuthorityAnchorLedger(data_dir).require_current(authority_id, authority_public_key, fp)
    if fp in {current["scopes"][s]["source_key_sha256"] for s in SCOPES}:
        raise ValueError("authority and source signers must have distinct keys")
    return {"status": "OPERATOR_ANCHORED_SNAPSHOT_DELEGATION_VERIFIED",
            "authority_id": authority_id, "authority_key_sha256": fp,
            "challenge": challenge, "observation_event": observation_event,
            "route": current["route"],
            "route_fingerprint": current["route_fingerprint"],
            "native_evidence_sha256": current["native_evidence_sha256"],
            "verified_source_scopes": list(SCOPES),
            "verified_native_snapshot_sides": 6,
            "same_native_process_objects_verified": True,
            "authority_signature_verified": True,
            "source_signed_public_bytes_correlated": True,
            "native_cached_transitions_matched": True,
            "authority_relative_to_pinned_key_only": True,
            "separately_pinned_operator_policy_required": True,
            "nontransferable_process_local_identity": True,
            "out_of_band_trust_anchor_authenticated_by_module": False,
            "real_world_external_owner_authenticated": False,
            "legal_ownership_proved": False,
            "cp30_independent_process_attestation_verified": False,
            "fresh_native_route_audit": False,
            "cp29_receipt_revalidated": False,
            "exact_task_authorized": False,
            "native_handoff_admitted": False,
            "new_transitions_observed": False,
            "journal_modified": False,
            "note": "An independently pinned authority key signed this six-snapshot claim; source signs matching observed content, but offline authority, legal ownership and CP30 tasks remain distinct."}
