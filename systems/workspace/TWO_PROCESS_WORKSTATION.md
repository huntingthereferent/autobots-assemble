# Process Workstation — two real bounded worker executions

The Process Workstation can now be populated, by an **explicit local command**, with two different implementations, an independent version branch, and two actual, recorded jobs. Both reuse the same workstation edition store, `HandoffRuntime`, `RuntimeJournal`, and read-only GUI.

**This is an opt-in LOCAL witness, not a hosted persistent service.** Source is committed to GitHub; actual worker copies, run events, and private data are created only on the computer where the command is executed. No background workers are started on GitHub.

## Run on your authorized computer

From the repository root (Python 3.12+):

```sh
python -m runtime.examples.workstation_two_processes --data-dir runtime/data --execute
python -m systems.workspace.view_server --data-dir runtime/data --port 8051
```

Open `http://127.0.0.1:8051/workstation.html`. The viewer is read-only; the `--execute` command is the separate affirmative decision to run selected local code. Don't point the workstation at source you haven't inspected: subprocess isolation (`-I`) is **not** an OS sandbox.

## Two worker types, no new scheduler

| Local worker | Source edition | Native job and witness | Boundary |
| --- | --- | --- | --- |
| Finite Correspondence Process | Original published finite goal/required-edge modules, copied to private version `baseline-001`, plus unexecuted branch `experiment-001` | Explicit required-edge prefilter, independently re-evaluated and recorded in existing runtime | A computed `NOT_CONTRADICTED` is not a proved correspondence or a claim of CP-0030 integration |
| Factory machine simulation process | `systems/workspace/factory_machine_worker.py`, copied to private version `machine-001` | Actual `FactorySystem` machine-stage handoff; child Python computes simulated part output; native `FactorySimulationAdmission` independently checks identical simulated result before journal admission | `simulation` / `simulated` evidence, **not** fabricated, manufactured, measured, or shipped physical goods |

The Factory order owns its `supply` and `machine` stage state. Its native simulated `supply` stage is completed first so that the machine stage receives the right inputs. The workstation displays the **machine** stage as its second worker job because it was assigned to the edition; the supply handoff remains source-owned Factory evidence, not an extra workstation worker.

The demo creates two `WorkspaceStore` lanes, one for each process, with exact handoff return references. Their histories and the two job results persist in private `runtime/data/runtime.jsonl`, `runtime/data/workspace.jsonl`, `runtime/data/factory_orders.jsonl`, and `runtime/data/workstation/`.

Re-running the **same command** recovers those records and rechecks their native verdicts without replaying completed jobs or creating duplicate event history. If source editions have changed since admission, verification fails closed. Editing/branching additional copies remains separately supported by `ProcessWorkstation` and does not silently replace these pinned versions.

## What this demonstrates—and does not

- Demonstrates two genuinely different source-selected local computations using one version-store, handoff event stream, verification boundary, and GUI.
- Does not claim the Finite Correspondence Process has generalized outside its declared finite operation.
- Does not claim a source-copied Factory simulation is a physical machine, or that all five factory stages ran through worker editions.
- Does not connect autonomous general AI agents, automatically admit jobs, or expose an untrusted remote code-execution service.
- The GUI displays `recorded-not-reverified` because reading records is not performing a new native check. The explicit setup/recovery command performs `reverify` before reporting completion.

## Reproduce

```sh
python -m unittest -v network.tests.test_workstation_two_processes network.tests.test_correspondence_worker_handoff network.tests.test_workstation_monitor network.tests.test_workstation_http network.tests.test_process_workstation network.tests.test_workspace_continuity
```

Next bounded move: extend process-specific **controls** only when separately authorized. The [native inspection panels](INSPECTION_PANELS.md) now show the two recorded process types through the existing read-only workstation GUI.
