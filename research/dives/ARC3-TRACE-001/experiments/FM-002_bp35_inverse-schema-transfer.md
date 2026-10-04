# FM-002 — BP35 Cross-Environment Transfer Attempt

**Type:** cross-environment correspondence test  
**Status:** WALL — missing cross-environment action-semantic correspondence  
**Purpose:** test whether FM-001 can legitimately transfer an inverse-action relation from LS20 into BP35.

## Source

Official ARC Prize BP35 replay:

https://arcprize.org/replay/5a2a4b50-bb1b-4219-a268-35dee2268d28

## Current-environment witness

The BP35 replay reasoning records a local transition:

```text
ACTION3
→ avatar moves exactly one six-pixel cell LEFT
→ facing reverses
```

This independently supports a BP35-local relation between ACTION3 and a leftward primitive component.

## Proposed carry from FM-001

FM-001 established, inside LS20, that an ACTION3 leftward slider movement was followed by an ACTION4 inverse rightward movement.

The tempting transfer was:

```text
LS20: ACTION3 ↔ ACTION4 directional inverse
                  ↓
BP35: ACTION3 ↔ ACTION4 directional inverse ?
```

## Correction

That transfer is **not admitted**.

ARC3 standardizes the action identifiers, but game-specific semantics still require a witness. The fact that both environments expose symbols named ACTION3 and ACTION4 does not itself support a relation saying those symbols carry the same directional semantics across games.

The missing parent relation is:

```text
LS20 ACTION3/ACTION4 semantic pair
        CORRESPONDS TO
BP35 ACTION3/ACTION4 semantic pair
```

No witness currently earns that correspondence merely from interface identity.

Therefore:

```text
same action ID
≠ same semantic relation
```

## What BP35 evidence can establish

BP35's own ACTION3 witness may be admitted locally:

```text
BP35 ACTION3
→ horizontal translation -6 px
→ facing left
```

Independent BP35 evidence may later establish ACTION4 locally as the inverse. If so, that would demonstrate that the same abstract relation family occurs in both games.

But it would **not** retroactively mean the LS20 relation predicted BP35 before BP35-local evidence.

## Result

`WALL_MISSING_CROSS_ENV_ACTION_CORRESPONDENCE`

This replaces the earlier `PARTIAL_TRANSFER_SUPPORTED_LOCAL_COMPONENT` interpretation.

The earlier record was too permissive because it treated standardized action IDs as if they supplied semantic correspondence.

## Preserved useful result

The factorization insight survives:

```text
ACTION
→ primitive effect(s)
→ context gates
→ composite consequence
```

But every transferred edge still needs a correspondence witness.

## Forward-match rule after correction

### Within one environment

A witnessed action effect may be projected into another **supported corresponding context** using the same action identity, because the action belongs to the same game semantics and only the context correspondence must be earned.

### Across environments

Do not transfer raw action IDs as semantics.

Cross-environment reuse may carry:

- representation shape;
- relation classes;
- candidate generation procedure;
- witness contract;
- action-selection strategy.

It may not carry a game-specific action mapping until the new environment earns that mapping.

## Next seam

Use forward matching first **within an environment**:

```text
same witnessed action
+ supported corresponding local context
→ candidate effect in new context
```

For cross-environment work, locally ground the action/effect relation first, then compare the abstract relation structures afterward.
