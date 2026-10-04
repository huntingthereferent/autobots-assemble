# FM-001 — LS20 Inverse-Action Calibration

**Type:** retrospective time-split calibration  
**Status:** supported calibration  
**Purpose:** test whether one witnessed transition can support an exact forward prediction before a later replay frame is unsealed.

## Source

Official ARC Prize replay:

https://arcprize.org/replay/8314341d-c2e5-4b75-af8a-a085eddd8165

## Evidence split

Treat the replay as time-split evidence.

The calibration boundary is placed immediately after the first witnessed horizontal movement.

### Admitted before prediction

The replay reasoning records a local transition in which:

```text
ACTION3
→ 12-block slider moves LEFT
→ columns 34–38 become 29–33
```

Observed primitive delta:

```text
Δx = -5 columns
```

No later ACTION4 effect is admitted yet.

## Forward candidate

Parent evidence:

1. same controllable slider;
2. same local state/context;
3. ACTION3 produced a horizontal translation;
4. ACTION4 is another available action in the same local interaction surface.

Candidate correspondence:

```text
ACTION3 : leftward horizontal primitive
ACTION4 : candidate inverse horizontal primitive
```

This is a **candidate correspondence**, not an admitted semantic rule.

### Prediction recorded before unseal

If ACTION4 is the inverse primitive under the same unblocked slider context:

```text
ACTION4
→ Δx = +5 columns
→ slider 29–33 becomes 34–38
```

### Falsification conditions

The forward candidate is falsified if ACTION4:

- moves a different object;
- moves vertically;
- moves horizontally by a non-inverse magnitude;
- leaves the slider fixed despite equivalent unblocked context;
- produces a non-inverse horizontal direction.

## Withheld witness

Later official replay reasoning records:

```text
ACTION4
→ slider moves RIGHT
→ columns 29–33 become 34–38
```

The withheld witness matches the predicted inverse delta exactly as described in the replay.

## Result

`SUPPORTED_FORWARD_MATCH_CALIBRATION`

The first witnessed transition generated a falsifiable prediction that survived the withheld later transition.

## Efficiency interpretation

This does **not** mean ACTION4 can always be removed from a successful plan.

It means ACTION4 need not necessarily be spent merely to **discover** whether it is the inverse primitive. If the action is needed for goal progress, it still must be executed.

So the counterfactual gain is:

```text
primitive-discovery probes potentially avoided: 1
task-required actions avoided: not claimed
```

## Recursive output

The supported relation may re-enter the same contract as:

```text
directional_inverse_schema(
  source_action = ACTION3,
  candidate_inverse = ACTION4,
  component = horizontal_translation,
  scale = local-context parameter
)
```

The magnitude `5` is local evidence. It is **not** part of the transferable schema unless another context independently supports the same scale.
