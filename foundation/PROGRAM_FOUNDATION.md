# Program Foundation

## Status — frozen capability evidence

This foundation is the first broad **Programs** capability proof under [Complete Stack](../COMPLETE_STACK.md).

It is frozen at the current verified boundary. Do not continue adding generic program features by default. Reopen only when a real incoming problem exposes a missing relation that the current foundation cannot carry.


## Referent

This is the reusable implementation foundation beneath arbitrary program realizations.

A/B remains the recursively reusable mathematical operation. This file does **not** redefine A/B as software, a workflow, or a factory.

The software problem is narrower:

> given a bounded referent and its witnessed relations, preserve enough structure that a program can be realized without rebuilding the same foundation from scratch.

The realized program may be almost anything. Monitoring, scraping, analysis, transformation, simulation, automation, networking, ML, firmware, a desktop tool, a service, a CLI, or another shape are downstream realizations. None defines the foundation.

## Current failure

The repository already proves many realizations, but most projects still hand-build the same structural concerns:

- what enters;
- what must remain identifiable;
- what changes;
- what state survives;
- what operations are valid;
- what leaves;
- what counts as success;
- what failure means;
- what evidence proves the result.

That repetition means the evidence is broad while the implementation foundation is still shallow.

## Foundation contract

Every bounded program realization must be expressible through the same minimal relations:

```text
referent
  -> boundary
  -> inputs
  -> representation
  -> operations
  -> state
  -> outputs
  -> witnesses
```

These are relations, not required runtime components. A stateless CLI may have no durable state. Firmware may have no database. A transformation may have one input and one output. The manifest must permit those absences without forcing an application architecture.

### Referent

What is currently being acted on.

### Boundary

What is inside this realization, what remains external, and what conditions stop unsupported movement.

### Inputs

Evidence or signals admitted into the realization.

### Representation

The internal form that preserves the distinctions needed by the current operation.

### Operations

Transformations admitted over that representation.

An operation must declare what it consumes, what it produces, and what witness establishes that the movement was valid.

### State

What must survive between operations or executions, if anything.

### Outputs

Externally useful realized results.

### Witnesses

Inspectable conditions that establish that the realized program did what its boundary required.

## Critical invariant

The foundation must not know what kind of program it is building.

Program shape is supplied by the referent and admitted relations.

Adding a new realization should therefore primarily add:

- a manifest;
- domain-specific operations/adapters;
- witnesses;

rather than another copy of orchestration, provenance, execution records, evidence layout, testing conventions, and output generation.

## First acceptance witness

The first foundation witness should prove **shape independence**, not another domain.

Use one kernel to instantiate at least three materially different realizations:

1. a pure stateless transformation;
2. a stateful program;
3. an event/stream or device-style program.

Acceptance:

- all three use the same manifest schema;
- all three use the same execution/witness contract;
- no domain name or application category appears in kernel logic;
- each realization can add its own operation implementation without modifying the kernel;
- invalid manifests fail before execution;
- operation input/output contracts are checked;
- execution produces a common evidence record;
- a realized output remains usable as input to another admitted operation when its contract matches.

That last condition is the software witness most directly aligned with recursive reuse without claiming that the software kernel *is* A/B.

## What this replaces

The ability map remains a read-only projection for résumé purposes.

It no longer selects development.

Individual projects remain evidence/regression cases.

The active development referent is the reusable program foundation.


## Verified foundation movement

### Witness 1 — shape independence

One unchanged kernel now realizes:

- a stateless text transformation;
- a stateful counter;
- an event/device-style debounce stream.

All use the same manifest and execution/witness contracts.

### Witness 2 — cross-realization composition

A realized output from one manifest can be admitted as an input to another manifest when the declared value contracts are compatible.

The receiving execution records:

- parent execution identity;
- source manifest identity;
- source output name;
- linked-input provenance.

An incompatible link is rejected before the target operation executes.

**Verified:** program-foundation workflow run 10 and protocol-tests run 460 passed on commit `a83e2bc1c71367b5de66acdd3785f48b2f857b98`.

## Current edge — relation graph

Pairwise composition still requires hand orchestration.

The next witness is a generic bounded execution graph:

```text
program node
   output
     ↓ declared compatible relation
program node
   output
     ↓
program node
```

The graph layer must validate structure before execution, preserve lineage through every edge, and remain ignorant of domain/program category.

A cycle is not automatically invalid in the larger research sense, but this first bounded graph executor must reject cycles unless an explicit state/time contract exists. It must never invent recursion semantics.


### Witness 3 — generic relation graph

The same manifests can now be assembled as graph nodes with declared value relations.

Verified behavior:

- topological execution is derived from relations rather than hand call order;
- required input relations are checked before execution;
- linked values retain node/execution provenance;
- a manifest can be reused as another node downstream without kernel changes;
- incompatible links are rejected;
- cycles are rejected because recurrence semantics are not yet explicit.

**Verified:** program-foundation workflow run 13 and protocol-tests run 465 passed on commit `b9a45e20b806acf2f09d29e16dec8bb2a9cbe5c8`.

## Current edge — explicit recurrence

A cycle cannot be admitted merely because two types happen to match.

The next foundation witness is bounded recurrence:

```text
realization(input_n)
      ↓
   output_n
      ↓ same declared value contract
realization(input_n+1)
```

The software layer must preserve:

- contract compatibility;
- iteration identity;
- parent execution identity;
- value provenance;
- an explicit bound or stop condition.

This is evidence that realized outputs can remain usable under repeated application. It is not a claim that the runtime itself is A/B.


### Witness 4 — bounded recurrence

A realization can now feed one of its declared outputs back into one of its declared inputs across repeated executions when the value contracts are compatible.

Verified behavior:

- the first value is explicitly seeded;
- every later execution names the prior execution as its parent;
- the same manifest and operation implementation are reused unchanged;
- a finite step bound is required;
- zero-step recurrence is rejected;
- incompatible output → input feedback is rejected.

**Verified:** program-foundation workflow run 18 and protocol-tests run 471 passed on commit `3fe0a95f878a11e1a1239afd8fa64fa0f06945b4`.

## Current edge — external effects / ports

The kernel can now transform, compose, graph, and recur over represented values, but useful programs also cross boundaries into systems not owned by the kernel.

The foundation needs a generic relation for:

```text
realization
   ↓ declared required effect
external port / adapter
   ↓ observed result
represented value + provenance
```

The kernel must not contain filesystem, network, device, process, UI, or service-specific behavior. Those remain adapters.

The common foundation should only preserve:

- what effect an operation declares;
- whether that effect was admitted for this execution;
- what adapter satisfied it;
- what evidence/result crossed back into the program.

This is an admission/evidence contract, not a security sandbox.


### Witness 5 — declared external effects

Operations may now declare named external effects without teaching the kernel what those effects mean.

Execution receives realization-specific adapters and records each admitted call.

Verified behavior:

- a declared + admitted effect can return represented data;
- the effect call records effect name, adapter identity, argument shape, and result type;
- a declared effect without an admitted adapter fails;
- an adapter cannot be used under an effect name the operation did not declare.

**Verified:** program-foundation workflow run 26 and protocol-tests run 481 passed on commit `8598153b087dc1825439b01b7876bbb5e88b4477`.

This is explicit boundary admission/evidence. It is not Python sandboxing.

## Current edge — conditional movement

Execution is still structurally predetermined by operation order, graph edges, or recurrence feedback.

The next foundation witness is conditional relation selection:

```text
current represented evidence
      ↓ evaluate declared guard
admitted relation A / B / ...
      ↓
next realization
```

The foundation should preserve:

- which alternatives were declared;
- what represented values were inspected;
- which guard matched;
- why that relation was admitted;
- what happens when no relation or multiple incompatible relations match.

Branch conditions remain realization policy. The kernel only preserves selection structure and evidence.
