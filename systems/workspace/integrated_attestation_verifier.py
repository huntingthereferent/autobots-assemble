"""Host-owned CP30 signature verdict replay, independent of selected worker code.

This authenticates signatures ONLY against public keys supplied with the task;
it does not authenticate human owners, route audits, physical observations, or
trust-root enrollment. No historical CP code is imported by this verifier.
"""
from __future__ import annotations

import base64
import binascii
import json
import re
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

SCOPES = ("donor", "middle", "final")
CLAIM_KIND = "selected-route-source-attestation/v1"
BUNDLE_KIND = "selected-route-source-bundle/v1"
_HEX48 = re.compile(r"[0-9a-f]{48}\Z")
_HEX64 = re.compile(r"[0-9a-f]{64}\Z")
_FIELDS = {"bundle", "trust", "expect"}
_EXPECT = {"challenge", "route", "fingerprint", "witness", "source_digests"}
_CLAIM = {"kind", "scope", "challenge", "route", "route_fingerprint", "witness_sha256", "source_sha256"}


def _b64(s: Any, size: int) -> bytes:
    if type(s) is not str or len(s) > 128:
        raise ValueError("invalid public key or signature encoding")
    try:
        data = base64.b64decode(s, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise ValueError("invalid base64") from exc
    if len(data) != size or base64.b64encode(data).decode("ascii") != s:
        raise ValueError("noncanonical public key or signature")
    return data


def validate_request(value: Any) -> dict:
    """Bound inputs before native admission; never accept signer private keys."""
    if type(value) is not dict or set(value) != _FIELDS:
        raise ValueError("CP30 verifier accepts only bundle, trust, expect")
    # Historical CLI has a 20,000 character request limit; enforce it in host.
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    if len(raw) > 18000:
        raise ValueError("CP30 verifier request exceeds 18,000 characters")
    e, t, b = value["expect"], value["trust"], value["bundle"]
    if type(e) is not dict or set(e) != _EXPECT:
        raise ValueError("invalid CP30 expected route scope")
    if (type(e["challenge"]) is not str or not _HEX48.fullmatch(e["challenge"]) or
            e["route"] not in ("left", "right") or type(e["fingerprint"]) is not str or
            not _HEX64.fullmatch(e["fingerprint"]) or type(e["witness"]) is not str or
            not _HEX64.fullmatch(e["witness"])):
        raise ValueError("invalid challenge, route or 64-char digest")
    digests = e["source_digests"]
    if type(digests) is not dict or set(digests) != set(SCOPES) or any(
            type(x) is not str or not _HEX64.fullmatch(x) for x in digests.values()):
        raise ValueError("expected donor/middle/final SHA-256 digests")
    if type(t) is not dict or set(t) != set(SCOPES):
        raise ValueError("three preselected public key anchors required")
    for key in t.values():
        _b64(key, 32)
    if type(b) is not dict or set(b) != {"kind", "attestations"} or b["kind"] != BUNDLE_KIND:
        raise ValueError("invalid signed bundle container")
    if type(b["attestations"]) is not list or len(b["attestations"]) != 3:
        raise ValueError("exactly three signed scope records required")
    for row in b["attestations"]:
        if type(row) is not dict or set(row) != {"claim", "signature"} or type(row["claim"]) is not dict:
            raise ValueError("malformed attestation record")
        # Malformed or tampered claims are permitted as negative verification
        # inputs, but only small JSON objects are accepted by the host.
        if len(json.dumps(row["claim"], sort_keys=True)) > 1800:
            raise ValueError("oversized attestation claim")
        if type(row["signature"]) is not str or len(row["signature"]) > 128:
            raise ValueError("invalid signature field")
    return json.loads(raw)


def native_verdict(value: dict) -> tuple[str, list[str]]:
    """Independently verify exact claims and signatures against passed trust."""
    e, bundle, trust = value["expect"], value["bundle"], value["trust"]
    verified: list[str] = []
    for scope, row in zip(SCOPES, bundle["attestations"]):
        claim = row["claim"]
        expected = {
            "kind": CLAIM_KIND, "scope": scope, "challenge": e["challenge"],
            "route": e["route"], "route_fingerprint": e["fingerprint"],
            "witness_sha256": e["witness"], "source_sha256": e["source_digests"][scope],
        }
        if type(claim) is not dict or set(claim) != _CLAIM or claim != expected:
            return "ATTESTATION_CLAIM_MISMATCH", []
        message = json.dumps(claim, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                             allow_nan=False).encode("utf-8")
        try:
            signature = _b64(row["signature"], 64)
            public_key = Ed25519PublicKey.from_public_bytes(_b64(trust[scope], 32))
            public_key.verify(signature, message)
        except (ValueError, InvalidSignature, TypeError):
            return "ATTESTATION_SIGNATURE_UNPROVED", []
        verified.append(scope)
    return "ATTESTATIONS_VERIFIED", verified
