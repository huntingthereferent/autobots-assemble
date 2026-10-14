# Workspace Continuity — initial lane journal

A small operating-state system for returning to different developing threads of work without flattening their source systems. **A lane is not a task, a discipline, or an instruction to become productive.** James can move away from a thread and return without losing its current referent, what changed, what survived, or where to resume. An exploratory thread can exist without any work commitment.

## Canonical placement

`systems/workspace/` owns only the **workspace's** append-only lane events. It does not own the research, chatbot, factory, education, creative files, notes, or household records it references.

```text
source-owned research / factory / school / creative work / other systems
     |                       |
     +-- source locators ----+---> WorkspaceStore (lane return points)
                                      |
                                      +-- independently movable lanes
                                      +-- explicit cross-lane relation edges
                                      +-- one optional current focus
                                      |
                                      v
                              workspace_view (read-only)
```

The general rules stay at [`protocols/core/provenance.md`](../../protocols/core/provenance.md), cross-system work remains under [`runtime/`](../../runtime/README.md), and current person-facing attention remains under [`systems/day_to_day/`](../day_to_day/README.md). The workspace is **not** a new orchestrator and does not change `state/current.json` or `TASKS.md`.

## Native records

- `LANE_OPENED` — stable lane identity, ordinary name, current referent, actor, canonical source locators.
- `LANE_MOVED` — new referent if any, what changed and survived, explicit evidence locators, walls, next possible movement. A movement must refer to the previous movement event for that *same* lane.
- `LANES_CONNECTED` — explicit, directed relation from one existing lane to another. Both lanes remain independent. No task, witness, or status is transferred by the link alone.
- `FOCUS_SET` — one optional focus pointer, including `None`. It does not close, complete, prioritize, or create obligations.

These events are append-only JSONL when a private journal path is supplied. Event replay reconstructs the latest immutable lane snapshots. A broken event history is rejected rather than silently repairing continuity. Project source ownership and native evidence standards are unchanged.

`workspace_view(store, actor_id=...)` is a read-only projection filtered to a person. **Actor filtering is not access-control authentication**; private journals still require authorized storage and callers. It includes cross-lane links only when both endpoints are visible. No implicit work enters the existing handoff runtime. That would require a separate, explicit admission with its native witness contract.

### Small example

```python
from systems.workspace import WorkspaceStore, workspace_view

store = WorkspaceStore("/private/path/workspace.jsonl")
store.open_lane("research", label="Research", referent="finite chatbot",
                actor_id="james", sources=("work/arc_like_maze/chatbot/README.md",))
store.open_lane("factory", label="Factory", referent="physical system",
                actor_id="james", sources=("systems/factory/README.md",))
store.record_movement("research", changes="checkpoint reproduced",
                      preserved="earlier witnesses remain historical",
                      next_movement="inspect new boundary", evidence_refs=("commit:<sha>",))
store.connect("research", "factory", relation="shared test interface")
store.set_focus("factory")
print(workspace_view(store, actor_id="james"))
```

This example is illustrative and **does not assert** that those projects currently share the depicted interface.

## Worker source editions — reusable process workstation

The [Process Workstation](WORKSTATION.md) now adds an **opt-in local copy, inspect, and branch facility** for worker implementation source. It preserves a source inventory and independent editions; modifying a copy cannot rewrite its origin or earlier versions. This supports the [Finite Correspondence Process](../../work/arc_like_maze/chatbot/PROCESS.md) first but is not restricted to it or to chatbot applications. Copying source does **not** itself execute, validate, deploy, or register a worker with the runtime. The optional [Correspondence Worker handoff](CORRESPONDENCE_HANDOFF.md) now adds **one** explicitly admitted, version-pinned finite prefilter computation, running a selected trusted copy in a child process and independently replaying its finite result against the shared `HandoffRuntime`. It is not a general-purpose autonomous worker.

## Current witness / limits

The new focused regression tests cover independent lane movement, connection without state merging, unstructured exploratory lanes, focus switching, read-only person-scoped views, return points, restart replay, provenance ancestors, and corrupted-data rejection.

This is the **local state and read-only projection** stage. The orchestrator, Day-to-Day activation, browser UI, authorization layer, real external source verification and concurrent multi-process writers **are not connected or proven** by this module. Writing to a journal path is a local operating action; GitHub source alone does not start a running service or access private state.

Reproduce from the repository root:

```sh
python -m unittest -v network.tests.test_workspace_continuity
```

The next bounded movement is an explicitly admitted bridge to existing handoffs, if and only if a lane reaches work requiring an actor; do not auto-admit ordinary observations or creative exploration.
