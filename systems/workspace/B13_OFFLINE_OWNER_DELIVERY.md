# B13 — Offline source-owner signature and explicit delivery

## Main referent

B12 can freshly inspect an existing B3 native finite-worker return and
submit it through B11's signed LOCAL_PASS gate to B10's event-driven journal.
B13 exposes that same path to a local operator **without requiring the
private signing key or a source-owner signer callback in the workstation
process**.

The operational movement is:

1. A source-owning host already has an explicitly admitted/completed B3
   native job, one original B2 lane, opening and persisted native return.
2. An operator independently provisions **raw 32-byte Ed25519 public key**
   bytes and supplies a separately confirmed SHA-256 fingerprint of those
   bytes (not copied from the signed response). This pin is a trust decision,
   never a source hint or identity automatically established by B13.
3. `prepare` creates an inert B10 candidate/route request. The selected
   B9 source suggestion must match the existing native B3 worker edition,
   job locator and exactly one candidate relation.
4. `signing-request` freshly checks the B3 native return and emits the
   canonical B11 `protocol + receipt` bytes as hex, without a signature.
   The owner signs those **exact bytes externally**, outside this repository
   and without passing a private key to the workstation.
5. The operator provides a signed response JSON with only `protocol`,
   `receipt` and `signature`; `deliver` requires an explicit flag and
   exact handoff ID confirmation. B13 rereads the real B3 result, rejects
   any changed native state/route/receipt, then delegates to the unchanged
   B11 Ed25519 verifier and B10 event journal.
6. B10 independently re-observes the same B3 source-native return one more
   time. It does not execute the finite worker again. A successful relation
   is candidate-local and never proves the entire B9 route.

## Invoked CLI

```text
python -m systems.workspace.b13_offline_owner_delivery
  --construction-dir <existing-B9-construction-data>
  --native-data-dir <existing-B3-native-workstation-data>
  --observed-journal <separate-B10-B11-journal>
  --lane-id <original-B2-lane-handoff>
  --opening-id <original-native-help-opening>
  --job-id <already-completed-B3-job>
  --confirm-source-job <same-B3-job>
  --pinned-public-key <operator-provisioned-raw-32-byte-public-key>
  --expected-public-key-sha256 <independently-confirmed-64-hex-fingerprint>
  inspect
```

The same fixed parameters are required for the `prepare`,
`signing-request` and `deliver` subcommands. The full commands add:

```text
prepare --goal-id <B9-goal> --candidate-id <exact-candidate>
        --route-node <leaf> --route-node <middle> --route-node <goal>

signing-request --request-id <prepared-B10-request>

deliver --request-id <prepared-B10-request>
        --confirm-request <same-B10-request>
        --approve-native-delivery
        --signed-envelope <external-owner-signed-B11-response.json>
```

`signing-request` includes `canonical_bytes_hex` and
`canonical_sha256` for an independent owner tool. An external Ed25519
signer must sign the decoded raw bytes in `canonical_bytes_hex` and return
a 64-byte signature encoded as lowercase hex.

A signed response file must be an ordinary file of no more than 4096 bytes
with exactly:

```json
{
  "protocol": "b11-pinned-native-local-result/v1",
  "receipt": {"...": "the exact signing-request receipt"},
  "signature": "<128 lowercase hexadecimal characters signed externally>"
}
```

No signing key or credential belongs in this JSON. Public keys are not
accepted from the signed response or registered by it. The operator's
out-of-band fingerprint check prevents a file substitution from being
mistaken for the selected pin; it does **not** by itself prove the person's
natural identity or the external origin of a key.

## Native verification

The 17 B13 tests use the actual existing repository B3 native subprocess
with its previously admitted source edition and saved B2 lane result. They
exercise separate CLI invocations for `prepare`, `signing-request` and
`deliver`, an external ephemeral test signer outside the CLI, and the
original B11/B10 journal/observation checks. Negative cases include wrong
operator fingerprints, symlinked public keys, forged signatures, stale B3
source code, changed native evidence digests, stale B9 routes, invalid signed
response files and missing explicit delivery approval.

CI must also preserve the native B12/B11/B10 suites and the original
73 B9 construction tests. No skipped case is considered a PASS.

## Remaining limits

- The operator must supply *genuine* source-owner signing capabilities and
  independently authenticate a public key. CI uses a disclosed **ephemeral
  signer fixture**; no production source-owner identity is created here.
- This tool is invoked directly by an operator. There is **no daemon,
  background watcher, automatic credential enrollment or ChatGPT controller**.
- B13 refuses to use the original B3 source runtime journal as the B10\n  delivery journal, preserving distinct append-only evidence histories.\n- The original native journals remain single-writer. There is no
  concurrency-safe delivery protocol, external-effect reconciliation, or
  durable transaction spanning B9 and B10.
- Native B3 result verification is bounded to the finite computation.
  An observed candidate does not prove a completed route, an external
  CP30 owner/candidate relation, or any cross-lane join.
