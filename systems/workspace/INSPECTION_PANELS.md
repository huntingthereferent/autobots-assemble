# Process Workstation — read-only native inspection panels

The shared workstation GUI renders process-specific observations for explicitly admitted jobs without putting the Finite Correspondence Process, Factory, or any later process's rules into the browser.

## Read-only relation

```text
native source + existing handoff + recorded result
  → inspections.py (chosen by the existing native verifier ID)
  → inspection data: kind, title, scope, inputs, outputs, notes
  → workstation_snapshot → /api/workstation
  → one generic workstation.js renderer (DOM textContent only)
```

The native verifier ID is a **display selector**, not a certificate. The inspector never registers, runs, or replaces the actual evidence verifier.

Current inspectors:

- **Finite required-edge prefilter:** old/new laws, requested edge, seed candidates and their *recorded* verdicts. READY work has no invented verdicts. `NOT_CONTRADICTED` is **not** a proved correspondence.
- **Factory machine-stage simulation:** original material/product/quantity and recorded simulated part/state. The job's evidence remains `simulation` / `simulated` rather than physical manufacture.
- **Generic fallback:** original handoff relation, assigned actor, status and output-field count when no source-specific inspector is registered. No mathematical or production claims are inferred for unknown processes.

A future source system may provide another read-only projector through `inspect_handoff(..., inspectors=...)` with the same string-only shape. The generic browser renderer does not need a new branch for each process.

## Preserved boundaries

- The viewer accepts local GET requests only. It never submits or executes a handoff, branches worker source, or reruns a verifier.
- A recorded `COMPLETE` stays `recorded-not-reverified` in this viewer.
- Edition changes still display `SOURCE_CHANGED`; an inspection panel cannot upgrade that state.
- Input/output fields come from recorded handoffs, not speculative live worker actions. The GUI inserts text with `textContent`, never HTML.
- The viewer is not an authentication mechanism or an OS sandbox.

## Verify and inspect

```sh
python -m unittest -v network.tests.test_workstation_inspections network.tests.test_workstation_monitor network.tests.test_workstation_two_processes network.tests.test_workstation_http
python -m runtime.examples.workstation_two_processes --data-dir runtime/data --execute
python -m systems.workspace.view_server --data-dir runtime/data --port 8051
```

Open `http://127.0.0.1:8051/workstation.html` and expand **Inspect** on a recorded job. Running the setup command is a separate explicit action; merely opening the viewer cannot execute worker code.
