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

## Two-process workstation witness

The [local two-process setup](TWO_PROCESS_WORKSTATION.md) creates real version-pinned finite computation and simulated Factory machine-stage jobs in the **same** private runtime journal, with source-owned native verification and the read-only workstation viewer. It is opt-in (`--execute`); running the viewer alone never creates or executes a worker. Both jobs remain separate by their native realization and evidence scopes.

## Native worker inspection

The [read-only inspection adapters](INSPECTION_PANELS.md) render one shared workstation UI with process-specific panels: finite candidate prefilter verdicts, Factory machine-stage simulated outputs, and a generic fallback for other workers. A panel reads recorded native state and never replays a verifier or creates work.

## Explicit local controls (separate from the viewer)

[Local workstation controls](WORKSTATION_CONTROLS.md) now support read-only
edition/input preparation, exact-ID admitted finite prefilter jobs, explicit
single-job execution, and native re-verification of completed recorded results.
The dashboard merely selects versions and displays local commands; it has **no
POST endpoint** and never starts a worker. Factory machine stages still require
a source-owned Factory handoff. Neither copying nor preparing a process creates
work automatically.

## Preferred edition -> future bounded job

The [preferred-job admission contract](PREFERRED_JOB_ADMISSION.md) rechecks the recorded
preferred source fingerprint and the original native supporting job before a
**new and explicitly confirmed** job can be admitted. It records the exact
preference event on the new handoff. Admission creates READY without executing.
Finite prefilter inputs must be provided explicitly; Factory admissions must
attach to an already-emitted source-owned pending machine stage. A changed
source or replaced selection fails closed; a preference is never a scheduler.

## Current witness / limits

The new focused regression tests cover independent lane movement, connection without state merging, unstructured exploratory lanes, focus switching, read-only person-scoped views, return points, restart replay, provenance ancestors, and corrupted-data rejection.

The core workstation is an **opt-in local process-and-viewer implementation**; it is not a hosted application or a physical machine. The orchestrator, Day-to-Day activation, browser UI, authorization layer, real external source verification and concurrent multi-process writers **are not connected or proven** by this module. Writing to a journal path is a local operating action; GitHub source alone does not start a running service or access private state.

Reproduce from the repository root:

```sh
python -m unittest -v network.tests.test_workspace_continuity
```

The next bounded movement is an explicitly admitted bridge to existing handoffs, if and only if a lane reaches work requiring an actor; do not auto-admit ordinary observations or creative exploration.

## Version comparison and explicit preferred edition

[Version comparison and promotion controls](PREFERRED_EDITIONS.md) compare actual
source inventories across two worker editions. A preference is accepted only
with a native-reverified COMPLETE job for the **exact selected fingerprint**.
It is an append-only local selection for future *manual* work, not a new CP,
automatic job admission, source merge, deployment, or general validation.
The read-only viewer displays stale preferences instead of silently falling back.

## Integrated CP30 verifier worker

The [CP30 three-scope signature-check adapter](INTEGRATED_CP30_HANDOFF.md)
allows an explicitly copied, source-pinned **281-file historical CP30 edition**
to check a caller-supplied challenge-bound Ed25519 scope bundle in a local child
process. A separate host-owned native verifier recomputes the exact signature
verdict before any RESULT enters `HandoffRuntime`. The original source stays
unchanged; a branch can be independently tested. The dashboard shows the exact
recorded verdict but never authenticates people, enrollment, or the fresh
owner-backed route audit. Current preferred-version promotion remains scoped
to its two existing worker operations and is not generalized by this adapter.
