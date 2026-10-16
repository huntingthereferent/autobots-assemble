# B7 — Bounded workstation continuation cycle

The B2–B6 workstation on `main` preserves independent lanes, source-owned
native execution results, freshly witnessed next relations, owner-native local
audits, and explicit unresolved source-owner walls.

B7 adds one **invoked** coordination controller,
`systems.workspace.workstation_cycle.WorkstationCycle`, which:

- Reads the original `RuntimeJournal` through B2's existing
  `WorkstationContinuationHarness` without a second state store.
- Finds B3 verified returns only on genuine B2 continuation handoffs.
- Calls B4's existing `derive_next` and `next_pass` so every admitted
  follow-up requires the same native verifier and independently checked
  domain-specific relation.
- Repeats until the journal becomes stable or an explicit pass/event limit is
  reached, never running or admitting source-native workers by itself.
- Reports awaiting native execution, owner observation, unresolved returns,
  and previously preserved owner-source walls.
- Reopens the on-disk journal each pass and checks a content fingerprint
  for every existing event **and immutable handoff specification**. A source,
  parentage, or worker-metadata rewrite cannot masquerade as ordinary
  append-only progress within that invocation.

The final journal check is an integrity check, **not** concurrent journal
locking or cryptographic identity authentication. A single pass can append
more than `max_new_events` before the bound is recognized; the bound
limits subsequent passes, not writes already performed atomically by B2/B4.

## Invoked use (inside an authorized host process)

```python
from systems.workspace.workstation_cycle import WorkstationCycle

# host creates the EXISTING B2 harness and B4 continuation object with
# independently implemented source-native verify_observation,
# verify_connection and verify_relation callbacks.
cycle = WorkstationCycle(harness, return_continuation=b4)
report = cycle.run(max_passes=8, max_new_events=64)
```

B7 does not set up source-owner callback identities, scan GitHub for jobs,
start a daemon, execute a subprocess, spawn a model worker, or claim W13/CP30
external source authority.

## Verification

The new workflow `workstation-cycle-b7.yml` tests actual B3's source-pinned
finite subprocess and independent B4 native re-verification, as well as
the B7 controller's on-disk journal limits and tamper refusal.
The initial A/B observation in the native fixture remains simulated.
Do not promote `NOT_CONTRADICTED` to a proved edge; if an owner-native
capability is missing, record `OPEN_UNSTAFFED` and preserve that relation.

```sh
python -m pip install 'cryptography>=45,<47'
python -m unittest -v \
  network.tests.test_workstation_native_feedback_integration \
  network.tests.test_workstation_return_continuation \
  network.tests.test_workstation_cycle_repo_native \
  network.tests.test_workstation_cycle_bounds
```

This controller is sequential/invoked. Actual continuous orchestration would
also need authenticated native worker providers, independently evidenced
cross-lane joins, and multi-process writer coordination.
