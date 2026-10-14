# Process Workstation — private copies and branching

The workstation belongs to the reusable [Workspace Continuity system](README.md), not to any one chatbot, finite process, factory, or future implementation. It is a place to **copy, alter, inspect, and branch** worker *source implementations* while preserving the canonical origin.

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

The workstation currently **does not run copied processes**, compile them, assign handoffs, autonomously edit code, verify arbitrary mathematical conclusions, operate physical equipment, or promote experiments into their original sources.

A future work station can connect an edition to the **existing** `runtime/HandoffRuntime` after checking capabilities, dependencies, required witnesses and task admission. That bridge must preserve source ownership and the worker-specific verifier, not invent a second general-purpose scheduler. No cloned test report or original CP evidence may be treated as a test pass for modified code without re-execution.

Reproduction:

```bash
python -m unittest -v network.tests.test_process_workstation network.tests.test_workspace_continuity
```

This local source-version facility is the first construction step, not a running AI-worker factory.
