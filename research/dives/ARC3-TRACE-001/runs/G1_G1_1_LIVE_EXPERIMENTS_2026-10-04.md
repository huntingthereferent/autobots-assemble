# Live Solver Experiments — G1 / G1.1 — 2026-10-04

## Context

Parent witness:
`runs/FIRST_CONTACT_G0_1_2026-10-04.md`

G0.1:
- 25/25 games executed
- 2/183 levels
- 0/25 games
- 15,025 environment actions
- official aggregate score 0.0059025446738094935

The purpose of G1 was not to add architecture generally. It was a direct correction to G0.1's observed repetitive-action failure.

## G1

Generic changes:
- exact-state tried-action memory;
- coarse control-regime inference from available actions;
- ACTION7 used as explicit DFS/backtracking;
- globally balance action types instead of repeatedly selecting one action.

No game IDs or public solution paths.

Smoke set:
- VC33
- LS20
- SB26
- G50T

Budget:
200 actions/game.

Result:
```text
VC33  0 levels
LS20  0 levels
SB26  0 levels
G50T  0 levels
aggregate score 0
```

### What G1 fixed

It changed behavior qualitatively:
- G50T no longer collapsed immediately onto one action;
- it cycled through distinct available controls.

### What G1 did not fix

No outcome improvement.

Conclusion:
`BALANCED EXPLORATION != TASK INFERENCE`

## G1.1

Two additional generic hypotheses were tested:

1. **directional momentum**
   - if a directional action reaches a genuinely new state, continue that direction once before cancelling it.

2. **edit → commit**
   - in interfaces exposing click + ACTION5, if a click visibly changes state, test ACTION5 as possible commit/evaluate.

Smoke set:
- LS20
- SB26

Budget:
250 actions/game.

Result:
```text
LS20  0 levels
SB26  0 levels
aggregate score 0
```

Observed failure:
- LS20 devolved into long same-direction runs.
- SB26 initially alternated ACTION5 / ACTION6 and later repeated click blocks with ACTION5 / ACTION7 cycles.

Conclusion:
`LOCAL EFFECT PERSISTENCE != PROCEDURAL GOAL`
and
`SINGLE EDIT -> COMMIT IS TOO EAGER`

G1.1 is not promoted.

## Direct state-change probe

This probe used only observable frames and legal actions. No game source or oracle solution path was read.

### LS20

Available actions:
```text
[1,2,3,4]
```

Initial color counts:
```text
0:3
1:2
3:892
4:2609
5:439
8:12
9:45
11:84
12:10
```

One-step action signatures from reset:
```text
ACTION1  changed 52 pixels  bbox (13,40)-(38,62)
ACTION2  changed  2 pixels  bbox (13,61)-(13,62)
ACTION3  changed 52 pixels  bbox (13,45)-(38,62)
ACTION4  changed 52 pixels  bbox (13,45)-(43,62)
ACTION5  changed  0
ACTION7  changed  0
```

Interpretation:
- the directional controls do not belong to one homogeneous transition class;
- ACTION2 is visibly a different kind of operation from ACTION1/3/4;
- flattening all directional actions into one action prior loses task-relevant structure.

### SB26

Available actions:
```text
[5,6,7]
```

Initial color counts:
```text
0:20
2:80
4:3628
5:152
8:72
9:36
11:36
14:36
15:36
```

One-step action signatures from reset:
```text
ACTION5 changed 1 pixel at (63,53)
ACTION7 changed 0
```

Interpretation:
- ACTION5 primarily behaves like a tiny status/evaluation mutation from the initial state;
- it should not be promoted merely because it changes the frame;
- ACTION6 is the likely structural edit channel, but solving still requires representation of the edited structure and visible target relation.

## Old Gen-1 world-model candidate

The previously frozen Gen-1 object/world-model agent was retested because the live failures earned reopening it.

Smoke:
- LS20
- SB26
- 250 actions/game

Observed:
- LS20 collapsed onto ACTION2.
- SB26 collapsed onto ACTION5.

No level-up observed during the smoke.

Conclusion:
`OBJECT TRANSITION MEMORY + ACTION SCORING IS STILL NOT ENOUGH`

This is now a concrete solve failure, not a hypothetical architecture concern.

## Exact-state BFS probe

A source-free reset/replay BFS was started for LS20 to test whether brute-force planning over exact observable frames was sufficient.

Result:
- reset/replay reconstruction was too expensive in the live engine before reaching a useful frontier;
- exact-frame BFS is not a viable first-contact main path under the action/latency budget.

Conclusion:
`PLAN AFTER ABSTRACTION`, not `PLAN OVER RAW FRAMES`.

## Earned next layer

The next solver generation must learn a compact latent state before planning.

Required properties now supported by live evidence:

1. infer **action effect classes** from observed deltas;
2. identify stable/moving objects and relational variables;
3. distinguish structural state from tiny status/evaluation indicators;
4. represent multiple simultaneous variables when needed;
5. only then search/plan over the learned latent transition graph;
6. preserve exact pixels as a witness lens so abstraction cannot silently erase causal history.

The next implementation should not be another action-score tweak.
