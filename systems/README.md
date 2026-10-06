# Systems

A system owns a coherent body of **local operating state** and exposes supported movement to the shared handoff runtime.

The runtime does not absorb each system's internal model.

Instead:

```text
SYSTEM LOCAL STATE
        ↓
system-specific admission / adapter
        ↓
shared HANDOFF carrier
        ↓
another system / person / program / machine / simulator
        ↓
returned result + evidence
        ↓
system reconciles its own local state
```

This allows unlike systems to remain unlike internally while sharing one cross-boundary carrier.

Examples already present in the ecosystem include:
- Education Kernel — present learner relations regrounded from observations while prior relations remain natural provenance;
- Online School — education operation and schedule/task/artifact state;
- Personal Operations — notes, tasks, and plans;
- Calendar — dated/recurring time relations without automatically becoming work;
- Day-to-Day — person-facing attention projection over live work, explicit reminders, and Calendar;
- Factory System — order/stage state that generates the next handoff after each reconciliation;
- simulated factory witnesses — production state/events;
- future company, research, city, software, machine, or household systems.

## Boundary

A system is not A/B.

A system is not the handoff runtime.

A system may emit or consume handoffs, but it keeps its own local concepts, state, evidence, and invariants.

## System contract

A concrete system should make explicit:
- its local referents;
- its local record/state types;
- what events change that state;
- what conditions allow a local record to become a handoff;
- how returned handoff results reconcile back into local state;
- what evidence/provenance must survive the boundary;
- what activations/views can project it for humans.

No system is required to use another system's local schema merely because both can exchange handoffs.

## Shared orchestrator binding

`systems/bindings.py` contains the first concrete bindings to the generic runtime orchestrator.

A binding does not replace the system.

It exposes only:

```text
system local state
→ emit ready shared handoffs

returned handoff state
→ reconcile back into system local state
```

Current demonstrated bindings:

- Personal Operations;
- Online School;
- Factory System.

The Online School binding deliberately receives the school's own task provider, handoff adapter, and patch function. The orchestrator therefore does not need to understand the school's task schema.
