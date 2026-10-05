# Architecture — Complete Stack

The architecture exists to preserve movement through a problem's **entire required dependency stack**.

It separates four things that were previously easy to blur:

1. **Referent** — the problem currently being solved.
2. **Capability** — a broad problem-space already demonstrated or being expanded.
3. **Dependency layer** — any field/system the current problem actually requires.
4. **Realization depth** — how far evidence has moved from representation toward observed operation.

```text
REAL PROBLEM / REFERENT
        ↓
COMPLETE-STACK TRAVERSAL
        ↓
required layers as actually reached
        ↓
represent / model / simulate / design / build / measure / inspect / validate
        ↓
evidence + provenance
        ↓
FOUNDATION
        ↓
capability / read-only views
```

## A/B boundary

A/B remains the recursively reusable mathematical operation and witness/evidence contract.

This architecture is not A/B. It is a repository organization that preserves repeated applications and their evidence.

## Capability layer

A capability is a broad space in which unlike concrete problems can increasingly be carried through their required stacks.

Capabilities are not résumé labels and are not isolated disciplines.

The first broad proof, **Programs**, is frozen in [capabilities/README.md](capabilities/README.md).

## Dependency layers

Dependency layers are open-ended and entered only when the current referent requires them.

Examples include mathematics, software, physics, chemistry, biology, electronics, controls, mechanics, materials, fabrication, manufacturing, economics, safety, regulation, supply chain, and human factors.

No layer is privileged.

## Realization depth

Keep reached depth explicit:

```text
unknown
→ researched
→ represented
→ modeled
→ simulated
→ designed
→ implemented
→ physically built
→ measured
→ inspected
→ externally validated
→ deployed / operating
```

This is not a mandatory linear lifecycle.

The invariant is:

```text
represented ≠ physically present
simulated ≠ built
built ≠ measured
tested ≠ deployed
```

## Placeholders

A missing physical relation may be represented by a bounded digital placeholder when the interface is known well enough to continue valid surrounding work.

The placeholder must preserve what is measured or sourced, what is assumed, what downstream layers consume, what evidence is still missing, and what must be rerun when the real witness arrives.

A placeholder never upgrades itself into a physical witness.

## Goal lanes

Research, open source, and paid work answer **why** the work exists rather than defining the technical stack.

- `research/`
- `open_source/`
- `money/` and `jobs/`

The same complete-stack capability may be exercised in any of them.

## Work and Foundation

Concrete work remains where it belongs. Foundation preserves what that work actually demonstrated.

```text
work item
→ evidence / witness
→ Foundation record
→ capability projection
```

Capability/read-only outputs may summarize Foundation. They may not manufacture evidence.

## Language and views

`language/` handles interpretation/rendering of human expression.

`views/` and generated outputs handle read-only projections.

The old generic `lenses/` layer is removed because those responsibilities are already represented by these more specific layers.

## Core invariant

**Do not stop traversal because the next required relation belongs to another discipline.**

A movement stops only at a supported result, an explicit bounded placeholder that preserves continuation, or a recorded wall.
