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
| SEC-02 | BLOCKER | The existing service still exposes other trusted-local HTTP paths (tasks, Ohayo, notes and projections) and trusted Python calls. Signing worker results does not make the entire service authenticated. | Local staging only. Do **not** expose the HTTP service through a public host, port forwarding, or a reverse proxy. A separate complete authentication/authorization review is required. |
| SEC-03 | BLOCKER | Other local stores, workstation source files, workflow artifacts, backup copies and process memory remain outside the sealed journal. | Data inventory, separate encrypted storage policies and least-privilege protections before handling private research. |
| SEC-04 | BLOCKER | Journal and replay ledger are distinct commits. A crash between admission and journal write consumes the event ID but may not write the handoff. | Design/test single transactional admission or an operator-authorized recovery protocol before production. No automatic replay. |
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
