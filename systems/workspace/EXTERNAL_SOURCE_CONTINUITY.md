# External source continuity — two signed observations, no native owner pin

**Status: staged, opt-in verification of a public repository's reported history.** This is a separate evidence layer alongside the CP20–CP30 historical research, not an owner-backed CP30 route implementation. No historical sources, native CP30 owner-pin rules, or handoff runtime records are modified.

The existing [enrollment and signature contract](EXTERNAL_EVIDENCE_BOUNDARY.md), [GitHub observer](GITHUB_OBSERVATION.md), and [finite declaration mapper](EXTERNAL_ROUTE_MAPPING.md) establish **one** receiver-challenged observation. This adapter requires **two** independently issued challenges, accepted three-scope Ed25519 receipts, and separate `SOURCE_OBSERVED` events. Only an explicitly enrolled GitHub branch/file locator is eligible.

## What continuity means here

Across earlier and later observation records, the adapter requires:

- Exactly the same enrolled public-key fingerprint and `source_id` for each donor, middle and final scope, with no revocation or rotation.
- Exactly the same GitHub owner, repository, branch, file path and declared route/witness referent.
- Both sets of locally retained source bytes still matching their separately signed SHA-256 digests and the two public GitHub observation events.
- Matching declared source labels. Each F3 old/new revision must not regress; if its declaration changes, its own declared revision must increase. These are **claims about revisions**, not observed native owner state.
- If `--verify-github-ancestry` is explicitly requested: current GitHub branch heads must equal the later observed commit IDs both before and after comparison; GitHub's compare API must report the later commit as a descendant of the earlier one with the earlier commit as merge base. Divergence, force-push/rebase, stale observation, missing evidence, or head movement fails closed.

This checks an **external repository lineage**, not continuity of a real-world owner or source object. The signing key is operator-enrolled; a matching public GitHub blob does not establish the identity of the organization behind either key or repository. A source can consistently sign a false declaration. The source's reported `phi` and edges remain observations **of public bytes**, not observed system transitions.

## Exact command

Run the staged code in a trusted environment with `cryptography>=45,<47` after completing and retaining **both** observation rounds. Each round must have its own challenge, signing action and fresh GitHub observation. Retain the exact three JSON files for each round:

```bash
python -m systems.workspace.external_source_continuity \
  --data-dir runtime/data \
  --earlier-challenge EARLIER_RECEIVER_CHALLENGE \
  --earlier-event EARLIER_SOURCE_OBSERVED_EVENT_SHA256 \
  --later-challenge LATER_RECEIVER_CHALLENGE \
  --later-event LATER_SOURCE_OBSERVED_EVENT_SHA256 \
  --earlier-donor-file /private/earlier-donor.json \
  --earlier-middle-file /private/earlier-middle.json \
  --earlier-final-file /private/earlier-final.json \
  --later-donor-file /private/later-donor.json \
  --later-middle-file /private/later-middle.json \
  --later-final-file /private/later-final.json
```

This defaults to a **read-only, offline comparison**: `EXTERNAL_SIGNED_OBSERVATION_PAIR_NATIVE_OWNER_UNPROVED`. It requires both prior observations to be recent (within the existing mapping's ten-minute window). It will not contact GitHub, infer a current head, or emit new evidence.

To additionally query the public GitHub API for **commit ancestry**, opt in with both `--verify-github-ancestry` and `--confirm-later-challenge LATER_RECEIVER_CHALLENGE`. On an exact match, the status is `EXTERNAL_GITHUB_LINEAGE_REPORTED_NATIVE_OWNER_UNPROVED`. GitHub's API supplies a repository history assertion; this status does not mean independent real-world ownership or CP30 proof has been established.

## Deliberate limits

| Requirement | Available after this check |
| --- | --- |
| Two independently challenged accepted signed-source receipts | Yes, from prior evidence journal |
| Two independently recorded public GitHub blob observations | Yes, from prior observation journal |
| Declared same-key, locator and revision lineage | Checked |
| Current GitHub commit ancestry | Only when explicitly enabled, and subject to GitHub API evidence |
| In-process `LOCAL_OWNER_VERIFIED` bridge to an actual owned snapshot | **No** |
| Native registry-issued owner pins bound to exact source objects | **No** |
| CP30 two-hop route and fresh two-pass native audit | **No** |
| Exact task fulfilled / HandoffRuntime job admitted | **No** |

There is no remote write, no scheduler, no private-key storage, and no native worker execution. The local JSONL hash chain is not an independently anchored audit log; concurrent writers need locking. The optional HTTPS comparison is fail-closed but is not a security sandbox. Reconstructing in-process native owner bindings from public JSON would be a new **claim of locally owned source**, not genuine external ownership; this adapter intentionally does not perform that substitution.

## Tests

```bash
CP30_NATIVE_SOURCE_DIR=/tmp/cp30-native python -m unittest -v \
  network.tests.test_external_evidence \
  network.tests.test_github_observation \
  network.tests.test_external_route_mapping \
  network.tests.test_external_source_continuity
```

The GitHub observer and comparison requests are mocked in tests. **No real external source was enrolled, signed or contacted in these tests.** The native CP30 contract rejection test uses reconstructed historical source when `CP30_NATIVE_SOURCE_DIR` is supplied. This is an evidence-lineage adapter, not an externally authenticated CP30 task adapter.
