# B5 — Owner-native local observation at an unstaffed continuation lane

**Current referent:** B4's native finite prefilter identifies a next
owner-native observation need. B5 attaches that need to an *existing*
source-controlled CP30 in-process observation interface without pretending a
matching repository file is itself an owner or a worker.

## B5 path

1. B4 first records the exact owner-native need as a `WORKSTATION_HELP_OPEN`.
   Its origin is B3's actual source-owned finite subprocess and an additional
   domain-verified next-relation proposal. All B2/B3/B4 source evidence must
   still be fresh.
2. The caller supplies a reviewed CP30 source directory whose native modules
   are **already loaded**, plus a trusted `source_capture()` callback yielding
   actual `RouteBoundTask` objects from one live owner-held route. B5 does
   not construct owner pins from JSON, URLs or public source files.
3. With the caller's explicit native-audit request, the existing
   `observe_native_owners` verifies exact native local pins and snapshots at
   **two** captures; it may run the source-owned CP28 two-pass route audit.
4. B5 requires a specific selected task to return
   `TASK_COMPLETED_ON_SELECTED_ROUTE`; an unfinished task is refused.
   Separately, the trusted source owner must supply a
   `verify_candidate_binding` callback relating the native task to the
   **particular** unresolved finite prefilter candidate. That callback is a
   required capability, not something inferred from name equality.
5. After the native audit, B5 rechecks B4's original source, job output and
   admitted relation before recording the bounded observation.
6. Only with `allow_native_record=True` does B5 append
   `WORKSTATION_OWNER_NATIVE_LOCAL_TASK_AUDITED` to the **same lane's native
   RuntimeJournal**, preserving parentage, exact finite job, candidate index,
   native route fingerprint and native-local evidence digest.
7. Replaying the same source and audit returns the historical record without
   creating a duplicate; changed native evidence or task bindings are refused.

## What is and is not claimed

- A successful call is **a local in-process CP30 selected native task audit**
  and an owner-provided candidate-binding claim.
- It is **not** authenticated external owner identity, a new complete
  correspondence law, a proved finite candidate edge, independent CP30
  attestation, proof that the W13 game is complete, or evidence of an autonomous
  generative coding worker.
- If actual live CP30 owner tasks or their source-owned candidate-binding
  callback are absent, B4's need remains `OPEN_UNSTAFFED`.
- The preserved repository's CP30 fixture can be reconstructed for CI and
  tested with **synthetic owner objects**. These show the adapter's native
  operations really run, not that any outside source owner has been enrolled.
- This B5 interface is explicitly invoked by a trusted process, not a
  daemon, scheduler, external network service or arbitrary Python sandbox.

## Reproduction

```sh
python -m pip install 'cryptography>=45,<47'
python work/arc_like_maze/chatbot/research/integrated/assemble.py \
  --stage 30 --out /tmp/workstation-b5-cp30-native
CP30_NATIVE_SOURCE_DIR=/tmp/workstation-b5-cp30-native \
  python -m unittest -v \
    network.tests.test_workstation_owner_native_observer \
    network.tests.test_native_owner_observation
```

See `systems/workspace/workstation_owner_native_observer.py` and
`network/tests/test_workstation_owner_native_observer.py`. Earlier
B2/B3/B4 regressions run in the same dedicated GitHub Actions workflow.

## Next wall

A genuine separately controlled source-owner must supply current native task
objects and an independently validated candidate-to-task binding. Only then
can a real owner-native result contribute further movement. A live task audit
alone must never become a claimed generic A/B or cross-lane connection proof.
