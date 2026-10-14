# Process Workstation — explicit local controls

**Observation stays read-only.** The [viewer](view_server.py) only serves GET requests and never admits jobs, forks files, or executes selected code. The GUI's *Prepare an operation* section selects a known worker edition and displays a command. Copying that command is not a job admission or execution.

The separate [local CLI](controls.py) is the **opt-in control boundary** over existing `ProcessWorkstation`, `HandoffRuntime`, `RuntimeJournal`, and native process adapters. It introduces no AI agent, alternate scheduler, network code-execution API, or universal task semantics.

## Available actions

| Action | Effect | Gate |
| --- | --- | --- |
| `prepare` | Read-only source inventory and bounded-input validation; returns exact edition fingerprint | Selected existing edition; no journal writes |
| `admit-finite` | Admit **one** finite required-edge prefilter task to shared runtime, status READY | `--confirm-admit` must equal explicit `--job-id` |
| `inspect` | Read one recorded job and its inspection/evidence from the journal | Read-only; not native re-verification |
| `execute` | Execute **one** READY selected source edition, or reverify an already-completed job without another execution | `--confirm-execute` equals existing `--job-id` |
| `reverify` | Independently replay the process-specific verifier against the recorded result/source | Read-only replay; does not execute the worker again |

A Factory machine-stage job is admitted **only by `FactorySystem`'s native stage emission** (via the existing `FactoryMachineSimulationBridge`). It cannot be manufactured from free-form JSON or by `admit-finite`. When explicitly executing a READY Factory machine job, the CLI reconciles its source-owned local order once. Subsequent calls reverify without re-running the machine simulation.

## From the repository root

Run on an authorized computer with Python 3.12+. To populate two known test jobs and worker editions the first time (this command **does execute** two trusted local examples):

```sh
python -m runtime.examples.workstation_two_processes --data-dir runtime/data --execute
python -m systems.workspace.view_server --data-dir runtime/data --port 8051
```

Open `http://127.0.0.1:8051/workstation.html`; select the edition in **Prepare an operation** to see the corresponding shell commands. The page does not send any POST. If you want a **new finite task**, save a JSON file such as `runtime/data/finite-inputs.json` with the exact declaration below:

```json
{"old_phi":[0,0,1],"new_phi":[0,0,0],"candidate_words":[["ABAA","ABBABA"],["ABAA","AAABB","BAAAB"]],"required_state":[0,0,0],"required_action":"B"}
```

Then invoke the CLI explicitly in separate steps:

```sh
python -m systems.workspace.controls --data-dir runtime/data prepare --worker finite-correspondence-process --version baseline-001 --inputs-file runtime/data/finite-inputs.json
python -m systems.workspace.controls --data-dir runtime/data admit-finite --version baseline-001 --inputs-file runtime/data/finite-inputs.json --job-id finite-local-002 --confirm-admit finite-local-002 --from-actor local-operator
python -m systems.workspace.controls --data-dir runtime/data inspect --job-id finite-local-002
python -m systems.workspace.controls --data-dir runtime/data execute --job-id finite-local-002 --confirm-execute finite-local-002
python -m systems.workspace.controls --data-dir runtime/data reverify --job-id finite-local-002
```

`prepare`, `inspect` and the GUI cannot start a worker. `admit-finite` only records a READY job. Only `execute` runs the selected local source when READY, and only after exact ID confirmation. Existing COMPLETE jobs are reverified without another subprocess or new handoff event. An ACTIVE/UNKNOWN/BLOCKED/FAILED job requires a separately reviewed recovery decision, not blind retry.

## Source and safety boundaries

- The edition must be selected deliberately; its complete current fingerprint is pinned at admission and checked before execution and replay. Editing a version after admission blocks its result. Branch source copies with `ProcessWorkstation`, not by rewriting another edition.
- A source copy and a successful earlier CP are **not** permission to claim a new worker capability. A newly modified copy must be tested; native verifier checks only its expressly supported computation.
- Executing local Python code is **not sandboxed** by `-I`. Only run locally trusted and reviewed copies. Neither the viewer nor the CLI is a remotely authenticated multi-user service.
- `NOT_CONTRADICTED` remains a finite prefilter verdict, not proof of a correspondence. Factory completion remains `simulation` / `simulated` evidence, not physical machining.
- The workstation has no general-purpose task translation or dynamic worker code evaluation. New process types need an explicit native adapter and evidence contract; the shared UI and journal need not change.

## Tests

```sh
python -m unittest -v network.tests.test_workstation_controls network.tests.test_workstation_inspections network.tests.test_workstation_two_processes
```

The `workspace-continuity` workflow runs these against the real repository runtime. A passing local/CI finite test is not a deployment or a physical production claim.
