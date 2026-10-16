# B14 — Operator signing-pin lifecycle and live revocation

## Current referent

B13 provides a manually invoked, offline-signed B3 native result delivered through
B11/B10. B14 introduces a **local operator-approved PUBLIC key trust policy**
so key changes and revocations are checked at every native result boundary,
including after a B13 host was constructed and when B11 replays a saved LOCAL_PASS.

An operator's recorded name and audit reference are **claims**, not authenticated
legal identity. The original source-owner authority and CP30 evidence paths
remain independent. B14 neither creates a key pair nor asks for a private key.

## Trust lifecycle

`OperatorPinLedger` contains only one source name, source edition, public-key
SHA-256, explicit operator/audit references, event kind, and a local hash chain
per record. The externally supplied Ed25519 PUBLIC bytes are read from a
separate 32-byte file and must match the separately confirmed SHA-256.

- **ENROLL** requires a positive operator confirmation of the exact digest.
  Nothing is trusted merely because a key file exists.
- **ROTATE** requires both the old currently active digest and the new verified
  digest. Old keys become inactive immediately. A previously used digest
  cannot be silently reactivated for the same source/edition.
- **REVOKE** requires the exact active digest and removes current trust. It
  cannot be undone by restoring the old key file. A new key needs a new
  explicit enrollment or rotation.
- Every history read checks full record schema, record-hash chain, record order
  and allowed transitions; damaged history fails closed.
- No background service, keypair generation, source owner auto-enrollment,
  concurrent writer guarantee or remote authority is introduced. A hash chain
  detects uncoordinated changes but does not protect against a malicious actor
  able to rewrite the entire ledger. Protect this file with normal OS
  permissions and trusted backups.

## Native observation and recovery

`B14OperatorTrustedDelivery` composes the real B3 source from B12, the
offline B13 host, and a current policy lookup. It rejects shared trust,
source, construction, key and observed journal files.

The optional B14 callback in B12 is checked **before preparation, signing
requests, delivery, native re-observation and native result admission**.
B11 calls that verifier again when recovering an interrupted LOCAL_PASS.
A revoked, rotated or corrupted pin therefore cannot admit an old signed
receipt or trigger a new native attempt merely because a B13 object already
exists. Original B10 restart rules still protect uncertain external effects.

B9 route construction stays a proposal. Native B3 finite computation and
source-owner signature do not verify the whole route, parent CP or cross-lane
owner mapping. Historic events are retained and are not rewritten by revocation.

## Explicit local CLI

The operator uses:

```text
python -m systems.workspace.b14_operator_cli --trust-ledger <separate-trust.jsonl>
    pin --source-edition <exact-native-B3-edition> status

python -m systems.workspace.b14_operator_cli --trust-ledger <separate-trust.jsonl>
    pin --source-edition <edition> enroll
    --public-key <externally-supplied-raw-public-key>
    --expected-public-key-sha256 <independently-confirmed-digest>
    --confirm-new-sha256 <same-digest>
    --operator-ref <operator-reference>
    --verification-ref <separate-check-reference>

python -m systems.workspace.b14_operator_cli --trust-ledger <separate-trust.jsonl>
    pin --source-edition <edition> rotate
    --public-key <new-raw-public-key>
    --expected-public-key-sha256 <new-digest>
    --confirm-new-sha256 <new-digest>
    --confirm-prior-sha256 <old-active-digest>
    --operator-ref <operator-reference> --verification-ref <check-reference>

python -m systems.workspace.b14_operator_cli --trust-ledger <separate-trust.jsonl>
    pin --source-edition <edition> revoke
    --confirm-prior-sha256 <active-digest>
    --operator-ref <operator-reference> --verification-ref <check-reference>
```

The `native` subcommand accepts B13's existing native source, B9 construction,
separate observed-journal and public-key flags, then `prepare`,
`signing-request` or `deliver` with exact request confirmation and
`--approve-native-delivery`. It rechecks the current B14 operator trust
record rather than trusting a stale CLI invocation.

The signer stays a different process. It signs the exact raw
`canonical_bytes_hex` emitted by the signing request, and only its signed
B11 response is supplied to the delivery command.

## Verification and remaining walls

The dedicated B14 CI requires **25 tests**: operator policy transitions and
tamper rejection, live revoked-key attempts, source-edition scoping, real
native B3 signed delivery, and the CLI running in separate processes.
It also preserves the B13/B12/B11/B10 native suites and the original 73 B9
construction tests without skips.

No external production owner or person has been enrolled by these tests.
Deployment still needs a trustworthy human process for authenticating key
ownership, key storage/rotation, permissioned execution, integrity-protected
ledger backups, concurrency control and an authorized event caller.
