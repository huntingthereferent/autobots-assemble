# CP30 — signed external declarations matched to native cached edges

**Status: locally staged; not merged.** This is an **evidence-content comparison**, not a new CP30 owner authority. It adds `external_native_binding.py` alongside the existing public-source signature, GitHub observation, declaration mapping, continuity, and native-local owner checks. The recovered CP20–CP30 source is unchanged.

## Inputs and control boundary

A **trusted, already-running source-owning Python process** supplies:

1. An existing local `SourceEvidenceLedger` with receiver-issued challenge, three previously enrolled Ed25519 public keys, signed scope receipts, and *previously observed* public GitHub files (donor/middle/final). All verification and freshness checks remain in `map_observed_sources`; the binder performs **no network requests**.
2. Exact local copies of the three earlier observed declaration files, supplied by the authorized caller. Their SHA-256 hashes must still match the accepted signed observation.
3. `source_capture()` returning 1–16 actual native `RouteBoundTask` objects from the **same selected CP30 in-process route**, with its real old/new registry-issued pins. Native CP30 modules must be imported from the exact `native_source_root` directory. **A serialized declaration or a URL cannot substitute for these objects.**

The matcher double-captures native tasks, their live registry pins, same-process snapshot object identities, and native route evidence; rejects any observed change; checks the external evidence ledger did not change; and rehashes each file afterward. Native pin verification may mark an invalid pin inactive **in memory**. There are no runtime-journal entries or external-evidence ledger writes.

## What is actually matched

For **each of six sides** (`donor`/`middle`/`final` × `old`/`new`):

- External claimed source label and revision must equal the live native snapshot's claimed source and revision.
- At least **one** explicitly declared `state/action/target` edge must already exist in the native snapshot's **cached** edges.
- All declared edges must match the exact cached transitions and the locally bound owner-held revision. Merely agreeing with a proposed `phi` law is not sufficient.
- The signed route label and declared route fingerprint must match the selected native task's route and fingerprint.
- Each declared edge remains a **partial comparison**; we report both matched count and native cached-edge count, and explicitly mark *full table match = false*.

There is **no call to the native snapshot's edge-observation method**. The binder cannot acquire a transition to make an external claim look supported. The external JSON `phi` remains the declared law of that document; the native model can be conjugated or differently parameterized, so the binder **does not identify full laws from one or several matching edges**.

## Example integration from the owner-controlled process

```python
from systems.workspace.external_native_binding import bind_external_observation_to_native

report = bind_external_observation_to_native(
    data_dir=PRIVATE_DATA_DIR,
    challenge=RECEIVER_ISSUED_CHALLENGE,
    observation_event=RECORDED_GITHUB_OBSERVATION_HASH,
    source_files={
        "donor": DONOR_OBSERVED_COPY,
        "middle": MIDDLE_OBSERVED_COPY,
        "final": FINAL_OBSERVED_COPY,
    },
    native_source_root=REVIEWED_CP30_SOURCE_DIR,
    source_capture=OWNER_PROCESS_NATIVE_TASK_CALLBACK,
)
```

`source_capture` must come from the actual source-owning process holding its CP30 objects; it is not a callable obtained from an external JSON document. The API deliberately has no route-audit or task-authorization flag. If a separate native route audit is wanted, that remains the explicit `observe_native_owners(..., allow_native_audit=True)` call, with its own narrower witness scope.

## Claims deliberately **not** established

- Identical external and in-process owner identity, common real-world authority, or public-key enrollment by an independent owner.
- CP29 portable receipt revalidation or the CP30 independently signed three-scope route-authentication protocol.
- An all-states law equivalence, a full transition table, a rooted two-hop correspondence, an approved or finished task, or a new transition observation.
- A real live public-GitHub observation in these tests: GitHub responses are mocked. Network availability is not tested.
- Protection against malicious code inside the *already trusted* Python process, arbitrarily concurrent mutations, or changes hidden between the two captures. There is no OS sandbox and no independently anchored evidence journal.

**Interpret the positive result as:** the bytes of three previously signed and observed external documents agree with specified, already witnessed native-local transitions at two local captures. Anything stronger needs an independently demonstrated source-owned equivalence bridge and fresh native proof.

## Reproduce

```sh
python work/arc_like_maze/chatbot/research/integrated/assemble.py \
  --stage 30 --out /tmp/cp30-native
CP30_NATIVE_SOURCE_DIR=/tmp/cp30-native python -m unittest -v \
  network.tests.test_external_evidence \
  network.tests.test_github_observation \
  network.tests.test_external_route_mapping \
  network.tests.test_external_source_continuity \
  network.tests.test_native_owner_observation \
  network.tests.test_external_native_binding
```

No fixture output is promoted as external identity, CP30 proof or deployment evidence.

## Additional trust-anchor-relative authority check (staged)

The separate [authority delegation verifier](EXTERNAL_AUTHORITY_BINDING.md) can confirm that an explicitly operator-pinned **independent** Ed25519 key signed the exact scope/content/native-local handle binding. It still does not establish the authority key holder's real-world identity, CP30 route/task proof, or legal ownership; this source matcher remains read-only.
