# B10 — B9 route-scoped event-driven native continuation

## Main referent

Carry an explicitly chosen B9 candidate requirement through one native
observation boundary without promoting candidate construction, a past local
test, or a possible source suggestion into an approved worker or a proof
of the requested result.

B9 is a graph of **proposals**. The event-driven journal is a record of
**attempts and independently observed results**. B10 is an opt-in handoff
between those existing mechanisms, not a combined source of truth.

## Implemented boundary

- `B9ContinuationBridge.prepare(...)` reads the **complete bounded B9 frontier**
  and requires an exact leaf-to-goal candidate route, including middle steps.
  A source hint must match a particular intermediate candidate, source
  identity, edition, and source locator.
- A separately configured `ObservedEventJournal` must expose a *previously
  authorized* `SourceAdapter` whose claimed output equals the candidate
  requirement. A B9 hint never grants that permission.
- Preparing an observation request submits one immutable, deterministic
  handoff into a **separate append-only journal**, with the selected route,
  source edition, candidate spec digest, and original provenance. This is not
  a native attempt; no LOCAL_PASS is emitted by construction.
- `scoped_local_verifier(graph, verify_native_local_result)` first checks
  that the original candidate, exact route, and source hint still exist.
  It then delegates evidence checking to the caller's independently
  supplied verifier. Only an accepted LOCAL_PASS can start the journal's
  existing event-driven continuation.
- The reactor now honors the optional
  `handoff.metadata.continuation_source_binding` (exact name and edition).
  This prevents an unrelated authorized adapter with the *same* relation
  from being substituted across B9 branches. Ordinary unbound event-journal
  work remains unchanged.
- The journal records ATTEMPT_STARTED before native execution and records
  real native results/errors. An interrupted started attempt remains
  RECOVERY_REQUIRED on restart, never automatically replayed.
- A successfully observed relation is **candidate-local**. B9's projected
  `whole_route_verified`, `join_observed` and native
  `execution_authorized` remain false, as do the bridge's route/join claims.
  Native B2/B3/B7/B8 admission is not bypassed.

## Example (source owner must provide real verification)

```python
graph = WorkstationConstruction(construction_dir)
journal = ObservedEventJournal(
    observed_journal_path,
    adapters=(authorized_source_adapter,),
    verify_local_pass=scoped_local_verifier(graph, source_owned_local_verifier),
)
bridge = B9ContinuationBridge(graph, journal)
request_id = bridge.prepare(
    goal_id, candidate_id,
    route=(leaf_id, middle_id, goal_id),
    worker_id=source_name, edition_ref=source_edition,
    source_locator=source_locator,
)
# PREPARE DOES NOT EXECUTE. Only an actual externally checked LOCAL_PASS
# emitted by its trusted source at the appropriate time can trigger an attempt.
# The native adapter independently observes the returned source evidence.
```

This is an integration **library**, not a production scheduler. It does not
automatically watch B9 history for new candidates; it does not bind ChatGPT
tool decisions, install external credentials, or enable unattended GitHub
operations. Its callable adapters and local-result verifier must be supplied
by an authorized source owner. The journals are single-writer: no concurrency
lock, signature scheme, crash-atomic cross-journal transaction, or external
effect reconciliation is provided by this change.

A scope or route invalidation after request creation causes the local verifier
to fail closed rather than silently selecting another route. Shared upstream
candidates on different routes remain separate handoff identities and
observational histories.

## Verification

The `workstation-b9-observed-bridge` GitHub workflow requires:

1. The new B10 bridge tests, including invalid hints, fraudulent LOCAL_PASS
   events, multiple possible native editions, restart recovery, and scoped
   route invalidation. No skipped tests.
2. Existing `test_observed_event_journal` and
   `test_observed_event_journal_native`, using the repository's real native
   B3 subprocess and independent return re-verification.
3. All 73 unchanged B9 construction tests (no skips).

The new suite also directly connects a B9 candidate to the real B3 finite
worker and independently re-verifies that native return. This is a bounded,
test-owned native worker, **not** a production job or a live source owner.

The CI result, not a locally saved PASS label, determines the trial result.
