# ARC3 Level Preservation Gate

A level transition is a protocol boundary for game-specific relation preservation.

## Rule

```text
relation supported in level L
+ level L completed
≠
relation supported in level L+1
```

To carry the relation as supported:

```text
source support
+
destination correspondence
+
witness
→ SUPPORTED_PRESERVED
```

Otherwise carry it as `PREDICTED_PRESERVED`, `PARTIAL`, or `UNKNOWN`.

## Why

ARC Prize documents cases where an agent completed a level under an incorrect primitive/world model, then used that mistaken success as a scaffold in the next level.

Reward is therefore evidence about outcome, not automatic provenance for every relation in the model.

## Selector integration

At a new level, inherited relations become candidate models.

Use the witness-compression selector to choose a small number of actions that distinguish:

- preserved mechanic;
- changed mechanic;
- preserved primitive with changed goal/context;
- unsupported inherited theory.

A high-value action is one whose possible observed outcomes separate several of these candidates at once.

## Boundary

This gate is an operational application of evidence/preservation discipline.

It is not A/B itself and does not settle the mathematical correspondence principle.
