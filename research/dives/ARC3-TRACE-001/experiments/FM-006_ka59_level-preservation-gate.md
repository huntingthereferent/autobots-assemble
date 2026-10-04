# FM-006 — KA59 Level-Boundary Preservation Gate

**Type:** cross-level preservation audit  
**Status:** supported boundary correction  
**Purpose:** prevent a successful level outcome from silently certifying the model that happened to produce it.

## Official evidence

ARC Prize's analysis of Claude Opus 4.7 on KA59 reports:

- Level 1 was solved in 37 actions;
- the model's working theory of the click primitive was wrong;
- Level 2 required the real shape-matching / pushing mechanic;
- the incorrect Level 1 theory hardened into a click-fishing strategy and the run did not recover.

Source:

https://arcprize.org/blog/arc-agi-3-gpt-5-5-opus-4-7-analysis

Replay:

https://arcprize.org/replay/1dfbb619-2f6a-484a-89c8-bbe64abc977b

## A/B-relevant correction

The level result is evidence that an action sequence crossed the level boundary.

It is **not** automatically evidence that every internal relation used by the agent was correct.

Therefore:

```text
LEVEL COMPLETED
≠
WORLD MODEL PRESERVED
```

This is the ARC3 analogue of:

```text
coverage
≠
preservation
```

and:

```text
successful output
≠
proof of every parent relation
```

## Preservation gate

Before a relation learned in level `L` is allowed to orient action selection in level `L+1`, require a preservation witness.

A carried relation may be:

- `SUPPORTED_PRESERVED`
- `PREDICTED_PRESERVED`
- `PARTIAL`
- `UNKNOWN`
- `FALSIFIED`

### Minimum supported carry

A relation is eligible for `SUPPORTED_PRESERVED` only when both are recoverable:

1. **source-level support** — the relation explains/retrodicts the source transition(s) it claims to govern, not merely the final level reward;
2. **destination correspondence** — the new level contains evidence that the relevant objects/context/action relation is preserved.

Without the second condition, the relation may enter Level `L+1` only as a prediction.

## Cheap first-contact test

When a source-level relation is useful but destination preservation is unknown:

```text
source relation
+ new-level candidate correspondence
→ exact destination prediction
→ choose a low-cost discriminating action
→ preserve / falsify / partial
```

Do this **before** letting the inherited model drive a long plan.

## Why this can save actions

KA59 shows the failure shape:

```text
level reward
→ wrong primitive treated as confirmed
→ wrong model becomes planning scaffold
→ repeated actions inside bad scaffold
```

The preservation gate changes it to:

```text
level reward
→ preserve reward separately from primitive evidence
→ new level rechecks correspondence
→ one discriminating witness
→ carry only surviving relations
```

The gain is not guaranteed from one example, but the mechanism directly targets a documented ARC3 failure mode.

## Interaction with witness compression

The level-boundary gate supplies candidate relations to the selector.

For a new level:

1. collect carried relations as `PREDICTED_PRESERVED`;
2. add new-level alternatives;
3. generate exact observable predictions;
4. use the pair-separation selector;
5. choose one action that resolves as many preservation questions as possible;
6. promote only witnessed survivors.

This combines:

```text
preservation gate
+
forward match
+
witness compression
```

without changing the A/B evidence contract.

## Result

`SUPPORTED_LEVEL_BOUNDARY_PRESERVATION_GATE`

Supported claim:

> Level completion is not a sufficient witness for carrying the agent's internal mechanic/world-model relations into the next level.

## Next test

Find a replay boundary where:

- a relation is believed at the end of level `L`;
- level `L+1` initially provides multiple possible correspondences;
- a small set of early actions can distinguish preservation from failure.

Run the selector on those early actions and compare its chosen witness to the recorded agent's behavior.
