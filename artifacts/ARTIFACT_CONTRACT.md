# Artifact Contract

## Purpose

Provide one cross-layer contract for outputs created during complete-stack traversal.

Programming output, CAD-like output, system diagrams, math models, schematics, and physical measurement packages are different representations under the same outer artifact relation.

## Minimum record

```text
artifact
├─ id
├─ referent
├─ boundary
├─ representation_type
├─ inputs
│  ├─ witnessed
│  └─ assumed / placeholder
├─ parameters
├─ interfaces
├─ outputs
├─ witness_depth
├─ provenance
└─ invalidation / replacement conditions
```

## Rule: representation must expose what downstream work needs

Do not add detail because a drawing, diagram, or codebase looks more professional with it.

Add structure when another relation requires it.

Examples:

- a mounting relation requires hole positions and tolerances;
- a thermal relation requires material, area, thickness, heat input, and boundary conditions;
- an electrical relation requires voltage/current/power/interface behavior;
- a program relation requires input/output/state/effect contracts.

## Rule: placeholders remain visible

A placeholder is admissible when it preserves enough interface structure for valid continuation.

Every placeholder must state:

1. what real thing it stands for;
2. which properties are evidenced;
3. which properties are assumed;
4. acceptable uncertainty/range where known;
5. what consumes it;
6. what physical/real evidence must replace it;
7. which downstream artifacts must be revisited when replacement occurs.

## Rule: derived values keep lineage

A derived value should point back to the artifact inputs that produced it.

```text
motor torque requirement
← wheel radius
← target acceleration
← vehicle mass estimate
← CAD/BOM mass model
```

Changing the CAD/BOM mass model should therefore expose the torque result as stale/recomputable rather than silently preserving the old number.

## Rule: an artifact can be evidence without being final evidence

A CAD assembly is evidence that geometry and interfaces were represented.

It is not evidence that the assembly was fabricated.

A simulation is evidence that the represented model produced a behavior under declared assumptions.

It is not evidence that the real system behaves identically.

Preserve both usefulness and boundary.
