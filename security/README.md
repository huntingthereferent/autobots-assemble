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
admission and runtime journal submission are separate writes in the legacy
JSONL lane. For the opt-in sealed native journal, replay and native event now
commit in one SQLite transaction (see [atomic admission](ATOMIC_ADMISSION.md)).
Before deployment, address legacy recovery, distributed replay, key revocation,
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

## Independent signed checkpoints and offline key recovery

[Checkpoint and offline recovery](CHECKPOINT_RECOVERY.md) covers signed external anchors, rollback/fork detection, trusted restart, and a separately encrypted recovery envelope for the actual native journal key. Nothing publishes those checkpoints, stores a production private key, or automatically restores a workstation. The operator must retain an authentic checkpoint and separate recovery credentials outside the journal's failure domain.

Once a trusted host registers a signed worker-result ingress, the legacy unsigned native-result and agent-result HTTP service methods refuse submissions; the signed native result path remains available. This opt-in boundary does not automatically authorize unreviewed local code that directly calls the underlying runtime.

## Independent review and local staging

[Review findings and controlled staging](REVIEW_AND_STAGING.md) records
a recovered-checkpoint authentication defect fixed on this branch, the
outstanding production blockers, and a read-only
`check_staged_local_security` gate. A passing local staging gate **cannot
authorize production use** or certify the operator's human identity or
off-host checkpoint custody. No external professional review is claimed.

## Signed-only HTTP audit

[The HTTP ingress contract](HTTP_INGRESS.md) now records the default-deny
HTTP fence: once any signer role is registered, **only** authenticated
handoff/result POSTs can reach the native service, and private legacy
`/api/` GET views are denied. The signed HTTP response no longer returns
decrypted native work material, only the handoff ID and status. The normal
local prototype retains its existing routes when no signer role is
configured. This still does not cover privileged direct Python calls.

## Native atomic replay admission

[Atomic native admission](ATOMIC_ADMISSION.md) binds each signed replay token to its encrypted native SUBMISSION or RESULT record in a **single** SQLite commit on the opt-in sealed journal path. Restart verifies that the replay table exactly matches the authenticated encrypted history. Fault-injection tests exercise before-commit rollback and after-commit lost acknowledgements. The legacy JSONL lane and offline recovery ledger retain their separate transactions; distributed admission remains out of scope.

## Independently witnessed remote source movement

[Source-bound offline witness exchange](REMOTE_WITNESS.md) lets an
operator-pinned observer verify a bounded contiguous encrypted journal
hash-chain extension from an independently owned source. The observer
keeps its own SQLite source checkpoint and cannot decrypt or execute the
source's work. CI exercises separate journals and keys, rejects missing
frames, alternate sources, wrong signing keys and competing observations.

This is **observation, not remote control**. There is no live network
transport, worker admission or distributed consensus. The independent
"hosts" in these regression fixtures are separately owned directories
and journals on one CI runner, not physically distinct machines.

## Authenticated witness transport and observer rollback anchors

[Witness-only TLS and independent observer anchors](WITNESS_TRANSPORT.md)
add a deliberately loopback-only TLS 1.3 receiver that authenticates a
pre-enrolled client certificate and separately verifies the source's
Ed25519 ciphertext-chain witness. Incoming HTTP cannot control native
workers, enroll identities or request decryption.

The receiving operator can separately sign and preserve its own
source-specific **observer checkpoint**. An observer that has rolled
back below this independently retained prefix is refused before another
witness movement is admitted. This requires actual out-of-band
checkpoint retention; creating a signature beside the SQLite file is
not independent storage.

The tests use genuine localhost TLS with temporary CA/server/client
certificates and separately owned source/observer journals on one
runner. Neither real internet transport nor physical multi-host
resilience is established. Security preflight for public deployment
remains blocked.

## Certificate authorization on witness transport (SEC-20)

The [observer transport's certificate lifecycle](WITNESS_TRANSPORT.md)
uses the existing local B14 operator-pin ledger rather than treating
a successful TLS handshake as indefinite authority. A trusted operator
must separately enroll each source's exact client-certificate DER digest.
The receiver checks current enrollment at construction, on each witness
request and after the proof checks before persisting an observation.
Tests cover revocation of an already-running client, rotation that
requires trusted listener reconfiguration, corrupt policy, and denial
when revocation occurs during proof verification. This is not an atomic
policy/journal commit or a production CA revocation service.

## A/B bipolar approach at existing cryptographic key use

[Key-approach motion and noninterference evidence](KEY_APPROACH.md) now link the *already existing* `BipolarBoundary` to the real `AuthenticatedHandoffIngress`. Each external approach moves only the bounded probe; the protected trajectory moves only after a cryptographically authenticated and successfully committed native handoff/result. **Neither key material nor key identity is changed by the bipolar model**. Negative tests include 250 invalid approaches, signature refusal before private-key derivation, bad native actors, replay attempts, and unchanged disposable test keys.

The approach/admission trajectories are event-driven; independently clocked
presence is opt-in and documented below. It does not hide all public envelope metadata or guarantee safety from a compromised local host. Authenticated signatures and native evidence checks still control actual admission; bipolar motion is the observation-layer relationship, not a new cipher.

## Independently continuing bipolar presence

The [native key-approach experiment](KEY_APPROACH.md) now includes
`NativePresenceRunner`, an **explicitly host-started**, monotonic-clock
driver for a *separate* bipolar presence trajectory. It advances without
incoming requests or worker results. Both trusted signed roles sharing
the same `HandoffRuntime` now share one key-approach referent.

`EcosystemService.start_local_key_presence()` and
`stop_local_key_presence()` are trusted-local Python lifecycle controls,
not HTTP endpoints. Startup requires the same sealed runtime and two
currently B14-pinned reciprocal actor roles. No worker is run,
journal event fabricated or cryptographic key modified. CI includes
actual idle-time thread ticks, independent interleavings, stable
native journal, and explicit stop/restart controls.

**What has not been proven:** this finite clock-driven trajectory is
not already a physical world-motion witness or perpetual protection;
its phase is only observed while the trusted process runs. It does
not obscure public envelope metadata, prevent key theft or grant
cryptographic authorization. The key material remains governed by
ordinary vetted cryptography and operator trust policies.

## Explicitly submitted A/B approach dialogue (toy maze)

[Consent-based message recorder and local maze demonstration](APPROACH_DIALOGUE.md)
allow a willing participant to type an entire submitted message into an
**explicit local A/B experiment**. Only complete messages deliberately
submitted after an informational consent notice appear in a bounded,
in-memory transcript. Submissions now **read** the independently
moving bipolar presence: they never step, reverse or stop it. The
observed orientation points to an explicitly fictional branch of words,
which always leads to another branch rather than any real key. Code-like
input selects a static Python, JavaScript, SQL, shell or prompt-shaped
signpost; no submitted code or instructions are ever executed.

This is **not** a covert keylogger, OS keyboard hook, recording service,
honeypot for unsuspecting people, public network listener, or log of
unsubmitted typing. Private keys and legitimate signed ingress remain
untouched. Basic obvious credential/email patterns are redacted;
such patterns are not comprehensive privacy protection. The operator
must not deploy the experiment to others without separate data handling,
consent and security review.

Local demo from repository root: `python -m security.approach_dialogue`.
