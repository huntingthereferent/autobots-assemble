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

The simulator returns `simulation` evidence. **The current stage contracts admit
only simulation evidence**, because this repository has no connected physical
supplier, machine, inspection instrument or carrier source verifier. A correctly
labeled `supplier_record`, `measurement` or `carrier_record` supplied by an
unverified caller therefore cannot complete these simulated-stage handoffs.

Those physical evidence kinds describe *possible future source connections*,
not existing admission paths. A real source must provide its own verifiable
record/identity and source-specific admission before changing this contract.

## Running factory

`run_simulated_order(...)` repeatedly asks the factory for its next handoff, runs it through the shared runtime, reconciles the return into local order state, and asks again.

The system therefore drives continuation from **changed state**, rather than a script hard-coding all downstream handoffs in advance.


## Native simulation witness — language before implementation

**What the current stage claims:** Given this Factory handoff's simulated
inputs, the deterministic native simulator computed the reported simulated
output and emitted the recorded simulated witness.

**What it does not claim:** A physical supplier delivered material, a machine
ran, a physical part was inspected, or a carrier shipped a package.

The source-owned `FactorySimulationAdmission` in
[`simulated.py`](simulated.py) uses the existing runtime native-verifier
registration boundary. It does not add another runtime or mathematical engine.

When explicitly enabled, it:

1. checks that the handoff is one of Factory's actual five current simulated
   stages with the matching actor, relation and witness;
2. checks a reported `COMPLETE` against `default_simulated_actors()` using
   the handoff's own inputs, including the exact output and simulated
   source/ref/depth;
3. rejects the result **before** it enters the shared journal if the report
   differs, and fails closed if the native verifier was not registered;
4. exposes `reverify(handoff_id)` for replaying a recorded `COMPLETE` after
   a journal restart.

Attach it to the existing Factory binding with
`factory_binding(factory, simulation_admission=FactorySimulationAdmission(runtime))`.
Other systems and generic handoffs retain their existing contracts. The
optional verifier does **not** automatically recheck every existing journal
reader; consumers requiring verified native evidence must call
`reverify()` after recovery.

Native deterministic replay establishes **internal consistency with the
simulation**, not authentication of the machine that ran it or a physical event.
The unwrapped legacy Factory binding still checks evidence labels without
native replay; use the explicit verified binding when that stronger source
boundary matters.

See [the focused tests](../../network/tests/test_factory_source_admission.py)
for fabricated supplier/carrier reports, matching labels with forged output or
source, fail-closed verifier registration, and restarted-journal mutation.

## Current wall

No physical source adapter has been reached. The next test is not to rename a
simulated outcome as physical; it is to identify an actual source with an
inspectable record/identity contract, check that contract at its boundary, and
preserve any missing physical witness as UNKNOWN/WALL. No additional claim of
physical manufacturing or shipping is made.
