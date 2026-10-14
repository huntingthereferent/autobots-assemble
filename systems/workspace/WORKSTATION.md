# Process Workstation — private copies and branching

The workstation belongs to the reusable [Workspace Continuity system](README.md), not to any one research project, finite process, factory, or future implementation. It is a place to **copy, alter, inspect, and branch** worker *source implementations* while preserving the canonical origin.

**Vocabulary:** Finite Correspondence Research = investigation; Finite Correspondence Process = executable implementation; Correspondence Worker = the role of one implementation carrying a bounded job. The name *worker* does not imply an AI agent.

## Copy and branch contract

```text
source-owned implementation (unchanged)
      |
      +--> workstation / worker ID / version 1  [copy]
      |             |
      |             +--> version 2               [branch modified copy]
      |             +--> version 3               [another independent branch]
      |
      +--> independent edition for other work
```

`ProcessWorkstation` supplies three narrow operations:
- `copy_source(source_dir, worker_id=..., version_id=...)` — capture selected source files into a fresh private edition and write their SHA-256 inventory.
- `inspect(worker_id=..., version_id=...)` — read-only report of added/modified/deleted files relative to that edition's recorded baseline.
- `branch(worker_id=..., parent_version=..., version_id=...)` — create another private edition from the parent's *current* source files while preserving the declared parent and fresh baseline.

IDs are path-safe; editions cannot overwrite one another; symlinks and known credential file names fail closed; transient caches/`.git` are omitted; size/file budgets limit accidental huge copies. The private copy is editable using normal developer tools. Editing one version does not rewrite the original or earlier versions. An edition's manifest tracks the copy event, **not cryptographic source authorship** or independent witness authenticity.

### Example (explicit local source selection)

```python
from systems.workspace.workstation import ProcessWorkstation

desk = ProcessWorkstation("runtime/data/workstation")  # private, git-ignored
v1 = desk.copy_source(
    "/path/to/verified-process-source",
    worker_id="finite-correspondence-process",
    version_id="experiment-001",
)
# Edit v1["path"] with ordinary development tools, then inspect:
print(desk.inspect(worker_id="finite-correspondence-process", version_id="experiment-001"))
v2 = desk.branch(worker_id="finite-correspondence-process",
                 parent_version="experiment-001", version_id="experiment-002")
```

The source path above is a placeholder. Select real, authorized source before using it; **the GitHub research folder does not include the entire integrated owner-backed CP-0030 package**. Private working copies belong outside the public Git tree.

## Execution and evidence are separate

The source-copy workstation itself **does not automatically run or assign processes**. The first optional [Correspondence Worker handoff adapter](CORRESPONDENCE_HANDOFF.md) connects a chosen edition to the **existing** `runtime/HandoffRuntime`. Its only implemented capability is a declared finite required-edge prefilter, executed locally in a subprocess with independent native mathematical replay before `COMPLETE` is recorded. Explicit admission and `allow_local_execution=True` are both required.

The adapter does not operate physical equipment, authenticate remote source owners, autonomously edit code, import the full CP-0030 owner-backed archive, or promote experiments into original research. No cloned test report or old CP evidence becomes a test pass for changed code without re-execution.

Reproduction:

```bash
python -m unittest -v network.tests.test_process_workstation network.tests.test_workspace_continuity network.tests.test_correspondence_worker_handoff
```

This local source-version facility is the first construction step, not a running AI-worker factory.

## Read-only process station

A separately started local viewer reuses the **same** private worker editions and `RuntimeJournal`, rather than inventing a second scheduler. Run `python -m systems.workspace.view_server --data-dir runtime/data --port 8051` from the repository root, then open `http://127.0.0.1:8051/workstation.html`. It projects every recognized process edition and admitted `source_system=process-workstation` job, regardless of worker family, with source-change checks, result evidence and event trails. An empty station stays empty; there are no sample jobs or automatic worker launches.

Read-only status is **not** native re-verification or proof of a currently executing process. The [viewer implementation](monitor.py) never modifies process copies or emits handoffs. To demonstrate a populated station, the first explicit [Correspondence Worker bridge](CORRESPONDENCE_HANDOFF.md) can admit and execute a task into the same `runtime/data/runtime.jsonl` only when invoked separately by an authorized caller. [Viewer details](README.md#local-workstation-viewer).

## Inspect recorded jobs without executing them

[Native inspection panels](INSPECTION_PANELS.md) display finite required-edge prefilter verdicts and simulated Factory machine output through one common workstation GUI. These are **recorded** observations only; source editions, verifiers, and execution controls remain separate.
