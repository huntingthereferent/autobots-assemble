# Handoff Runtime

The runtime makes the repository's existing `core.handoff` contract executable.

It is deliberately small.

```text
world / human expression
        ↓
translation
        ↓
HANDOFF
        ↓
human / agent / program / machine / simulator
        ↓
result + evidence
        ↓
append-only event
        ↓
derived state
        ↓
next eligible handoff
```

## Boundary

The runtime is **not A/B**.

A/B remains the recursively reusable mathematical operation and witness/evidence contract described in `AB_CONTRACT.md`.

The runtime is an implementation layer that carries bounded work between unlike actors while preserving:

- current referent;
- required relation;
- inputs;
- expected output;
- required witnesses;
- admissible evidence;
- dependencies;
- boundaries;
- provenance.

## Durable vs live

The repository and runtime have different jobs.

```text
REPOSITORY
contracts / provenance / evidence / implementations / tests
        ↓
RUNTIME
live handoffs / events / current state / routing
        ↓
ADAPTERS
human / AI / software / machine / simulator
        ↓
PROJECTIONS
task / job / command / dashboard / language
```

A view can disappear and be regenerated. The handoff specification and append-only event history remain sufficient to recover why the current state exists.

## Common carrier

A handoff is not synonymous with a task.

```text
handoff → human projection      → task
handoff → program projection    → job
handoff → machine projection    → command
handoff → simulator projection  → simulated event
```

The receiving implementation may differ. The handoff/evidence boundary does not silently change.

## Event sourcing

`EventStore` preserves append-only events.

`HandoffRuntime.state(...)` derives current state from those events plus dependency state.

Supported live states:

- `WAITING`
- `READY`
- `ACTIVE`
- `COMPLETE`
- `PARTIAL`
- `BLOCKED`
- `FAILED`
- `UNKNOWN`

A handoff cannot become `COMPLETE` unless every required witness is returned using an admitted evidence kind.

## Files

- `handoff.py` — carrier, evidence, state, execution result, simulated actor
- `engine.py` — append-only event store and runtime
- `projections.py` — task/job/command projections
- `activation.py` — explicit actor+surface activation routes over existing handoff state
- `orchestrator.py` — generic system registration, routing, automatic execution, and result reconciliation
- `journal.py` — durable handoff-spec + event journal for restart recovery
- `service.py` — persistent application service over existing system/runtime contracts
- `http_server.py` + `http/` — bounded HTTP/HTML entrance
- `handoff.schema.json` — external serialized handoff shape
- `examples/cross_layer.py` — same carrier across James/school/software/factory
- `examples/tiny_factory.py` — sequential simulated production run
- `examples/ohayo.py` — James `ohayo` activation over a mixed handoff set
- `examples/full_ecosystem.py` — Personal Operations + Online School + Factory under one orchestrator
- `examples/restart_recovery.py` — crash after runtime result, recover without duplicate execution

The examples are witnesses for the runtime shape, not claims about physical production.


## Multi-system orchestration

`Orchestrator` sits above the shared runtime without owning any system's local state.

Each registered system exposes a small boundary:

```text
emit_ready()
→ zero or more SystemEmission records

reconcile(emission, returned_handoff_state)
→ mutate/reconcile only that system's local state
```

The orchestrator:

1. asks each system what is ready;
2. submits new handoffs to the shared runtime;
3. automatically executes handoffs when a registered executable actor exists;
4. leaves human/unconnected handoffs READY;
5. routes returned results back to the system that emitted them.

This means an automated factory can continue moving while human work remains visible in projections such as `ohayo`.

The demonstrated full ecosystem currently contains:

```text
Personal Operations
Online School
Factory System
        ↓
shared Orchestrator + HandoffRuntime
        ↓
human actors / simulated actors
        ↓
activation projections
```

The systems retain different local schemas. The shared boundary is the handoff.


## Durable restart recovery

`RuntimeJournal` persists both:

- the immutable handoff specification;
- append-only runtime events.

A submission writes the specification together with its `CREATED` event. Recovery therefore restores **what the handoff means**, not merely its status history.

On restart:

```text
system-local log/state
+
runtime handoff specs/events
        ↓
reconstruct systems + HandoffRuntime
        ↓
systems re-emit same pending handoff IDs
        ↓
Orchestrator re-binds origin routing
        ↓
READY work remains READY
terminal runtime results reconcile without re-execution
        ↓
normal movement continues
```

The crash-recovery witness specifically covers a process dying after a factory result is durably `COMPLETE` but before the factory records reconciliation. The recovered orchestrator applies the existing result and does not execute that operation twice.


## HTTP entrance

`python -m runtime.http_server` starts the shared local entrance on:

`http://127.0.0.1:8040`

Environment:
- `HOST` — bind host, default `127.0.0.1`;
- `PORT` — bind port, default `8040`;
- `ECOSYSTEM_DATA_DIR` — private durable state directory, default `runtime/data/`.

Current API:

```text
GET  /api/status
GET  /api/notes
POST /api/notes

GET  /api/plans
POST /api/plans

GET  /api/tasks
POST /api/tasks
POST /api/tasks/{task_id}/admit

GET  /api/handoffs?actor=&status=
POST /api/handoffs/{handoff_id}/result

GET  /api/activate?surface=ohayo&actor=james
```

The HTTP layer does not create a parallel model. It calls the existing Personal Operations, activation, orchestrator, runtime, evidence, and recovery contracts.

The included dashboard exposes Notes, Plans, Tasks, Live Handoffs, and the `ohayo` projection while preserving their boundaries.
