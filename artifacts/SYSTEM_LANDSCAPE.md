# System Landscape Artifact

## Definition

A system landscape is the **relational map of the current referent**.

It shows what exists, what depends on what, what crosses boundaries, and where evidence or placeholders currently sit.

It is not merely an architecture picture.

## What the landscape must preserve

When present, distinguish:

- system boundary;
- subsystems;
- components;
- external actors/systems;
- material flows;
- energy flows;
- data/signal flows;
- control flows;
- mechanical interfaces;
- electrical interfaces;
- spatial interfaces;
- constraints;
- feedback loops;
- evidence sources;
- placeholders / unknowns;
- walls;
- downstream dependents.

## Diagram families

Use the smallest diagram that preserves the relation currently needed.

### 1. Context landscape

Shows the referent and external systems/boundaries.

### 2. System decomposition

Shows system → subsystem → component structure.

### 3. Dependency graph

Shows what values/artifacts depend on what others.

Useful for propagation and invalidation.

### 4. Interface map

Shows connections/contracts between components or layers.

### 5. Flow diagram

Shows movement of energy, material, information, money, heat, force, etc.

### 6. Spatial/packaging diagram

Shows rough placement and geometric constraints before or alongside CAD.

### 7. Evidence landscape

Overlays witness state:

```text
[MEASURED] wheel radius
     ↓
[MODELED] wheel torque
     ↓
[PLACEHOLDER] motor map
     ↓
[DESIGNED] inverter requirement
     ↓
[UNKNOWN] real thermal behavior
```

## Diagram syntax

Every node should identify a referent, not just a department/category.

Every edge should mean something.

Prefer labeled relations:

```text
battery
  -- supplies DC power -->
inverter

inverter
  -- drives 3-phase current -->
motor

motor
  -- applies torque -->
gear reduction
```

Avoid unlabeled boxes connected by lines when the relation itself matters.

## Landscape and CAD relation

Landscape answers:

> What is connected and why?

CAD-like representation answers:

> Where is it, what geometry does it have, and how does it physically fit/connect?

They should cross-reference rather than duplicate one another.

## Landscape and math relation

A diagram edge may open a quantitative relation.

Example:

```text
vehicle
 -- requires acceleration force -->
wheel-ground interface
```

opens:

```text
F_required =
    m*a
  + rolling resistance
  + aerodynamic drag
  + grade force
```

The equation/model becomes its own artifact and feeds the landscape edge with quantified evidence.
