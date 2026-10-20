# Security review and controlled local staging — PR #262

**Scope:** A/B authenticated handoffs, HTTP ingress, native sealed journal,
operator pinning, signed history checkpoints, and offline key recovery.

**Current posture:** A reviewable research implementation; **not approved for
production or remote researchers**. Keep the PR draft. The tests and this
document do not constitute an independent external security assessment.

## Review observations (2026-10-20)

| ID | Severity for external deployment | Finding | Resolution / next boundary |
| --- | --- | --- | --- |
| SEC-01 | Fixed on draft branch | Recovery validated the operator-signed recovery envelope but did **not** independently validate the supplied journal checkpoint signature. A valid recovery-envelope signer could present altered checkpoint bytes as if independently anchored. | Require `trusted_checkpoint_public_key` in `recover_journal_key`; verify the checkpoint's Ed25519 signature before decrypting. Regression signs an escrow against deliberately forged checkpoint bytes. |
| SEC-02 | PARTIALLY FIXED; production BLOCKER | The signed-result-only fence did not block Ohayo/task admission, other mutation endpoints or private GET reads. A loopback caller could bypass the intended signed ingress or observe protected data. | Signed-only HTTP mode now denies **all** unsigned POST routes and all API GET routes from first signer registration; signed routes return minimal non-decrypted receipts. This is local Handler enforcement, **not** privileged Python, multi-user or remote authorization. Do **not** publish the service through a proxy. |
| SEC-03 | BLOCKER | Other local stores, workstation source files, workflow artifacts, backup copies and process memory remain outside the sealed journal. | Data inventory, separate encrypted storage policies and least-privilege protections before handling private research. |
| SEC-04 | PARTIALLY FIXED; deployment BLOCKER | The legacy JSONL native journal and replay ledger still commit separately. The **opt-in sealed native ingress** previously had the same gap. | For sealed native ingress only, replay identity and encrypted SUBMISSION/RESULT are committed in one SQLite transaction and checked against each other on restart. Faults before commit roll back both; a lost acknowledgement after commit cannot admit a duplicate. JSONL/other ledgers, whole-host rollback, cross-host concurrency and independent review remain unresolved. See [atomic admission](ATOMIC_ADMISSION.md). |
| SEC-05 | BLOCKER | Signed journal checkpoint proves an **observed prefix** only if a newer checkpoint and its independently pinned signer survive outside the database's rollback domain. | Operator controls off-host anchoring, versioned retention, restore authorization and independent auditing; local preflight cannot prove this. |
| SEC-06 | BLOCKER | Keys are supplied by the trusted host. No production identity vetting, private-key custody, key rotation/re-encryption, retention, or cross-host revocation protocol is included. | Select and independently audit a trusted key-management workflow. Do not commit or log test/production secrets. |
| SEC-07 | BLOCKER | B14 policy uses an ordinary local hash chain. Operator authority and policy-file integrity require an independent trust root. | Protect policy custody and independently review operator actions and key source. |
| SEC-08 | BLOCKER | SQLite replay is local; distributed requests, host rollback, cross-process concurrency and multi-replica journaling are not implemented as one global proof. | Require independent concurrency/rollback review, source replay and multi-host tests. |
| SEC-09 | Research only | The bipolar finite-motion harness records bounded trajectories/noninterference, not general cryptographic protection or perpetual denial. | Preserve it as a distinct experimental lane. No security property is inferred from motion alone. |

A **passing CI** is evidence of specific implemented tests, not a substitute
for independent penetration testing, human authorization or live custody.
No outside reviewer has signed off on this PR.

## Dry-run go/no-go gate

`security.deployment_preflight.check_staged_local_security` is a **read-only
preflight** for an *isolated local pilot*. It neither accepts external
connections nor performs key enrollment, creates checkpoints, migrates
journals or starts a worker.

The operator provides an **already constructed** `EcosystemService`
with a fresh encrypted journal, both signed ingress roles independently
enrolled under the live B14 policy, an independently retained checkpoint and
its previously pinned Ed25519 verification key.

```python
from security.deployment_preflight import check_staged_local_security

# service, checkpoint and checkpoint_signer_public must come from separately
# authorized preparation. Never take them from the HTTP request being checked.
decision = check_staged_local_security(
    service,
    independently_retained_checkpoint=checkpoint,
    trusted_checkpoint_public_key=checkpoint_signer_public,
    listener_host="127.0.0.1",
)
for finding in decision.findings:
    print(finding)
if not decision.ready_for_isolated_local_test:
    raise RuntimeError("LOCAL STAGING REFUSED")
# A pass authorizes NOTHING by itself. No launch or service activation here.
```

The preflight refuses plaintext native journals, unpinned/revoked/wrong-role
signing keys, nonreciprocal lanes/actors, mismatched native runtime references,
invalid/missing checkpoints, and remote bind addresses. It does **not** verify
that a signed checkpoint is *actually* stored on an independent machine:
that requires separate human/operational evidence.

## Pilot procedure (only after authorization)

1. Use an isolated, access-controlled **new** working directory, not the
   current workstation's `runtime/data` and not a copy of any real person's
   research. Explicitly exclude production keys, existing worker lanes and
   machine-control interfaces.
2. Record the source commit, Python and library versions; run the focused
   security suite and repository protocol suite on that commit.
3. Independently pin disposable signers and a dedicated checkpoint signer.
   Keep the recovery recipient's private key **offline**.
4. Construct a fresh sealed journal; issue and independently retain a
   signed checkpoint; register the two reciprocal signed ingresses with
   active operator-trusted public key pins.
5. Run the read-only preflight and retain its structured findings alongside
   the exact source commit. **Stop** if any BLOCK appears.
6. Exercise a disposable signed handoff/result on loopback only. Independently
   verify source witnesses, restart/replay refusal, revocation, rollback
   rejection, and a controlled recovery to a **different isolated copy**.
7. Stop the pilot, retain or destroy disposable evidence according to the
   approved local policy, and request external security review. Do not
   interpret pilot success as a public deployment authorization.

## Before any production decision

Require an independent reviewer not involved in writing the security
implementation, documented resolution or acceptance of every BLOCKER above,
fresh successful CI at the reviewed merge commit, key-custody/runbook proof,
a complete HTTP/API permission audit, restore drill with independent anchor,
and a separate explicit go-live authorization.

**No unattended activation, internet exposure, or migration is authorized by
this file.**

## Additional adversarial review findings

- **SEC-10 — fixed on draft branch:** Protected-mode HTTP initially
  denied just unsigned agent/result endpoints, leaving Ohayo, task
  admission, personal mutations and private projections open. An
  allowlist fence now refuses every other HTTP mutation and all unsigned
  API GET reads **before JSON parsing**. The default local prototype
  stays unchanged until a signer is registered.
- **SEC-11 — fixed on draft branch:** Signed native HTTP response payloads
  previously reflected decrypted handoff inputs and result outputs.
  The signed routes now return only handoff ID and status. Integration
  tests place distinctive private markers in inputs, metadata, output
  and witness source and assert that response bodies disclose none.
- **SEC-12 — remains a deployment blocker:** Registered signed-only HTTP
  ingress is not a trust boundary around trusted Python code, native
  agent adapters, arbitrary local files, or unprotected process memory.
  Registration must be complete before HTTP listener startup; this PR
  does not implement a hardened multi-user service or independently
  attested signer key custody.

The legacy dashboard's HTTP API is deliberately unavailable while
signed-only mode is enabled. Do not treat this as an accidental UI
regression or silently re-enable unsigned reads for convenience.

- **SEC-13 — fixed on draft branch:** Encrypted native journal startup
  originally left legacy localhost APIs usable until the first
  authenticated signer role was installed. The HTTP entrance now enters
  signed-only mode immediately on sealed-service construction. Until
  operator trust is installed, both signed routes return 403. This is
  exercised with a fresh encrypted test journal and no enrolled worker.

## SEC-14 — sealed atomic native admission

The opt-in sealed native journal now binds replay identity to the signed native event **inside one SQLite commit**. The replay token and envelope digest are authenticated in encrypted journal content; restart compares every replay table entry to those protected records and refuses deletion, alteration or extra entries. Failure-injection tests interrupt between replay insertion and encrypted event insertion, after both inserts but before COMMIT, and simulate losing the network acknowledgement after COMMIT. Separate plaintext JSONL admission and recovery-escrow operations are unchanged. This is not distributed consensus, hardware power-loss certification or an independently audited production guarantee.

## SEC-15 — signed native concurrency

The authenticated `submit` and `return_result` paths now share one
native runtime admission lock, covering read/validation/commit instead of
relying on SQLite's write lock alone. Concurrent integration tests cover
independent submissions, duplicate attempts and two worker results against
the same parent event. The second conflicting result fails as stale, and
restart preserves one coherent recorded outcome. This is a **single-process
trust boundary**; privileged direct runtime calls and independently started
hosts are still outside it. [Protocol](ATOMIC_ADMISSION.md).

## SEC-16 — independent native process collision (local)

Two separately spawned interpreters independently restore the same sealed
native journal and compete to submit signed handoffs or return different
signed results referring to one earlier event. Tests require exactly one
successful commit, one stale-writer refusal, no duplicate persisted
native movement, and a coherent native restart. A follow-up test verifies
that a fresh, observed-and-authorized signed handoff can continue after a
stale writer is rejected. Independent processes do **not** share the
`HandoffRuntime` in-memory lock; their conflict is stopped by the
sealed SQLite sequence check under its `BEGIN IMMEDIATE` transaction.

Do **not** promote this to multi-host consensus or restart/retry
automatically against an obsolete parent. A real secondary process must
reload authentic, checkpointed evidence and obtain current authorization
before issuing new work. See [atomic admission](ATOMIC_ADMISSION.md).

## SEC-17 — separately owned source observation

A new optional [offline witness exchange](REMOTE_WITNESS.md) exports at
most 64 consecutive encrypted journal frames between a previously
pinned source checkpoint and its next signed checkpoint. A separate
observer stores source-specific witnessed prefixes and refuses
missing/altered frames, old observations, the wrong signer, and
conflicting signed histories that do not extend the already observed
prefix. It never copies the source decryption key or admits source work.

**Not resolved:** the cross-host gap is not a distributed protocol; two
untrusted machines have not communicated over a real network, remote
authorization and key custody remain operational decisions, and a
remote source's signatures do not prove the truth of plaintext work.
Observer SQLite state still requires independent retention to defend
against observer-side rollback. Tests use isolated directories on the
same CI machine. No production route is opened.

## SEC-18 — mTLS witness-only transport (local)

The separately owned observation lane now offers an opt-in TLS 1.3
listener **restricted to localhost** and only `POST /v1/witness`.
It requires a trusted client certificate, an exact operator-enrolled
certificate fingerprint mapped to an already-pinned source Ed25519
key, plus a valid ciphertext witness that extends that source's
existing observed prefix. The receiver returns a minimal receipt and
does not dispatch work or expose the core HTTP workstation API.
Negative tests include unrecognized clients, missing client certs,
false source claims, unauthorized endpoints and ambiguous JSON/HTTP
framing. See [transport contract](WITNESS_TRANSPORT.md).

**Deployment still blocked:** the local ephemeral TLS fixture is not
a field-tested two-host transport, an identity-management system, an
internet-service boundary, or a production certificate revocation
scheme. Keys, TLS configuration and source identity must be separately
authorized and reviewed before any external traffic is permitted.

## SEC-19 — independently signed observer continuity

The operator may issue an independent observer-owned checkpoint for
the per-source acknowledged prefix: source identity, current signed
source checkpoint, counted movement history, and its canonical digest,
signed by a separate observer key. The witness receiver verifies this
anchor at startup and before accepting another observation.
Rollback of the observer SQLite ledger behind a newer independently
retained signed prefix is refused in tests. A valid older anchor
cannot protect subsequent *unanchored* observations.

**Deployment still blocked:** there is no actual off-host automatic
checkpoint publication, independent retention schedule, hardware
trust root, observer PKI, or disaster recovery system. The receiving
operator is responsible for retaining authentic anchors outside the
SQLite file's rollback domain. Passing CI does not prove such an
independent custodian exists.

## SEC-20 — live operator revocation of pinned TLS client certificates

The witness-only TLS receiver now requires a separately maintained
B14 `OperatorPinLedger`. Trusted enrollment scopes the exact DER
certificate fingerprint to a locally pinned source ID. The running
receiver checks that the certificate is still current on every
incoming signed witness request, and repeats the check after proof
verification before committing the observer advance. The test suite
covers a valid observation before revocation, denied subsequent
observations, rotation disabling the old certificate, missing enrollment,
corrupted operator policy, and revocation during witness verification.

**PARTIAL FIX, NOT PRODUCTION APPROVAL:** This denies subsequent
requests and tested in-flight revocation before the second check, but
B14 and observer SQLite cannot commit policy and observation together.
A revocation may race with the final SQLite write. A compromised local
operator ledger is also not a trusted independent PKI authority. See
[the certificate lifecycle contract](WITNESS_TRANSPORT.md).

## SEC-21 — bipolar approach at real key-use ingress (bounded)

The existing `security.finite_motion.BipolarBoundary` is now connected to the actual signed native ingress through an operator-only `KeyApproachBoundary`. An incoming approach can move the independent probe trajectory; a **durably accepted native movement** advances the protected trajectory. Invalid signatures, unauthorized actor claims and replays leave that trajectory unchanged. The 141-test security CI includes a key derivation guard and unchanged disposable signing/recipient-key test. [Observed relationship and limits](KEY_APPROACH.md).

**Still open:** this event-driven harness does not by itself prove uninterrupted native movement in the absence of input; it does not constitute cryptographic authorization, passive traffic secrecy, general leak resistance or a guarantee against key theft. The existing crypto, trust enrollment and server protections remain necessary. A compromised host still has privileged access outside this ingress.

## SEC-22 — independent native bipolar presence with no key mutation

A trusted native host can explicitly start a `NativePresenceRunner`
attached to the real signed key-approach boundary, with no need for
incoming requests. The monotonic-clock native thread advances a
**separate bipolar presence trajectory** while retaining the existing
probe and authenticated/durable-movement trajectories. Two signed
roles using the same runtime share this one observation referent.

A protected `EcosystemService` only starts this presence after both
reciprocally scoped B14-pinned worker roles are installed with the
same sealed native journal. Negative tests refuse missing roles,
revoked pins and plaintext runtime. Actual native idle tests verify
presence ticks without **any native journal events**, no HTTP requests
and no worker dispatch; stop halts it. The cryptographic key bytes,
key identities and replay rules are untouched.

**Remaining bounds:** the driver is opt-in, native and memory-resident.
It is not a durable source-synchronized physical world clock, cannot
guarantee timing through host suspend or crash, and its ticks are
*not* accepted as signed native evidence. Compromised endpoints,
traffic metadata, cryptographic leakage, keys exposed by an adversarial
host, and pre-existing untrusted Python entrances are not secured
by oscillation. No production deployment approval results.
