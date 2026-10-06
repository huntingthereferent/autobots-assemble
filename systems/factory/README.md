# Factory System

This is the first system that **generates its next shared handoff from its own changed local state**.

It replaces the earlier manually sequenced tiny-factory witness with:

```text
factory order state
→ next_handoff()
→ shared runtime
→ actor / simulator
→ result + evidence
→ factory.reconcile(...)
→ changed factory order state
→ next_handoff()
→ ...
```

## Local state

The factory owns:
- orders;
- product/material/quantity state;
- current production stage;
- pending handoff identity;
- reconciliation events.

The handoff runtime does not own those concepts.

## Current stage chain

```text
supply
→ machine
→ inspect
→ assemble
→ ship
```

That sequence is a current factory realization, not a universal handoff taxonomy.

Each stage declares:
- receiving actor;
- required relation;
- required witness;
- admissible evidence kinds.

The simulator returns `simulation` evidence. The same stage contract can later admit an appropriate real source such as machine telemetry, measurement, supplier records, inspection records, or carrier records without pretending the simulation was physical evidence.

## Running factory

`run_simulated_order(...)` repeatedly asks the factory for its next handoff, runs it through the shared runtime, reconciles the return into local order state, and asks again.

The system therefore drives continuation from **changed state**, rather than a script hard-coding all downstream handoffs in advance.
