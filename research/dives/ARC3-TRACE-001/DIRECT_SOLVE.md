# ARC3 Direct Solve — Human-Level 100% Target

**Status:** active objective  
**Primary referent:** solve ARC-AGI-3, not study the tracing machinery.

## Definition of solved

ARC Prize defines a 100% ARC-AGI-3 score as beating every environment at or above the human action-efficiency baseline.

So the target is:

```text
novel environment
→ infer controls
→ infer mechanics
→ infer goal
→ solve all levels
→ do so within human-efficient action budgets
```

The benchmark is human-solvable by design. Every environment has been solved by at least two independent human participants under first-run conditions.

## Operating rule

Use the simplest thing that gets the game solved.

A/B, forward matching, witness compression, world models, planning, search, coding, replay analysis, symmetry, object tracking, or any other machinery may be used underneath.

None of them are the goal.

Do not stop to prove a mechanism if the game can simply be solved.

## Human-shaped solve loop

For each new environment:

1. **Look before acting.**
   Identify objects, repeated motifs, boundaries, counters, obvious controllable elements, and available actions.

2. **Ground controls cheaply.**
   Use the fewest safe actions needed to identify what the controls do.

3. **Track consequences, not stories.**
   Record concrete changes in the board/state. Avoid committing to a theme or semantic explanation too early.

4. **Infer the likely objective.**
   Prefer visible completion cues, progress changes, object alignment, collection, escape, matching, ordering, or transformation evidence.

5. **Plan to finish.**
   Once mechanics and objective are clear enough, stop exploring and execute the shortest supported plan.

6. **Carry only what survives levels.**
   Assume useful continuity, but verify changed mechanics quickly when a new level contradicts the current model.

7. **Correct immediately.**
   When a prediction fails, update the model instead of defending it.

This loop is deliberately ordinary. Humans do not need to formalize every relation before playing well.

## Efficiency

Exploration is part of the score.

Therefore:

- prefer observations that answer several questions at once;
- avoid repeating already-known control effects;
- do not spend actions proving something that is already sufficient for planning;
- once the goal is evident, switch from learning to execution;
- use resets only when the expected recovery cost is lower than continuing.

## Development boundary

### Public/demo games

We can use the public game set and released human replays to:

- understand failure modes;
- measure action efficiency;
- test solver logic;
- compare against human baselines.

A replay-assisted solution is useful engineering evidence but is **not** evidence of first-contact generalization.

### Hidden/private evaluation

The real 100% claim requires the competition evaluator.

Private environments, mechanics, and win conditions are intentionally unavailable during development.

Therefore:

```text
public 100%
≠
private 100%
```

until the official evaluator witnesses it.

## Existing ARC3 trace work

The existing FM-001 through FM-006 work remains useful as supporting evidence.

Its role is now subordinate:

- use forward matching when it saves actions;
- use witness compression when several hypotheses are live;
- use preservation gates when a level transition creates uncertainty;
- otherwise just solve the game.

Do not let methodology block progress toward the win state.

## Immediate target

Build/test the direct solver against the public ARC3 environments with the explicit success criterion:

```text
WIN every public environment
AND
measure score against human action baselines
```

Then package the same solver for Competition Mode without game-specific public solutions embedded in it.
