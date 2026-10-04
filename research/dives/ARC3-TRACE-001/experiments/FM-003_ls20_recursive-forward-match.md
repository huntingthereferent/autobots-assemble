# FM-003 — LS20 Same-Environment Recursive Forward Match

**Type:** within-environment translated-context calibration  
**Status:** supported recursive forward match  
**Purpose:** test whether a witnessed action/effect can be carried forward through a supported translated context and then recursively reused without changing the evidence contract.

## Source

Official ARC Prize LS20 replay:

https://arcprize.org/replay/8314341d-c2e5-4b75-af8a-a085eddd8165

## Source witness

The replay reasoning records:

```text
ACTION3
slider cols 34–38
→ slider cols 29–33
```

So the admitted local primitive is:

```text
same game
same slider
ACTION3
horizontal translation Δx = -5 columns
```

## Correspondence used

Do not use a cross-game action-name correspondence.

Use a same-environment translated-context correspondence:

```text
C0:
slider at 34–38
same horizontal track
next-left region open

R = translate controllable slider/context one 5-column step left

C1:
slider at 29–33
same horizontal track
next-left region open
```

The correspondence is about the same object in the same track under a translated local context.

## Forward prediction 1

From the witnessed relation:

```text
C0 + ACTION3 → C1
```

and the supported translated context:

```text
C0 --R--> C1
```

predict:

```text
C1 + ACTION3
→ C2
→ slider 24–28
```

Status before later replay evidence:

`PREDICTED`

## Recursive forward prediction 2

If C2 preserves the same track/context conditions, the predicted output is itself admissible to the same forward-match contract:

```text
C2 + ACTION3
→ C3
→ slider 19–23
```

No new action semantics, operator, or future-position schedule is introduced.

The continuation is earned from the same local relation plus the next translated context.

## Withheld replay witness

The official replay timeline shows three consecutive Move Left decisions after the slider had been returned to cols 34–38.

Later replay reasoning records the slider at cols 19–23 and confirms the left/right control scheme.

That endpoint is exactly consistent with:

```text
34–38
--ACTION3--> 29–33
--ACTION3--> 24–28
--ACTION3--> 19–23
```

## Result

`SUPPORTED_SAME_ENV_RECURSIVE_FORWARD_MATCH`

This is stronger than FM-001 for the recursion question:

- the source transition is witnessed;
- the next context is related by a local translation in the same environment;
- the predicted output can re-enter the same contract;
- the same primitive relation is reused without importing a new game mapping.

## What this does NOT prove

It does not prove:

- that ACTION3 has the same meaning in another ARC3 environment;
- that the track remains open indefinitely;
- that the relation survives a level boundary;
- that the higher-level game goal has been inferred;
- that general A/B correspondence has been mathematically justified.

A blocker or changed local geometry would create a new context gate.

## Efficiency result

The experiment validates **prediction reuse**, not direct action removal.

If the task requires physically moving the slider through those positions, the actions still have to be executed.

The speed value appears when the same mechanism is queried in multiple corresponding contexts: the agent does not need to spend additional actions merely to relearn the primitive at each translated state.

## Next seam — witness compression

Find a state with multiple unresolved corresponding contexts.

Then use one action whose outcome can resolve several candidate context gates simultaneously.

Target metric:

```text
relations resolved / environment action
```

rather than simply actions guessed correctly.
