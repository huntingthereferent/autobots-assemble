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
- Online School — education operation and schedule/task state;
- Personal Operations — notes, tasks, and plans;
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
