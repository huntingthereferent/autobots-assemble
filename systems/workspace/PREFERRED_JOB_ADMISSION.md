# Preferred edition — admitted future work, not automatic execution

This stage connects the existing **append-only preferred edition** ledger to the
existing **HandoffRuntime**, without changing either worker's native verifier.
Selection records an exact worker/version/hash and a completed, natively
rechecked supporting job. A preference is a *choice of source*, **not evidence
that future tasks are complete**. Neither the original research nor earlier
worker editions are overwritten.

## New job admission sequence

```text
review source edition and completed supporting job
                 ↓
explicit preferred edition record (version, SHA-256, event ID)
                 ↓
prepare-preferred [READ ONLY; native supporting-job replay]
                 ↓
confirm selected event ID AND exact new job/handoff ID
                 ↓
native-specific job admission (READY, not executed)
                 ↓
explicit separate execute command -> verifier -> event journal
```

Selection can be replaced without rewriting an earlier job. Every admitted
handoff retains its own `worker_version`, `edition_fingerprint`, and
`preferred_selection_event` and provenance reference. A later selection never
silently switches an existing READY job. If the edition changes after admission,
execution/reverification refuses to promote the recorded result.

### Finite Correspondence Process

First explicitly select a version using `promote` in
[preferred editions](PREFERRED_EDITIONS.md). Inspect its event ID in
`python -m systems.workspace.controls --data-dir runtime/data preferred`.
Provide a *new* finite input file with the same bounded schema as the existing
required-edge prefilter:

```sh
python -m systems.workspace.controls --data-dir runtime/data prepare-preferred --worker finite-correspondence-process --inputs-file runtime/data/finite-inputs.json
python -m systems.workspace.controls --data-dir runtime/data admit-preferred-finite --inputs-file runtime/data/finite-inputs.json --job-id finite-next-002 --confirm-admit finite-next-002 --confirm-selection ACTUAL_SELECTION_EVENT_ID --from-actor local-operator
# This job is now READY only. No subprocess was started.
python -m systems.workspace.controls --data-dir runtime/data inspect --job-id finite-next-002
python -m systems.workspace.controls --data-dir runtime/data execute --job-id finite-next-002 --confirm-execute finite-next-002
```

Replace the placeholder with the actual event ID. A missing selection,
changed source, invalid finite inputs, missing or inconsistent supporting job,
replaced selection event, or reused job ID prevents admission. A copy has no
inherited verification. The original prefilter only assesses contradiction;
`NOT_CONTRADICTED` is **not** proof of an admitted correspondence.

### Factory machine stage (simulation only)

After native Factory has **actually created and emitted** a pending machine
handoff (and the supply-stage simulation is verifiably recorded complete),
the exact pending handoff may be bound to the current preferred machine worker.
The workstation cannot invent an order, synthesize a supply witness, or assign
physical machine work:

```sh
python -m systems.workspace.controls --data-dir runtime/data prepare-preferred --worker factory-machine-simulation-process
python -m systems.workspace.controls --data-dir runtime/data admit-preferred-factory --order-id ACTUAL_ORDER_ID --confirm-handoff ACTUAL_PENDING_HANDOFF_ID --confirm-selection ACTUAL_SELECTION_EVENT_ID
# READY only; separate explicit execute and replay checks remain required.
```

Evidence stays `simulation` / `simulated`. This does not operate machinery.

## Boundaries

- The workstation dashboard is still read-only and loopback-only. It displays
  terminal commands rather than issuing mutations; there is no POST endpoint.
- Source hash, selection event, admitted job ID, and native supporting job are
  required. There is no automatic fallback to another version.
- The runtime and preference ledger are local files, not a multi-process
  locking service. Do not run simultaneous admissions in this prototype.
- The supporting job is natively rechecked at selection use. **Every future
  job still needs its own execution and verification.**
- Locally selected Python is trusted code, not an OS sandbox. `-I` does not
  constitute isolation of untrusted source.

Focused regression:

```sh
python -m unittest -v network.tests.test_workstation_selected_admission
```
