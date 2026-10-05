# Math Model Artifact

## Definition

A math-model artifact is the **explicit quantitative relation created when traversal reaches a dependency that must be calculated, constrained, estimated, optimized, or compared**.

Math should arise from the relation being traversed rather than being added as decoration.

## Required structure when relevant

- quantity / relation being resolved;
- symbols and units;
- governing equation(s);
- source of each input;
- witnessed vs assumed values;
- valid range / boundary conditions;
- calculation or solver;
- resulting value/range;
- uncertainty/sensitivity where material;
- downstream consumers;
- invalidation conditions.

## Example

```text
referent: required wheel force

F_required =
    m*a
  + C_rr*m*g
  + 0.5*rho*C_d*A*v^2
  + m*g*sin(theta)

inputs:
  m       ← CAD/BOM mass estimate
  a       ← performance requirement
  C_rr    ← tire/road assumption
  rho     ← environmental condition
  C_d     ← aerodynamic model/placeholder
  A       ← CAD frontal area
  v       ← speed requirement
  theta   ← grade requirement

output:
  F_required

downstream:
  wheel torque
  motor sizing
  inverter current
  battery power
  thermal load
```

If the CAD mass changes, this artifact becomes stale and must be recomputed.

## Evidence boundary

An equation can be mathematically valid while its physical inputs remain placeholders.

The artifact must preserve both:
- mathematical correctness under its declared model;
- empirical status of the model inputs.

Do not convert modeled certainty into physical certainty.
