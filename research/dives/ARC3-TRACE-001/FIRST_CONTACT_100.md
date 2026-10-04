# ARC3-100 — First-Contact Human Solver

## Primary objective

Solve novel ARC-AGI-3 environments on first contact with the behavior of a competent human:

```text
look
→ use supplied control priors
→ identify what changes
→ infer the smallest useful mechanic
→ infer goal
→ stop experimenting
→ finish
```

The target is not merely to recover an efficient path after search.

The target is to keep **discovery actions + execution actions** near the human first-run budget.

## Official control priors

ARC Prize's official action documentation supplies:

- ACTION1 — semantically mapped to up;
- ACTION2 — semantically mapped to down;
- ACTION3 — semantically mapped to left;
- ACTION4 — semantically mapped to right;
- ACTION5 — game-specific simple interaction;
- ACTION6 — coordinate click;
- ACTION7 — undo.

Therefore the solver does not waste actions rediscovering the basic directional mapping.

What remains game-specific:

- which object(s) the directional actions affect;
- movement scale and collision rules;
- secondary consequences;
- ACTION5 semantics;
- valid ACTION6 targets;
- the goal / terminal procedure.

## Direct solve hierarchy

### Phase 1 — parse before acting

Extract:

- connected components / repeated objects;
- borders, lanes, rooms, targets, counters;
- rare/salient colors;
- symmetries and repeated motifs;
- available action set;
- level/state metadata.

Do not assign semantic names unless needed.

### Phase 2 — cheapest useful grounding

Prefer an action that both:

1. advances a plausible goal or reaches new space;
2. reveals an unknown mechanic.

Directional priors make this cheaper than blind action enumeration.

### Phase 3 — infer controllable object

Use frame delta after a directional action.

Identify the component(s) whose position/shape changed consistently with the supplied direction.

Carry:

```text
action
→ affected object
→ primitive delta
→ context-conditioned side effects
```

### Phase 4 — infer objective from structure + progress

Candidate goal signals:

- level counter increments;
- reaching/covering a distinct target;
- matching repeated patterns;
- clearing/collecting rare objects;
- arranging objects into a visible template;
- satisfying a counter/resource condition;
- ACTION5/ACTION6 causing a stable progress-state transition.

Do not spend an action only to philosophically confirm the goal once one supported plan can test it while making progress.

### Phase 5 — switch from learning to execution

Once a plan has sufficient support:

```text
exploration OFF
planning/execution ON
```

This switch is mandatory for human-like efficiency.

### Phase 6 — level transition

Reuse previous-level mechanics as priors.

Only re-test when:

- a prediction fails;
- geometry/object roles materially change;
- a previously valid action becomes unavailable;
- progress stalls.

Do not automatically relearn every primitive every level.

## Memory

Maintain per game:

- action → primitive effect hypotheses;
- affected-object identity;
- collision / gate conditions;
- target/progress hypotheses;
- visited state summaries;
- failed actions at equivalent states;
- successful subplans;
- level-to-level preserved mechanics.

A remembered hypothesis carries its witness count and failure count.

## Exploration policy

Order candidate actions by:

1. supported progress toward likely goal;
2. new-state reachability;
3. ability to distinguish important live hypotheses;
4. low reset/death risk;
5. low redundancy with already witnessed effects.

The selector/witness-compression work may provide item 3, but it is subordinate to solving.

## Public-vs-hidden discipline

Public game-specific solutions/replays are for evaluation and failure analysis only.

The Competition-Mode agent must not embed:

- public game IDs → hand-coded policies;
- banked public solution action sequences;
- source-derived mechanics.

It may embed:

- official action semantics;
- generic perception;
- generic search/planning;
- generic learned priors trained from allowed public data;
- general relation/witness machinery.

## Immediate engineering target

Create one Kaggle-starter-compatible `MyAgent` that:

- uses only current/previous frames and allowed metadata;
- has no per-game branch;
- exploits the official direction priors;
- grounds ACTION5/6 locally;
- stores a compact state/action graph;
- switches from exploration to execution when progress-producing structure is found;
- logs enough state to audit why actions were chosen.

Then run:

```text
make play-local
```

on the full public set and measure:

- games solved;
- levels solved;
- total first-contact actions;
- per-game RHAE including the actual run's discovery actions.
