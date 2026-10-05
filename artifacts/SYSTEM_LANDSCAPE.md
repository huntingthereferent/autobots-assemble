# System Landscape Artifact

## Definition

A system landscape is the **relational map of the current referent**.

It shows what exists, what depends on what, what crosses boundaries, and where evidence or placeholders currently sit.

It is not merely an architecture picture.

## Production mechanism

The default implementation path is defined in [LANDSCAPE_TOOLCHAIN.md](LANDSCAPE_TOOLCHAIN.md).

Use a machine-readable graph source, normally **Graphviz/DOT**, as the canonical artifact. SVG/PDF/PNG diagrams are generated views. This keeps nodes, relations, feedback loops, placeholders, and artifact references traversable rather than trapping them in an image.

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

## Diagram categories by emphasized relation

Use the smallest diagram that preserves the relation currently needed.

The sibling question is:

> **Which relation must this landscape emphasize?**

- **boundary** → context landscape;
- **composition** → system decomposition;
- **dependency** → dependency graph;
- **interface** → interface map;
- **flow** → flow diagram;
- **spatial placement** → packaging diagram;
- **evidence state** → evidence landscape.

Each branch can be decomposed again. For example, a flow diagram may next distinguish energy, material, information, heat, force, or another actually reached flow relation.

An evidence landscape may overlay:

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
