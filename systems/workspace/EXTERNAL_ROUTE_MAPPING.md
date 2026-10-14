# External GitHub finite-source declarations → CP30 native boundaries

**Status: staged, read-only declaration preflight. No external CP30 owner integration or admitted task.**

This layer accepts three exact **operator-supplied local copies** of public files previously fetched by the [GitHub observer](GITHUB_OBSERVATION.md). It verifies that the copies still have the signed-and-observed SHA-256 bytes, checks a narrowly declared F3 A/B transition schema, and produces a machine-readable account of the CP30 owner/pin requirements **not yet satisfied**. It does not contact GitHub, start workers, call `HandoffRuntime`, or append any journal event.

## Why this boundary is necessary

Recovered native CP30 route auditing is built from CP29's `RouteBoundTask`, the live two-hop route object, and `OwnerPinRegistry` instances. A native pin is issued only after an in-process bridge passes `LOCAL_OWNER_VERIFIED`, with exact owner, bridge, and snapshot object identity. Later, CP30 rechecks the *same* pinned source objects and performs a fresh two-pass route audit before evaluating exact task edges.

A remotely obtained JSON declaration, GitHub blob digest, or Ed25519 signature **cannot** produce those local object identities or source-owner proofs. External source descriptors therefore remain **declarations**, not native pins. Tests execute the recovered CP29 native `accept_handoff` and `OwnerPinRegistry` gates with external descriptions and confirm rejection.

## Source content contract

Each enrolled GitHub file must be JSON, at most 1 MiB, with **exactly** these fields:

```json
{
  "kind": "cp30-external-finite-declaration/v1",
  "scope": "donor",
  "source_id": "src-donor",
  "challenge": "cccccccccccccccccccccccccccccccccccccccccccccccc",
  "route": "left",
  "route_fingerprint": "<exact 64-character lowercase digest from receiver>",
  "witness_sha256": "<exact 64-character lowercase digest from receiver>",
  "old": {
    "source_label": "donor-old", "revision": 1, "phi": [0, 0, 1],
    "claimed_edges": [
      {"state": [0, 0, 0], "action": "B", "target": [0, 1, 0]}
    ]
  },
  "new": {
    "source_label": "donor-new", "revision": 1, "phi": [0, 0, 0],
    "claimed_edges": [
      {"state": [0, 0, 0], "action": "A", "target": [1, 0, 0]}
    ]
  }
}
```

Repeat for `middle` and `final`, with their actual enrolled `source_id` values. The challenge and digests above are placeholders; use the exact strings from an actual receiver-issued challenge. Recompute and sign each **file's exact SHA-256** in the existing three-scope signed-claim flow before observing GitHub. In particular, a source changing its bytes requires a **new** signed challenge and observation; do not change the existing record.

`phi` is the declared F3 law triple used by the original finite `Law.step`: action `A` advances x modulo three; action `B` advances y and z under `phi`. Each `claimed_edges` record must agree with its own declared `phi`. The host checks internal consistency and duplicate edge keys, but an internally consistent *claim* is not a witnessed transition or native CP30 correspondence.

No source content field is named `owner_pin` or permitted to supply a local owner object. Arbitrary extra fields, duplicate JSON keys, mismatched source/route/challenge/witness fields, invalid F3 states or inconsistent transitions are rejected.

## Read-only mapping

After explicit enrollment, accepted signed claims, and a successful `SOURCE_OBSERVED` event, save the exact publicly observed bytes in three local files and run:

```sh
python -m systems.workspace.external_route_mapping \
  --data-dir runtime/data \
  --challenge RECEIVER_ISSUED_CHALLENGE \
  --observation-event EXACT_SOURCE_OBSERVED_EVENT_HASH \
  --donor-file /private/donor.json \
  --middle-file /private/middle.json \
  --final-file /private/final.json
```

The read-only mapping requires a recent observation (within 10 minutes), exact event ID, unchanged active signer enrollments and three content digests matching **both** the accepted signed declaration and recorded observed GitHub bytes. The files are not downloaded by this command. The prior observation did not store their contents, so exact local copies must be retained separately.

Expected status: `EXTERNAL_DECLARATIONS_CHECKED_NATIVE_OWNER_UNPROVED`, with all native proof flags **false**. It reports the declarations' shape and internal finite consistency but never `TASK_COMPLETED_ON_SELECTED_ROUTE` or CP30 `proof_for_use`.

| Native gate | Status after this mapping |
| --- | --- |
| Signed claims and exact public-file bytes | Confirmed against local ledger and operator copies |
| Internally consistent declared finite A/B edges | Checked as *claims*, not observations |
| Live in-process local owner with matching snapshot | **Unproved** |
| Registry-issued exact owner pins | **Unproved** |
| Original two-hop route/certificate and identity | **Unproved** |
| Fresh native two-pass route audit | **Not performed** |
| Selected exact task edges satisfied | **Not established** |

This preflight is **not** an online freshness check at mapping time; it relies on the previously completed observation and a bounded age. GitHub branches may have moved since then. None of the operators in this stage independently authenticates the real-world organization behind a GitHub account. Local hash-chain records do not resist an authorized writer rewriting the full journal, and writes assume one writer.

## Tests

Run from the repository root (Python 3.12+, `cryptography>=45,<47`):

```sh
python work/arc_like_maze/chatbot/research/integrated/assemble.py --stage 30 --out /tmp/cp30-native-check
CP30_NATIVE_SOURCE_DIR=/tmp/cp30-native-check python -m unittest -v \
    network.tests.test_external_evidence \
    network.tests.test_github_observation \
    network.tests.test_external_route_mapping
```

The tests use generated local keys and **mocked GitHub API responses**. The native contract test loads reconstructed historical CP30 to confirm **rejection** of external descriptors. The source mapper itself has no network or execution path. This is a verified admission boundary, not an external-owner native CP30 integration.

## Two-observation continuity boundary

After completing **two** separately challenged, signed public-source observations, the [external source continuity checker](EXTERNAL_SOURCE_CONTINUITY.md) can compare claimed revisions and, when explicitly authorized, GitHub commit ancestry. It does not create `LOCAL_OWNER_VERIFIED` objects, owner pins or CP30 route proofs.

## Further bounded comparison

See [external declarations versus native cached edges](EXTERNAL_NATIVE_BINDING.md)
for an additional, explicitly source-controlled in-process comparison of exact
signed declaration bytes to previously witnessed CP30 native transitions. This
does not make external declarations into local owner objects.
