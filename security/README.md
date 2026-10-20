# A/B security: authenticated continuation and finite movement

A small, testable security lane that protects evidence at handoff boundaries and
observes a separate finite bipolar movement. Neither implementation redefines
A/B or substitutes for native research verification.

## What exists

| Boundary | Actual mechanism |
| --- | --- |
| Confidentiality | Ephemeral X25519 key exchange, HKDF-SHA256, and AES-256-GCM per record |
| Source authentication | Ed25519 signature over the complete canonical envelope; pinned public key required to open |
| Continuity | Authenticated lane, event ID, expected parent envelope digest, and sender/recipient key fingerprints |
| Replay | Persistent SQLite first-admission ledger, unique per lane and event ID |
| Bipolar motion | Two separate finite trajectories with tests confirming probe movements do not change protected trajectory |

The finite-motion harness is not cryptography, malicious-intent detection, an
attacker sandbox, or an access-control replacement. Admission must come from an
independent authenticated authorization decision, **never** from oscillation alone.

## Use the evidence boundary

Requires Python 3.12+ and `cryptography>=45,<47`. This example generates disposable
test keys. Real deployments must enroll, protect, rotate and revoke keys separately.

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from security.continuation import ReplayLedger, seal_record, open_record, envelope_digest

sender = Ed25519PrivateKey.generate()
recipient = X25519PrivateKey.generate()
root = seal_record(
    b"observed native result", lane="world48", event_id="move-1",
    parent_sha256=None, sender_private_key=sender,
    recipient_public_key=recipient.public_key(),
)
with TemporaryDirectory() as d:
    ledger = ReplayLedger(Path(d) / "admission.sqlite3")
    assert open_record(
        root, expected_lane="world48", expected_parent_sha256=None,
        sender_public_key=sender.public_key(),
        recipient_private_key=recipient, replay_ledger=ledger,
    ) == b"observed native result"
    continuation = seal_record(
        b"continuation", lane="world48", event_id="move-2",
        parent_sha256=envelope_digest(root), sender_private_key=sender,
        recipient_public_key=recipient.public_key(),
    )
    assert open_record(
        continuation, expected_lane="world48",
        expected_parent_sha256=envelope_digest(root),
        sender_public_key=sender.public_key(),
        recipient_private_key=recipient, replay_ledger=ledger,
    ) == b"continuation"
```

Run the focused suite from the repository root:

```sh
python -m pip install 'cryptography>=45,<47'
python -W error::ResourceWarning -m unittest discover -s network/tests -p test_security_continuation.py -v
```

## Threat model and limits

Demonstrated: actual encrypted round-trip; failed signature and wrong
recipient/pin; tampered metadata or ciphertext; wrong lane/parent; oversized
records; duplicate event admission after process restart; and mathematical
noninterference between protected and probing motion under interleaving.

Not demonstrated: secure production key custody, authenticated human identity,
distributed replay consensus, tamper-resistant storage, a sandbox,
resistance to offline exhaustive analysis, physical-world safety, universal
cryptographic security, or continuous unattended protective action.

An authentic signature means **these bytes were signed by this key**, not
that the underlying observation is scientifically correct. A digest links a
specified parent envelope; it does not verify the parent automatically.
A hostile host can roll back or replace the local replay ledger. Private
research also requires confidentiality of appropriate metadata, protected
endpoints and backups. Do not commit private keys or plaintext records.

## Existing work stays intact

The specialized W13 encrypted native evidence vault continues to use its
own independently reverified source records. B14/B15 remains the current
operator key enrollment/revocation policy for its specific lane. These new
interfaces are opt-in; **no live runtime or network endpoint is rewired** by
this change.

Before connecting it to other researchers or real-world control:
authenticate and enroll the signer, secure persistent key material and
recovery, enforce the gate at every native entry point, coordinate replay
across machines, test concurrent/adversarial operations, and get an
independent security review.

The design goal is continuous observation of bounded movement with actual
evidence of which boundaries held; it does not promise perpetual hindrance.


## Authenticated native runtime ingress (draft review)

`security/runtime_ingress.py` is an opt-in entrance to the real
`runtime.engine.HandoffRuntime`; it does not replace the existing
scheduler, durable journal, or native witness contracts.

- `seal_handoff` and `AuthenticatedHandoffIngress.submit` sign, encrypt and
  admit a real `Handoff` only after checking the pre-pinned signer public key,
  the operator-selected lane, exact parent digest, signed event identity,
  claimed source actor, and destination actor.
- `seal_result` and `AuthenticatedHandoffIngress.return_result` bind a
  signed `ExecutionResult` to the runtime's last event, enforce the assigned
  worker identity, and pass the result through the existing native evidence
  requirements instead of inventing new completion semantics.
- The separately configured `IngressAuthority` supplies fixed actor/key
  policy. Neither actor identity nor key enrollment is inferred from the
  received message. Admission does not start a worker.
- Focused tests use actual `HandoffRuntime` and `RuntimeJournal` instances,
  restart state, check replay, wrong actors, changed ancestry, stale returns,
  and unsupported evidence.

Run all focused tests:

```sh
python -W error::ResourceWarning -m unittest discover -s network/tests -p 'test_security_*.py' -v
```

**Storage boundary:** Accepted handoffs and results are passed to the existing native `RuntimeJournal`, which serializes their contents as ordinary local JSONL. Transport encryption does **not** make those at-rest journal bytes confidential. Do not submit secrets or human-private research into a journal without separately secured storage, redaction, permissions, and backups.\n\n**Trust boundary:** This is not a global interceptor. Applications must keep
the raw `HandoffRuntime.submit/run/return_result` methods away from
untrusted callers and exclusively route their untrusted ingress through this
adapter. Private keys and operator key enrollment remain external. Replay
admission and runtime journal submission are two separate writes: a journal
failure consumes that envelope ID and fails closed. Before deployment, address
atomic cross-store recovery, distributed replay consensus, key revocation,
concurrent results, and independent external audit. The experimental bipolar
model is never used to authorize a worker.

## Native HTTP entrance

[HTTP ingress: admission, operator configuration, and limits](HTTP_INGRESS.md)
describes the optional signed worker endpoints on the actual
`runtime.http_server`. The server is loopback-only, and the signed
endpoints are disabled by default until a trusted host installs pinned keys.
This does not turn unconfigured web clients into authenticated researchers.

## Sealed native journal and operator key lifecycle

[Sealed journal — encrypted native records, recovery boundaries, and key custody](SEALED_JOURNAL.md) documents the optional AES-256-GCM journal. The default service still uses its historical plaintext journal until a trusted host explicitly opts into a new protected history. Existing plaintext data is never silently migrated, deleted or overridden.

Signed HTTP ingress now requires the repository's existing B14 operator-enrolled Ed25519 signing key ledger. Each request checks current enrollment, including after operator rotation and revocation. No HTTP request can enroll a signing key. The private journal encryption key is **not** the B14 signing key, and revoking a signing key cannot restore a lost encryption key.
