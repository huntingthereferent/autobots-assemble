# Exact owner pin and explicit re-pin — October 13, 2026

## Referent

Continue the bounded A/B mathematical chatbot's existing source-provenance contract without equating *reported* source labels, digests or revisions with ownership. An explicit task can identify one or both **locally issued pinned owner handles**. The task's previous mathematical goals, transition requirements, exact path histories and destination identities are evaluated by the unchanged `ProvenanceTaskSession` only after the exact handles pass.

This is an in-process research witness for a finite 27-state model. A/B continues to be language for following movement; these two operators are scoped finite examples, not an exhaustive model of human language or physical systems.

## New exact-owner task format

The caller must obtain a handle through `OwnerPinRegistry.issue(bridge)` **from a live locally verified owner binding**. The handle contains a randomized 48-character local registry token, the recorded source label, revision, digest and optional predecessor token. The token does **not** authenticate an external provider; its correctness depends on the already established trusted in-process owner binding.

```python
registry = OwnerPinRegistry()
original_pin = registry.issue(original_bridge)
changed_pin = registry.issue(changed_bridge)
request = {
    'goals': [[0,1,1],[0,2,0]],
    'required_owner_pins': {'old': original_pin.token, 'new': changed_pin.token}
}
session = ExactOwnerTaskSession(original_bridge, changed_bridge,
                                request, registry=registry, **options)
```

The registry checks **object identity** of both the owner and exact snapshot, the report version triple, and the live local owner binding **before and after each task continuation**, including zero-read revisitations. On withdrawal, mismatch or explicit revocation, the original pin is latched invalid and no former completion is returned. Unknown or malformed tokens are rejected before reading any transitions. A new bridge—even one with identical source-reported label, revision and digest—cannot reuse the old pin.

A **new explicit pin** creates a new registry entry and **new task session**. The optional `predecessor` is a historical reference, not a proof that the old/new owners are equivalent. Old pinned snapshots and results remain historical evidence, not newly witnessed conclusions. The library does not automatically repin, does not upgrade initially remote origins, and does not interpret ambiguous natural language.

## Reproduction

```bash
python -m unittest -q test_ab_chatbot_owner_pin_contract.py
python -m unittest -q test_finite_owner_pin_identity.py
python run_owner_pin_demo.py
```

The demo first completes a two-goal finite task with two locally verified owner pins: `GOALS_CARRIED_WITNESSED`, 28 original and 18 changed transition observations. Opening a **new snapshot** over the same old owner yields `OWNER_PIN_UNPROVED` if the old task token is reused. Explicit new pin and new task start at `SEARCHING` with **zero** inherited observations in that snapshot; the old snapshot retains its 28 observations.

## Verification and limits

- 10 new integrated exact-owner tests passed. Owner substitution, matching metadata with a different snapshot, version mutation, revocation, deliberate re-pin, remote cannot issue and invalid tokens are covered.
- 5 independently runnable finite identity-model tests passed. These check pointer/snapshot identity only, **not** real local HTTP attestation.
- 97 targeted unchanged regressions passed across seven modules: old provenance 14, mixed obligations 12, multi-required 13, prior task intake 11, language bridge 35, required-edge prefilter 8, and finite provenance 4.
- **112/112 tests** passed across separately completed runs. This is not the full historical suite. GitHub CI and remote-source authentication were not verified.

An in-process object identity is meaningful only within the current Python runtime. Across processes or machines, this experiment offers **no cryptographic source proof**. A copied digest, claimed source name, token string or equivalent finite transition table cannot inherit ownership. A version change without a new verified pin does not imply continuous provenance. The previous solver, task schemas and fixed-order default have not been modified.

## Files and next boundary

This full local package adds `ab_chatbot_owner_pin_contract.py`, `test_ab_chatbot_owner_pin_contract.py`, `finite_owner_pin_identity.py`, `test_finite_owner_pin_identity.py`, `run_owner_pin_demo.py`, `OWNER_PIN_RESULTS.json`, `OWNER_PIN_REGRESSION.json`, and this README. All prior 137 files are preserved byte-for-byte.

Next warranted question: how to **transport an explicitly authorized task across a fresh source pin** while replaying old evidence as historical *comparison* (not as automatically admitted new evidence). Keep side-specific preservation, source ownership, and mathematical relations separate. The unrelated repository `state/current.json` remains untouched.
