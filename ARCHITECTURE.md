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
working artifacts
(program / CAD-like / landscape / math / schematic / BOM / test)
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

## Category discipline

All categorization follows [CATEGORY_CONTRACT.md](CATEGORY_CONTRACT.md).

At any one level, siblings must answer the same relational question. Dependency layer, artifact type, witness depth, goal lane, capability, and view are separate axes; they must not be flattened into one category list.

A child category remains a valid referent and can be decomposed again by the same rule.

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

## Company layer

`companies/` contains persistent operating organizations.

A company is a durable referent, not a goal lane or product. It may span operations, products/services, work/projects, people, assets, finance, compliance, and external relations while preserving each layer's own evidence boundary.

A repo company record does not imply legal incorporation, accreditation, licensure, or regulatory approval; those states require explicit evidence.

## Goal lanes

Research, open source, and paid work answer **why** the work exists rather than defining the technical stack.

- `research/`
- `open_source/`
- `money/` and `jobs/`

The same complete-stack capability may be exercised in any of them.

## Artifact layer

Traversal emits working artifacts when a relation needs an inspectable representation.

Artifacts are not presentation-only views. They can be revised, calculated from, simulated, tested, and consumed by downstream artifacts.

See [artifacts/README.md](artifacts/README.md).

`views/` remains read-only presentation. `artifacts/` carries working represented structure.

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
