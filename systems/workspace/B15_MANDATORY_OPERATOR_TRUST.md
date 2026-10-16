# B15 — Mandatory operator trust across legacy offline delivery

## Main referent

B9 makes candidate proposals; B10 prepares route-scoped native observation;
B11 checks signed local evidence; B12 re-verifies the original B3 native
finite computation; B13 offers an offline signing-and-delivery interface;
B14 records and revokes locally trusted operator key pins.

B14's trust gate was previously enforced by the **new** B14 wrapper, while
the **older** B13 CLI and direct `B13OfflineOwnerDelivery` constructor could
still take public key bytes and a matching digest **without an operator
policy**. This was a real alternate entry point for delivery, even though it
still performed cryptographic and native source verification.

B15 requires B14's actual `OperatorPinLedger` **inside B13 itself**.
B13 no longer accepts an optional trust callback that a caller may simply
omit. Its standalone command requires `--trust-ledger`. The B14 wrapper uses
the same mandatory policy instead of substituting a callback. Existing B12
low-level source/native verification stays available for independently
controlled tests and host integrations; this movement does not turn B12
into a production delivery entry point.

## Enforcement

1. B13 requires an explicit ledger path and compares the current key's
   SHA-256 to the exact completed B3 source-worker edition.
2. The trust file is kept distinct from B9 construction, B3 native, and B10
   observed event journals. Colliding paths are rejected before any delivery.
3. Preparation, signing requests, explicit delivery, native re-observation,
   and B11 independent LOCAL_PASS admission all consult the **current**
   operator policy.
4. An existing B13 object cannot keep using a pin after rotation, revocation
   or a corrupted policy history. Journal recovery rechecks the same policy
   before starting native observation on a historical signed event.
5. B13 never enrolls a key, signs using a private key, starts B3 a second
   time, authenticates a real person, or infers a complete B9 route.
   Enrollment/rotation/revocation remain explicit B14 operator operations.

## Updated invocation

The existing B13 command has one new **required** common argument:

```text
python -m systems.workspace.b13_offline_owner_delivery
  --trust-ledger <separate-B14-operator-pin-journal.jsonl>
  --construction-dir <existing-B9-construction-data>
  --native-data-dir <existing-B3-native-data>
  --observed-journal <separate-observation-journal>
  --lane-id <original-native-lane>
  --opening-id <original-helper-opening>
  --job-id <completed-native-B3-job>
  --confirm-source-job <same-B3-job>
  --pinned-public-key <independently-enrolled-32-byte-public-key>
  --expected-public-key-sha256 <out-of-band-verified-pin-digest>
  inspect
```

The `prepare`, `signing-request` and `deliver` B13 commands also need
that ledger. The single B14 CLI remains the recommended operator interface
for public-key administration and trust-gated native delivery. Direct B13
callers need `operator_trust_ledger_path` explicitly; code omitting it
fails instead of silently operating with no live revocation policy.

## Verification boundary

The new B15 suite checks fifteen cases against an existing *real B3 native
subprocess fixture*: old CLI with no trust path, old API with no policy,
unprovisioned/revoked/rotated key, stale B13 instance, journal-path collisions, symlinked trust-policy files,
signed LOCAL_PASS replay after revocation and a valid cross-process
prepare/sign/deliver with an operator-enrolled ephemeral test public key.

CI additionally executes the existing B14/B13/B12/B11/B10 native cases,
original 73 B9 construction cases, and the repository-wide protocol suite.
Native CI must pass in GitHub on the exact candidate before merge.

The test operator/key is a fixture, **not** a production source owner. The
local B14 hash-chained policy is not a tamper-resistant credential vault or
an externally authenticated identity registry. Production enrollment,
operator authority, concurrent-writer controls, and unattended event
scheduling remain separate walls.
