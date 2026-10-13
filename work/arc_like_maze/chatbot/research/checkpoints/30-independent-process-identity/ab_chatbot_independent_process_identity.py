"""CP-30 owner-scope signature check in a separate verifier process.

Prior to every task authorization, an independent verifier subprocess checks
three Ed25519 signatures against public keys already pinned by the receiver,
then CP-29 performs its mandatory fresh two-pass owner-backed route audit.
Synthetic fixture owner keys do NOT establish real-world source ownership.
"""
from __future__ import annotations

import json
import secrets
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from ab_chatbot_certificate_handoff import (_digest, _route_evidence, _unpack,
    _bound, issue_handoff, accept_handoff)
from finite_process_attestation import make_claims, is_hex, SCOPES

VERIFIER = Path(__file__).with_name('finite_process_attestation.py')


def new_challenge():
    return secrets.token_hex(24)


def _digests(t):
    values = _route_evidence(t._route)
    if len(values) != 3:
        raise ValueError('exact three source pairs required')
    return {s: _digest(values[i]) for i,s in enumerate(SCOPES)}


def _child(mode, request):
    raw = json.dumps(request, sort_keys=True, separators=(',', ':'),allow_nan=False)
    if len(raw) > 19000:
        raise ValueError('IPC message too large')
    done = subprocess.run([sys.executable, str(VERIFIER), mode], input=raw,
            capture_output=True, text=True, timeout=15, check=False)
    if done.returncode or len(done.stdout)>20000:
        raise ValueError('subprocess failed')
    outcome = json.loads(done.stdout)
    if type(outcome) is not dict or type(outcome.get('pid')) is not int:
        raise ValueError('invalid subprocess result')
    return outcome


@dataclass(frozen=True)
class IssuedAttestations:
    status: str
    receipt: str | None
    bundle: dict | None
    challenge: str
    signer_pid: int | None


@dataclass(frozen=True)
class VerifiedHandoff:
    status: str
    tasks: tuple[tuple[str,str], ...]
    usable: tuple[str, ...]
    replay_calls: int
    verifier_pid: int | None

    @property
    def proof_for_use(self):
        return self.status=='INDEPENDENT_PROCESS_FRESHLY_VERIFIED' and bool(self.tasks) and len(self.usable)==len(self.tasks)


def issue_owner_attestations(task, private_keys, challenge):
    """Fixture signer controls private keys; issue CP-29 receipt from live route."""
    if not is_hex(challenge,48) or not _bound(task):
        return IssuedAttestations('ATTESTATION_INVALID_DECLARATION',None,None,challenge,None)
    try:
        before=_digests(task)
        handoff=issue_handoff(task)
        if handoff.status!='HANDOFF_REFERENCE_ISSUED' or not _bound(task):
            return IssuedAttestations('ATTESTATION_SOURCE_UNPROVED',None,None,challenge,None)
        after=_digests(task)
        if before!=after:
            return IssuedAttestations('ATTESTATION_SOURCE_MOVED',None,None,challenge,None)
        record=_unpack(handoff.receipt)
        if record is None:
            return IssuedAttestations('ATTESTATION_RECEIPT_UNPROVED',None,None,challenge,None)
        claims=make_claims(challenge=challenge,route=task.route_name,
                    fingerprint=task.expected,witness=record['witness_sha256'],
                    source_digests=after)
        result=_child('sign',{'claims':claims,'private_keys':private_keys})
        if result['status']!='ATTESTATIONS_SIGNED':
            return IssuedAttestations(result['status'],None,None,challenge,result['pid'])
        # Recheck after subprocess returned, not merely before signature issue.
        if _digests(task)!=before or not _bound(task):
            return IssuedAttestations('ATTESTATION_SOURCE_MOVED',None,None,challenge,result['pid'])
        return IssuedAttestations('ATTESTATIONS_ISSUED',handoff.receipt,result['bundle'],challenge,result['pid'])
    except (ValueError, TypeError, KeyError, AttributeError, subprocess.TimeoutExpired):
        return IssuedAttestations('ATTESTATION_ISSUE_ERROR',None,None,challenge,None)


def receive_owner_attestations(issued, named, trust, expected_challenge):
    """No task proof until separate signature verification AND new CP-29 replay."""
    def denied(status, pid=None, count=0):
        return VerifiedHandoff(status,(),(),count,pid)
    if (type(issued) is not IssuedAttestations or issued.status!='ATTESTATIONS_ISSUED' or
        type(named) is not dict or not 1<=len(named)<=16 or
        any(type(n) is not str or not n or not _bound(t) for n,t in named.items()) or
        not is_hex(expected_challenge,48) or issued.challenge!=expected_challenge):
        return denied('INDEPENDENT_PROCESS_INVALID_REQUEST')
    receipt=_unpack(issued.receipt)
    if receipt is None:
        return denied('INDEPENDENT_PROCESS_INVALID_RECEIPT')
    first=next(iter(named.values()))
    if any(t._route is not first._route or t.expected!=first.expected or
           t.route_name!=first.route_name for t in named.values()):
        return denied('INDEPENDENT_PROCESS_ROUTE_MISMATCH')
    if first.route_name!=receipt['route'] or first.expected!=receipt['route_fingerprint']:
        return denied('INDEPENDENT_PROCESS_ROUTE_MISMATCH')
    try:
        before=_digests(first)
        expected={'challenge':expected_challenge,'route':first.route_name,
                  'fingerprint':first.expected,'witness':receipt['witness_sha256'],
                  'source_digests':before}
        verdict=_child('verify',{'bundle':issued.bundle,'trust':trust,'expect':expected})
        pid=verdict['pid']
        if verdict.get('status')!='ATTESTATIONS_VERIFIED':
            return denied(verdict.get('status','INDEPENDENT_PROCESS_INVALID_VERDICT'),pid)
        if tuple(verdict.get('verified_scopes',()))!=SCOPES or before!=_digests(first):
            return denied('INDEPENDENT_PROCESS_SOURCE_MOVED',pid)
        # Credential authenticity is NOT enough: mandatory current local audit.
        outcome=accept_handoff(issued.receipt,named)
        if before!=_digests(first) or any(not _bound(t) for t in named.values()):
            return denied('INDEPENDENT_PROCESS_SOURCE_MOVED',pid,outcome.replay_calls)
        if outcome.status!='HANDOFF_FRESHLY_REVALIDATED':
            return denied('INDEPENDENT_PROCESS_REAUDIT_UNPROVED',pid,outcome.replay_calls)
        return VerifiedHandoff('INDEPENDENT_PROCESS_FRESHLY_VERIFIED',
                    outcome.task_status,outcome.usable,outcome.replay_calls,pid)
    except (ValueError, TypeError, KeyError, AttributeError, subprocess.TimeoutExpired):
        return denied('INDEPENDENT_PROCESS_VERIFICATION_ERROR')
