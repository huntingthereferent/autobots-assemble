# FM-002 — BP35 Hard-Environment Schema Transfer

**Type:** cross-environment forward-match test  
**Status:** partial transfer / supported local component  
**Purpose:** test whether the FM-001 relation shape transfers without copying LS20's game-specific magnitude or higher-level dynamics.

## Source

Official ARC Prize BP35 replay:

https://arcprize.org/replay/5a2a4b50-bb1b-4219-a268-35dee2268d28

## First-contact witness used

The official replay reasoning records:

```text
ACTION3
→ avatar moves exactly one six-pixel cell LEFT
→ facing reverses
```

Admitted local component:

```text
horizontal translation = -6 px
direction marker/facing = left
```

This is the only current-game primitive needed to localize the transferred schema.

## What FM-001 may carry forward

FM-001 supports the abstract candidate relation:

```text
ACTION3 / ACTION4
can form a directional-inverse pair
for a horizontal controllable component
```

FM-001 does **not** license:

- a 5-column step in BP35;
- LS20 object identity;
- LS20 blocking rules;
- absence of additional BP35 dynamics;
- any BP35 goal semantics.

Therefore the transferred candidate must be re-parameterized from BP35's own witness.

## Forward prediction

Given BP35's witnessed local scale of one six-pixel cell:

```text
if ACTION4 is the local inverse primitive
and the equivalent horizontal move is unblocked,

ACTION4
→ horizontal component +6 px
→ facing/direction marker reverses to the right
```

Status before a current-game witness:

`PREDICTED`

## Critical factorization

Do **not** predict the whole next frame from the horizontal primitive.

Factor the transition:

```text
ACTION
→ primitive horizontal component
+ context-coupled consequences
```

For BP35:

```text
horizontal inverse component
= forward-match candidate

additional slide / pull / collision / state consequence
= UNKNOWN until BP35 context supports it
```

This is the important result.

If we copied the entire LS20 transition shape into BP35, we would silently assert that nothing else happens after the horizontal move. The parent evidence does not support that.

## External comparison evidence

A derived public BP35 explainer based on the released game/replay material describes left/right movement as one sideways cell and indicates additional context-dependent movement behavior.

That supports the **local horizontal component** while simultaneously showing why the full composite transition cannot be inherited from LS20.

Treat this as derived/secondary validation, not as the primary witness.

## Result

`PARTIAL_TRANSFER_SUPPORTED_LOCAL_COMPONENT`

Supported carry:

```text
directional-inverse schema
+ BP35 local step scale
→ exact candidate horizontal component
```

Not yet supported carry:

```text
horizontal component
→ complete BP35 next-state prediction
```

The first unsupported relation is the mapping from the local primitive to BP35's additional context-dependent consequence.

## Why this matters

The forward matcher can save probes only if it is allowed to reuse supported relation components **without importing an entire old world model**.

So the useful representation is not:

```text
ACTION4 → next frame
```

It is:

```text
ACTION4
→ primitive effect(s)
→ gated context relations
→ composite next frame
```

Each edge keeps its own witness.

## Next seam

Represent action effects as composable evidence-bearing components.

Then ask, for each candidate action:

1. which primitive components are already forward-matchable;
2. which context gates are supported in the current state;
3. which consequences remain UNKNOWN;
4. which one live action would discriminate the unresolved gates most efficiently.
