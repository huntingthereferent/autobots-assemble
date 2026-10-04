# FM-002 — BP35 Cross-Environment Transfer Attempt

**Type:** cross-environment correspondence test  
**Status:** PARTIAL — directional semantic prior supplied, effect correspondence still local  
**Purpose:** test how much of FM-001 may legitimately transfer from LS20 into BP35.

## Source

Official ARC Prize BP35 replay:

https://arcprize.org/replay/5a2a4b50-bb1b-4219-a268-35dee2268d28

Official action semantics:

https://docs.arcprize.org/actions

## Current-environment witness

The BP35 replay reasoning records:

```text
ACTION3
→ avatar moves exactly one six-pixel cell LEFT
→ facing reverses
```

## Correction to the earlier correction

ARC Prize's official docs explicitly state:

```text
ACTION1 → semantically mapped to up
ACTION2 → semantically mapped to down
ACTION3 → semantically mapped to left
ACTION4 → semantically mapped to right
```

Therefore it was too strict to say ACTION3/ACTION4 carry no cross-game semantics.

The supported cross-game prior is directional:

```text
ACTION3 = leftward semantic
ACTION4 = rightward semantic
```

## What still does NOT transfer automatically

The official directional mapping does not establish:

- which object is controlled;
- movement magnitude;
- whether movement is blocked;
- side effects such as facing, pulling, sliding, rotation, or collision;
- whether ACTION3/ACTION4 are exact state inverses in the current context;
- any goal relation.

Thus:

```text
shared directional semantic
!=
shared transition function
```

## Result

`PARTIAL_DIRECTIONAL_SEMANTIC_TRANSFER`

Supported carry:

```text
ACTION3 is a left-directed control prior
ACTION4 is a right-directed control prior
```

Still game-local:

```text
affected object
step size
collision/context gate
composite consequence
goal relevance
```

## Operational consequence

A first-contact solver should not waste actions rediscovering the basic ACTION1–4 direction mapping.

It should use those supplied semantics to choose cheap directional probes and infer only the game-specific consequence.

This narrows the uncertainty surface substantially.
