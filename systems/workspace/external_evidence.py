"""Local external-source enrollment and challenge-bound signed CLAIM intake.

Keys are deliberately pinned by an authorized local operator. Verifying these
signatures does not authenticate a person, contact a live external service,
verify observation truth, or run CP30's owner-backed route audit. There is no
network fetch, hidden scheduler, private key management or HTTP write route.
"""
from __future__ import annotations

import argparse
import base64
import binascii
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import secrets
from urllib.parse import urlsplit

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

SCOPES = ("donor", "middle", "final")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
HEX48 = re.compile(r"[0-9a-f]{48}\Z")
IDENT = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}\Z")
CLAIM_KIND = "external-source-observation/v1"
BUNDLE_KIND = "external-source-bundle/v1"
_EVENTS = {"KEY_ENROLLED", "KEY_REVOKED", "CHALLENGE_ISSUED", "EVIDENCE_ACCEPTED", "SOURCE_OBSERVED"}


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("utf-8")


def _utc() -> datetime:
    return datetime.now(timezone.utc)


def _parse_time(value: str) -> datetime:
    if type(value) is not str:
        raise ValueError("timestamp must be ISO8601 text")
    value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if value.tzinfo is None:
        raise ValueError("timestamp must have a timezone")
    return value.astimezone(timezone.utc)


def _b64(value: str, count: int) -> bytes:
    if type(value) is not str or len(value) > 128:
        raise ValueError("invalid key/signature encoding")
    try:
        raw = base64.b64decode(value, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise ValueError("invalid base64") from exc
    if len(raw) != count or base64.b64encode(raw).decode("ascii") != value:
        raise ValueError("noncanonical key/signature encoding")
    return raw


def _id(value: str) -> str:
    if type(value) is not str or not IDENT.fullmatch(value):
        raise ValueError("invalid source/operator identifier")
    return value


def _sha(value: str) -> str:
    if type(value) is not str or not HEX64.fullmatch(value):
        raise ValueError("expected exact lowercase sha256")
    return value


def _locator(value: str) -> str:
    # This is metadata only; NEVER fetched or resolved by this package.
    if type(value) is not str or len(value) > 512:
        raise ValueError("invalid external source locator")
    u = urlsplit(value)
    if u.scheme != "https" or not u.hostname or u.username or u.password or u.fragment:
        raise ValueError("source locator must be a literal HTTPS URL without credentials or fragment")
    if u.query or any(c.isspace() for c in value):
        raise ValueError("source locator must not include query parameters or spaces")
    return value


def _request(request: dict) -> dict:
    if type(request) is not dict or set(request) != {"route", "route_fingerprint", "witness_sha256", "source_digests"}:
        raise ValueError("required: route, route_fingerprint, witness_sha256, source_digests")
    if request["route"] not in ("left", "right"):
        raise ValueError("unrecognized route")
    _sha(request["route_fingerprint"])
    _sha(request["witness_sha256"])
    if type(request["source_digests"]) is not dict or set(request["source_digests"]) != set(SCOPES):
        raise ValueError("three exact source digests required")
    for digest in request["source_digests"].values():
        _sha(digest)
    return request


class SourceEvidenceLedger:
    """Append-only local single-writer log; verification follows explicit enrollment.

    A hash chain detects accidental edits and interior truncation but is NOT
    independently anchored and cannot protect against a malicious local writer.
    Multi-process writes require a separately supplied lock / transaction layer.
    """

    def __init__(self, data_dir: str | Path):
        self.path = Path(data_dir).resolve() / "external_evidence.jsonl"

    def history(self) -> list[dict]:
        if not self.path.exists():
            return []
        if self.path.is_symlink() or not self.path.is_file() or self.path.stat().st_size > 5_000_000:
            raise ValueError("unsafe or oversized external-evidence journal")
        previous, rows = None, []
        for n, raw in enumerate(self.path.read_text(encoding="utf-8").splitlines(), 1):
            try:
                event = json.loads(raw)
            except ValueError as exc:
                raise ValueError("corrupt signed-evidence journal") from exc
            if (type(event) is not dict or set(event) != {"seq", "previous_hash", "kind", "record", "event_hash"} or
                type(event["seq"]) is not int or event["seq"] != n or
                event["previous_hash"] != previous or event["kind"] not in _EVENTS or
                type(event["record"]) is not dict or
                event["event_hash"] != sha256(_canonical({k: v for k,v in event.items() if k != "event_hash"})).hexdigest()):
                raise ValueError("signed-evidence journal history invalid")
            rows.append(event)
            previous = event["event_hash"]
        return rows

    def _state(self):
        keys: dict[str, dict] = {}
        challenges: dict[str, dict] = {}
        accepted: set[str] = set()
        observations: set[str] = set()
        rows = self.history()
        for event in rows:
            kind, record = event["kind"], event["record"]
            if kind == "KEY_ENROLLED":
                if record.get("scope") not in SCOPES or record["scope"] in keys:
                    raise ValueError("overlapping active source enrollments")
                keys[record["scope"]] = record
            elif kind == "KEY_REVOKED":
                if keys.get(record.get("scope"), {}).get("key_sha256") != record.get("key_sha256"):
                    raise ValueError("invalid source revocation history")
                del keys[record["scope"]]
            elif kind == "CHALLENGE_ISSUED":
                if record.get("challenge") in challenges:
                    raise ValueError("reused challenge in journal")
                challenges[record["challenge"]] = record
            elif kind == "EVIDENCE_ACCEPTED":
                if record.get("challenge") in accepted or record.get("challenge") not in challenges:
                    raise ValueError("duplicated or unissued receipt")
                accepted.add(record["challenge"])
            elif kind == "SOURCE_OBSERVED":
                challenge = record.get("challenge")
                if (challenge not in accepted or challenge in observations or
                        record.get("observer") != "github-public-branch-contents-v1" or
                        record.get("cp30_route_audited") is not False or
                        record.get("exact_task_authorized") is not False or
                        record.get("real_world_owners_authenticated") is not False or
                        type(record.get("observations")) is not dict or
                        set(record["observations"]) != set(SCOPES) or
                        any(type(record["observations"][scope]) is not dict
                            for scope in SCOPES) or
                        any(record["observations"][scope].get("sha256") !=
                            challenges[challenge]["source_digests"][scope]
                            for scope in SCOPES)):
                    raise ValueError("invalid or duplicate external observation in journal")
                observations.add(challenge)
        return keys, challenges, accepted, rows

    def _append(self, kind: str, record: dict) -> dict:
        _, _, _, events = self._state()
        entry = {"seq": len(events) + 1,
                 "previous_hash": events[-1]["event_hash"] if events else None,
                 "kind": kind, "record": record}
        entry["event_hash"] = sha256(_canonical(entry)).hexdigest()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.is_symlink():
            raise ValueError("unsafe external-evidence journal")
        with self.path.open("a", encoding="utf-8") as f:
            f.write(_canonical(entry).decode("ascii") + "\n")
            f.flush(); os.fsync(f.fileno())
        return entry

    def enroll(self, *, scope: str, source_id: str, public_key: str,
               locator: str, operator: str, confirm_key_sha256: str) -> dict:
        if scope not in SCOPES:
            raise ValueError("unknown source scope")
        _id(source_id); _id(operator); _locator(locator)
        digest = sha256(_b64(public_key, 32)).hexdigest()
        if confirm_key_sha256 != digest:
            raise PermissionError("full public-key fingerprint confirmation required")
        keys, _, _, _ = self._state()
        if scope in keys:
            raise ValueError("revoke existing scope before explicit key rotation")
        row = {"scope": scope, "source_id": source_id, "public_key": public_key,
               "key_sha256": digest, "locator": locator, "operator": operator,
               "enrolled_at": _utc().isoformat()}
        return self._append("KEY_ENROLLED", row)["record"]

    def revoke(self, *, scope: str, confirm_key_sha256: str, operator: str) -> dict:
        _id(operator)
        keys, _, _, _ = self._state()
        if scope not in keys or keys[scope]["key_sha256"] != confirm_key_sha256:
            raise ValueError("exact active source key required for revocation")
        row = {"scope": scope, "key_sha256": confirm_key_sha256,
               "operator": operator, "revoked_at": _utc().isoformat()}
        return self._append("KEY_REVOKED", row)["record"]

    def issue(self, request: dict, *, ttl_seconds: int = 300) -> dict:
        _request(request)
        if type(ttl_seconds) is not int or not 30 <= ttl_seconds <= 600:
            raise ValueError("challenge lifetime must be 30..600 seconds")
        keys, _, _, _ = self._state()
        if set(keys) != set(SCOPES):
            raise ValueError("three explicitly enrolled active keys required")
        row = {"challenge": secrets.token_hex(24), "issued_at": _utc().isoformat(),
               "ttl_seconds": ttl_seconds, **request,
               "pinned_keys": {s: {"source_id":keys[s]["source_id"],
                                   "key_sha256":keys[s]["key_sha256"]} for s in SCOPES}}
        return self._append("CHALLENGE_ISSUED", row)["record"]

    def accept(self, *, challenge: str, bundle: dict, confirm_challenge: str) -> dict:
        if type(challenge) is not str or not HEX48.fullmatch(challenge) or confirm_challenge != challenge:
            raise PermissionError("exact issued challenge confirmation required")
        keys, challenges, accepted, _ = self._state()
        if challenge not in challenges:
            raise ValueError("unknown challenge")
        if challenge in accepted:
            raise ValueError("challenge already consumed")
        issued = challenges[challenge]
        now = _utc()
        start = _parse_time(issued["issued_at"])
        if now > start + timedelta(seconds=issued["ttl_seconds"]) or now < start:
            raise ValueError("expired or invalid receiver challenge")
        if type(bundle) is not dict or set(bundle) != {"kind", "attestations"} or bundle["kind"] != BUNDLE_KIND:
            raise ValueError("unsupported external observation bundle")
        attestations = bundle["attestations"]
        if type(attestations) is not list or len(attestations) != 3 or len(_canonical(bundle)) > 16000:
            raise ValueError("exact three bounded signed statements required")
        for index, scope in enumerate(SCOPES):
            pinned = issued["pinned_keys"][scope]
            enrolled = keys.get(scope)
            if not enrolled or (enrolled["key_sha256"], enrolled["source_id"]) != (pinned["key_sha256"], pinned["source_id"]):
                raise ValueError("source key was revoked or rotated since challenge")
            item = attestations[index]
            if type(item) is not dict or set(item) != {"claim", "signature"} or type(item["claim"]) is not dict:
                raise ValueError("malformed source attestation")
            claim = item["claim"]
            if set(claim) != {"kind", "scope", "source_id", "challenge", "route", "route_fingerprint",
                              "witness_sha256", "source_sha256", "observed_at"}:
                raise ValueError("source claim fields invalid")
            expected = {"kind":CLAIM_KIND, "scope":scope,"source_id":pinned["source_id"],
                        "challenge":challenge, "route":issued["route"],
                        "route_fingerprint":issued["route_fingerprint"],
                        "witness_sha256":issued["witness_sha256"],
                        "source_sha256":issued["source_digests"][scope]}
            if any(claim.get(k) != v for k,v in expected.items()):
                raise ValueError("source attestation does not match receiver declaration")
            claimed_at = _parse_time(claim["observed_at"])
            if claimed_at < start - timedelta(seconds=30) or claimed_at > now + timedelta(seconds=30):
                raise ValueError("claimed observation time outside receiver challenge window")
            try:
                Ed25519PublicKey.from_public_bytes(_b64(enrolled["public_key"], 32)).verify(
                    _b64(item["signature"], 64), _canonical(claim))
            except (InvalidSignature, ValueError, TypeError) as exc:
                raise ValueError("source signature unproved") from exc
        entry = self._append("EVIDENCE_ACCEPTED", {"challenge": challenge,
                    "bundle_sha256":sha256(_canonical(bundle)).hexdigest(),
                    "accepted_at":now.isoformat(), "pinned_keys":issued["pinned_keys"]})
        return {"status":"SIGNED_SOURCE_CLAIMS_ACCEPTED",
                "challenge":challenge,"receipt_hash":entry["event_hash"],
                "bundle_sha256":entry["record"]["bundle_sha256"],
                "verified_scopes":list(SCOPES),
                "external_content_observed_by_receiver":False,
                "real_world_owners_authenticated":False,
                "cp30_route_audited":False}

    def status(self) -> dict:
        keys, challenges, accepted, rows = self._state()
        observations = sum(e["kind"] == "SOURCE_OBSERVED" for e in rows)
        return {"scope_enrollments":{s: {"source_id":row["source_id"],
                    "key_sha256":row["key_sha256"], "locator":row["locator"]}
                    for s,row in sorted(keys.items())},
                "issued_challenges":len(challenges),"accepted_receipts":len(accepted),
                "source_observations": observations,
                "events":len(rows),"read_only":True,
                "external_content_observed":observations > 0,"cp30_route_audited":False}


def _read_json(path: str | Path, *, limit: int = 20000) -> dict:
    source = Path(path)
    if not source.is_file() or source.stat().st_size > limit:
        raise ValueError("JSON input missing or oversized")
    payload = json.loads(source.read_text(encoding="utf-8"))
    if type(payload) is not dict:
        raise ValueError("JSON input must be an object")
    return payload


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Local, explicit external source signature admission")
    ap.add_argument("--data-dir", type=Path, required=True)
    commands = ap.add_subparsers(dest="operation", required=True)
    p = commands.add_parser("status", help="Read-only enrollment and receipt status")
    p = commands.add_parser("enroll", help="Pin operator-selected external public key")
    p.add_argument("--scope", choices=SCOPES, required=True)
    p.add_argument("--source-id", required=True); p.add_argument("--locator", required=True)
    p.add_argument("--public-key-file", required=True, type=Path)
    p.add_argument("--confirm-key-sha256", required=True); p.add_argument("--operator", required=True)
    p = commands.add_parser("revoke", help="Revoke one exact enrolled key")
    p.add_argument("--scope", choices=SCOPES, required=True)
    p.add_argument("--confirm-key-sha256", required=True); p.add_argument("--operator", required=True)
    p = commands.add_parser("challenge", help="Issue fresh receiver challenge from exact declared digests")
    p.add_argument("--request-json", required=True, type=Path)
    p = commands.add_parser("accept", help="Accept signed source claims only")
    p.add_argument("--challenge", required=True); p.add_argument("--confirm-challenge", required=True)
    p.add_argument("--bundle-json", required=True, type=Path)
    args = ap.parse_args(argv)
    store = SourceEvidenceLedger(args.data_dir)
    if args.operation == "status": out = store.status()
    elif args.operation == "enroll":
        file = args.public_key_file
        if not file.is_file() or file.stat().st_size > 128:
            raise ValueError("invalid public-key file")
        out = store.enroll(scope=args.scope, source_id=args.source_id,
                public_key=file.read_text(encoding="ascii").strip(),
                locator=args.locator, operator=args.operator,
                confirm_key_sha256=args.confirm_key_sha256)
    elif args.operation == "revoke":
        out = store.revoke(scope=args.scope, confirm_key_sha256=args.confirm_key_sha256,
                           operator=args.operator)
    elif args.operation == "challenge": out = store.issue(_read_json(args.request_json))
    else:
        out = store.accept(challenge=args.challenge, confirm_challenge=args.confirm_challenge,
                           bundle=_read_json(args.bundle_json))
    print(json.dumps(out, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
