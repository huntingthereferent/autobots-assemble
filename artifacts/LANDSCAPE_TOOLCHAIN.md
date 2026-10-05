# System Landscape Production Toolchain

## Purpose

Define how relational/system diagrams are actually produced.

The canonical landscape is a machine-readable graph with named nodes and labeled relations. Rendered diagrams are generated views of that graph.

## Default toolchain

**Primary:** Graphviz / DOT

Use for:
- context landscapes;
- decomposition graphs;
- dependency graphs;
- interface maps;
- flow diagrams;
- evidence-state overlays.

The graph source is canonical.

Generated SVG/PDF/PNG files are views of the graph.

## Canonical production path

```text
current referent
→ identified nodes/referents
→ named relations
→ graph source
→ rendered SVG/PDF/PNG
→ structural checks
→ downstream traversal
```

## Required graph evidence

Each node should identify a referent.

Each edge should carry a relation label whenever the relation matters.

Example:

```text
battery
  -- supplies DC power -->
inverter

inverter
  -- drives 3-phase current -->
motor

motor
  -- applies torque -->
reduction
```

## Structural checks

When useful, validate:

- orphan nodes;
- missing relation labels;
- cycles/feedback loops;
- required interfaces;
- dependency reachability;
- unknown/placeholder nodes;
- stale downstream dependents.

## Cross-artifact relation

Landscape source may point to artifact IDs.

Example:

```text
motor_mount
  -- represented spatially by --> ART-0042 CAD-like
  -- sized by --> ART-0039 math-model
  -- connected electrically by --> ART-0045 schematic
```

The landscape is therefore a navigation surface over the stack, not a substitute for the referenced artifacts.
