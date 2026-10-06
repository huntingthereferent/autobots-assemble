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
- `handoff.schema.json` — external serialized handoff shape
- `examples/cross_layer.py` — same carrier across James/school/software/factory
- `examples/tiny_factory.py` — sequential simulated production run
- `examples/ohayo.py` — James `ohayo` activation over a mixed handoff set
- `examples/full_ecosystem.py` — Personal Operations + Online School + Factory under one orchestrator

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
