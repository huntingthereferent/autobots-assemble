# Artifacts

Artifacts are **working representations produced by complete-stack traversal**.

They are not read-only views.

An artifact exists so a relation that has been traversed can be made inspectable, checked, handed to another layer, revised, and used as input to later movement.

```text
referent
  → traverse relation
  → produce artifact
  → inspect / calculate / simulate / build / test
  → artifact output becomes input elsewhere
```

## Same layer, different representation

These are sibling artifact families:

- **program** — executable/computational representation;
- **CAD-like geometry** — spatial/physical representation;
- **system landscape** — relational/topological representation;
- **math model** — quantitative relation representation;
- **schematic** — connectivity/functional representation;
- **BOM / composition model** — parts/material composition representation;
- **test / measurement artifact** — witness-producing representation.

No family is automatically more real than another.

Its evidence strength is determined by what it actually witnesses.

```text
code written ≠ code tested
CAD geometry ≠ fabricated part
system diagram ≠ operating system
equation ≠ measured behavior
BOM ≠ assembled product
simulation ≠ physical measurement
```

## Common artifact contract

Every artifact should preserve enough of the following to remain usable downstream:

- **referent** — what this artifact represents;
- **boundary** — what is inside and outside it;
- **inputs** — evidence, assumptions, measurements, or upstream artifacts used;
- **representation** — the form used to preserve the relation;
- **parameters** — explicit values that can change;
- **interfaces** — what other artifacts/layers may consume;
- **outputs** — values, geometry, behavior, or structure produced;
- **assumptions / placeholders** — anything not physically or externally witnessed;
- **witness depth** — represented / modeled / simulated / implemented / built / measured / etc.;
- **provenance** — where inputs and decisions came from;
- **invalidators** — what new evidence would require recomputation or redesign.

The exact fields vary by artifact family, but the distinctions must survive.

## Artifacts are recursive inputs

A produced artifact is not an endpoint.

Examples:

```text
CAD geometry
→ volume
→ estimated mass
→ vehicle mass model
→ suspension load
→ spring selection
→ packaging update
→ CAD geometry revision
```

```text
system landscape
→ exposed interface
→ control requirement
→ program artifact
→ timing measurement
→ control-system update
```

```text
math model
→ required torque
→ motor candidate
→ electrical load
→ battery model
→ thermal load
→ cooling geometry
```

This is why artifacts belong inside traversal rather than after it.

## Views are different

`views/` may render, summarize, filter, or present artifacts/evidence.

A view is read-only.

An artifact can change what later movement is valid because it carries represented structure and may produce new derived evidence.
