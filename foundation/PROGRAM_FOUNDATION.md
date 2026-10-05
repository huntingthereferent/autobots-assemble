# Program Foundation

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
