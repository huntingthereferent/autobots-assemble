"""CP-30 independent-process, challenge-bound Ed25519 scope attestations.

Verifier trusts ONLY caller-supplied, previously pinned public keys. The
attestation signer is a synthetic test owner, not a real-world identity oracle.
This module is intentionally independent of the owner-backed chatbot runtime.
Requires the `cryptography` Python package (Ed25519 support).
"""
from __future__ import annotations

import base64
import binascii
import json
import os
import sys
from dataclasses import dataclass
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

SCOPES = ('donor', 'middle', 'final')
CLAIM_KIND = 'selected-route-source-attestation/v1'
BUNDLE_KIND = 'selected-route-source-bundle/v1'
_HEX = frozenset('0123456789abcdef')


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode('utf-8')


def raw_b64(value: bytes) -> str:
    return base64.b64encode(value).decode('ascii')


def decode_b64(value: str, size: int) -> bytes:
    if type(value) is not str or len(value) > 128:
        raise ValueError('invalid encoded bytes')
    try:
        raw = base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError) as e:
        raise ValueError('invalid base64') from e
    if len(raw) != size or raw_b64(raw) != value:
        raise ValueError('noncanonical or invalid key/signature size')
    return raw


def is_hex(s: Any, count: int) -> bool:
    return type(s) is str and len(s) == count and set(s) <= _HEX


def generate_fixture_keys():
    """Ephemeral fixture secrets. Never export private keys in a receipt."""
    secret, trust = {}, {}
    for scope in SCOPES:
        key = Ed25519PrivateKey.generate()
        secret[scope] = raw_b64(key.private_bytes(
            encoding=serialization.Encoding.Raw, format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()))
        trust[scope] = raw_b64(key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw))
    return secret, trust


def make_claims(*, challenge, route, fingerprint, witness, source_digests):
    if (not is_hex(challenge, 48) or route not in ('left', 'right') or
        not is_hex(fingerprint, 64) or not is_hex(witness, 64) or
        type(source_digests) is not dict or set(source_digests) != set(SCOPES) or
        any(not is_hex(s, 64) for s in source_digests.values())):
        raise ValueError('invalid witnessed challenge or three source digests')
    return [dict(kind=CLAIM_KIND, scope=scope, challenge=challenge, route=route,
                 route_fingerprint=fingerprint, witness_sha256=witness,
                 source_sha256=source_digests[scope]) for scope in SCOPES]


def sign_scopes(claims, private_keys):
    if (type(claims) is not list or len(claims) != len(SCOPES) or
        type(private_keys) is not dict or set(private_keys) != set(SCOPES)):
        raise ValueError('exact three source signers required')
    # The fixture signer is authorized to attest to its supplied owner-state
    # claims. It must never treat arbitrary caller claims as real-world truth.
    if any(type(c) is not dict or c.get('scope') != SCOPES[i]
           or set(c) != {'kind','scope','challenge','route','route_fingerprint',
                         'witness_sha256','source_sha256'} or
           c.get('kind') != CLAIM_KIND for i, c in enumerate(claims)):
        raise ValueError('malformed signer claim')
    expected = make_claims(challenge=claims[0]['challenge'],
                           route=claims[0]['route'],fingerprint=claims[0]['route_fingerprint'],
                           witness=claims[0]['witness_sha256'],
                           source_digests={c['scope']:c['source_sha256'] for c in claims})
    if claims != expected:
        raise ValueError('inconsistent signed source claims')
    attestations = []
    for c in claims:
        private = Ed25519PrivateKey.from_private_bytes(decode_b64(private_keys[c['scope']], 32))
        attestations.append({'claim': c, 'signature': raw_b64(private.sign(canonical(c)))})
    return {'kind': BUNDLE_KIND, 'attestations': attestations}


@dataclass(frozen=True)
class AttestationVerdict:
    status: str
    verified_scopes: tuple[str, ...]

    @property
    def authenticated(self):
        return self.status == 'ATTESTATIONS_VERIFIED' and self.verified_scopes == SCOPES


def verify_scopes(bundle, trust, *, challenge, route, fingerprint, witness, source_digests):
    try:
        expected = make_claims(challenge=challenge, route=route,
                               fingerprint=fingerprint,witness=witness,
                               source_digests=source_digests)
    except (ValueError, TypeError):
        return AttestationVerdict('ATTESTATION_INVALID_EXPECTATION', ())
    if (type(trust) is not dict or set(trust) != set(SCOPES) or
        any(type(v) is not str for v in trust.values())):
        return AttestationVerdict('ATTESTATION_TRUST_MISSING', ())
    if (type(bundle) is not dict or set(bundle) != {'kind','attestations'} or
        bundle['kind'] != BUNDLE_KIND or type(bundle['attestations']) is not list or
        len(bundle['attestations']) != len(SCOPES)):
        return AttestationVerdict('ATTESTATION_MALFORMED', ())
    valid = []
    for i, att in enumerate(bundle['attestations']):
        if type(att) is not dict or set(att) != {'claim','signature'} or type(att['claim']) is not dict:
            return AttestationVerdict('ATTESTATION_MALFORMED', ())
        claim = att['claim']
        if claim != expected[i]:
            return AttestationVerdict('ATTESTATION_CLAIM_MISMATCH', ())
        try:
            key = Ed25519PublicKey.from_public_bytes(decode_b64(trust[SCOPES[i]], 32))
            key.verify(decode_b64(att['signature'], 64), canonical(claim))
        except (ValueError, InvalidSignature, TypeError):
            return AttestationVerdict('ATTESTATION_SIGNATURE_UNPROVED', ())
        valid.append(SCOPES[i])
    return AttestationVerdict('ATTESTATIONS_VERIFIED', tuple(valid))


def cli(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1 or args[0] not in ('sign','verify'):
        raise SystemExit('usage: finite_process_attestation.py sign|verify')
    try:
        wire = sys.stdin.read(20001)
        if len(wire) > 20000:
            raise ValueError('wire limit')
        request = json.loads(wire)
        if type(request) is not dict:
            raise ValueError('invalid request')
        if args[0] == 'sign':
            if set(request) != {'claims','private_keys'}:
                raise ValueError('invalid signer request')
            bundle=sign_scopes(request['claims'],request['private_keys'])
            result={'status':'ATTESTATIONS_SIGNED','pid':os.getpid(),'bundle':bundle}
        else:
            if set(request) != {'bundle','trust','expect'} or type(request['expect']) is not dict:
                raise ValueError('invalid verifier request')
            verdict=verify_scopes(request['bundle'],request['trust'],**request['expect'])
            result={'status':verdict.status,'pid':os.getpid(),
                    'verified_scopes':list(verdict.verified_scopes)}
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        result={'status':'ATTESTATION_INVALID_REQUEST','pid':os.getpid()}
    print(json.dumps(result, sort_keys=True, separators=(',', ':')))
    return 0


if __name__ == '__main__':
    raise SystemExit(cli())
