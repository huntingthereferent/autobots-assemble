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

## Unlike-system continuity witness — mathematical research and simulated Factory

The [native cross-system regression](../network/tests/test_continuity_unlike_systems.py)
runs the existing Cyclic Action Engine and FactorySystem over the **same**
HandoffRuntime with RuntimeJournal persistence. The systems retain separate
source-owned evidence: the mathematical witness is re-entered through its
native verifier; Factory owns stage/order events and admits simulator results
only as `simulation` / `simulated` evidence.

The focused witness checks that:

- mathematical UNKNOWN and Factory stage continuation survive the same
  journal restart without duplicate earlier factory execution;
- a restriction to B-conjugacy on the 81-state invariant fiber is not
  promoted to full A/B conjugacy when Factory completes;
- mathematical evidence does not satisfy a Factory stage's required witness,
  and Factory simulation output cannot forge native mathematical verification;
- Factory's five simulated stages leave the stage evidence **simulated**,
  even when the order's local simulation state says `shipped`.

The native mathematical engine, Factory order model, and shared carrier are
not merged into one ontology. This is bounded interoperability evidence,
not a proof of arbitrary representation independence or physical production.

**Remaining boundary:** the generic Factory evidence contract checks
declared condition/kind, not independent authenticity of arbitrary supplier,
machine, measurement or carrier sources. Real-world production evidence
needs a source-specific admission/verification contract before it can be
treated as physically witnessed. A `COMPLETE` simulated stage is not proof
of physical manufacture or shipment.

Reproduce with the real repository modules:

~~~bash
python -m unittest network.tests.test_arc_like_cyclic_action_continuation network.tests.test_arc_like_continuity_handoff network.tests.test_continuity_unlike_systems network.tests.test_handoff_runtime network.tests.test_recovery network.tests.test_orchestrator -v
~~~

The dedicated Cyclic Action Engine GitHub Actions workflow checks these
suites; the larger protocol suite is a separate verification boundary.
