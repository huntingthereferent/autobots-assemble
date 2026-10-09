# ar25 A/B Solve Evidence

## Status
Verified completion: 2 / 8 levels.

## Witness contract
Referent is the complete returned game board/state. Permitted movement is the game action interface. A derived feature may guide the next recursion only while its provenance to the whole returned board remains explicit. Missing evidence returns a boundary; it does not authorize an invented correspondence.

## Level 1 positive witness
Fresh-start closure sequence:
`3 x5, 2 x10`

The closing transition is structurally distinct from simple boundary consumption. Positive transition included 24 cells of navy -> yellow (`11 -> 4`) together with the paired-side rewrite. Returned Level 2 board is the next evidence-bearing input.

## Level 2 completion referent
At Level 2 entry the obvious carrier correspondence was already present, so geometric matching alone was not the goal. Subsequent returned boards exposed a completion-bearing counterpart exchange.

A downward crossing from the B8 returned state produced an 8-cell `11 -> 4` exchange. One outward relation could increase the temporary exchange to 16 cells, but further outward applications did not increase it. Ordinary vertical continuation reversed the exchange.

Action 5 at the 8-cell crossing was the first witnessed continuation that preserved the exchanged cells in the returned whole board instead of immediately reversing them. This produced the held-exchange referent.

Factoring 136 distinct whole returned boards by the exact eight exchanged coordinates yielded only two completion-relevant outcomes:
- all 8 remain yellow: held
- all 8 return navy: restored
No partial mixtures occurred.

Recursion was then restricted to whole returned states that preserved the held exchange. This is not a replacement of the board by an 8-cell abstraction: the full board remained the recursive state, while preservation of the witnessed exchange determined whether the completion-bearing relation survived.

## Level 2 positive witness
Exact fresh-start sequence through Level 2:
`3,3,3,3,3, 2,2,2,2,2,2,2,2,2,2, 7,5, 2,2,2,2,2, 5,3,5, 2,2,2, 5,3`

Compact:
`3x5 -> 2x10 -> 7 -> 5 -> 2x5 -> 5 -> 3 -> 5 -> 2x3 -> 5 -> 3`

The final action 3 raises `levels_completed` from 1 to 2.

The successful closure was found after 315 witnessed continuations in the held-exchange recursion.

## Important falsified alternatives
- bottom-boundary contact alone
- raw changed-cell count (including 105-cell Level 2 transitions)
- literal registration of the 72-cell counterpart components
- independent Cartesian x/y translation
- 45-cell carrier count
- arbitrary `11 -> 4` exchange
- increasing exchange magnitude to 24 by repeated outward movement
- undifferentiated breadth expansion of every visually distinct board

## Carry into Level 3
The exact board returned by the final Level 2 completion action is the Level 3 input. Do not replay a Level 2 semantic label onto it. Preserve the provenance chain and derive the next movement from the returned whole state.

## Mathematical reground at Level 3

Do not carry the Level-2 feature as the Level-3 operator. The Level-2 closure returns a new complete board, and that returned object is already a valid next input.

Let W be the unchanged witness contract:
- x is the complete returned environment state/board;
- R(x) is the set of permitted game interactions available at x;
- closure evidence is the returned environment state, especially levels_completed;
- provenance is the exact chain of returned states/interactions.

The recursive kernel remains:

```
x[n+1] = AB_W(x[n])
```

For ARC, an executed candidate relation is witnessed as:

```
(x[n], permitted action a, returned x[n+1])
```

The board may expose features, correspondences, or invariants, but these are evidence *about x*; they are not substituted for x unless a correspondence map is itself earned under W.

At the Level-2 -> Level-3 boundary:
- x0(L3) := exact whole state returned by the Level-2 closing action.
- Previous held 8-cell exchange remains provenance explaining the prior closure, not an orientation rule for x0(L3).
- Apply permitted relations directly to x0(L3).
- Exact equality of returned whole states may establish an equivalence of those witnessed returns.
- Changed-pixel counts, components, colors, and labels are diagnostics only.
- No semantic gate is inserted between a valid return and the next AB_W call.

This is the recursion/no-interposition test in operational form, not a new definition of A/B.


### Level 3 rare-departure recursion
- Dominant A5-varying class after removing witnessed 11->12 preservation: (((0, 9), 7), ((9, 0), 6)).
- Exact reconstructed frontier supplied 47 dominant whole-state parents.
- Their simple-action continuations produced 49 rare departure edges collapsing to 49 exact rare returned whole states.
- Recursed through 100 witnessed continuations from those rare whole states; no closure if this note is present.
- 88 exact non-dominant returned whole states survived that block. Whole board remained recursion referent; A5 signature was diagnostic only.


### Level 3 promoted action-relation algebra
The previous A5 support/count partition was swallowed after it exposed a higher relation. The recursive object at this layer is the action-word relation on exact returned whole boards, not another partition of pixel/count features.

Across the same 55 witnessed Level-3 whole states:

Exact two-action transformation equalities:
- 1,2 = 2,1
- 1,3 = 3,1
- 1,4 = 4,1
- 2,3 = 3,2
- 2,4 = 4,2
- 3,4 = 4,3
- 1,7 = 2,7
- 3,7 = 4,7
- 5,7 = 7,5

Thus actions {1,2,3,4} form a witnessed commuting block at this frontier. Action 5 does not commute with any of 1,2,3,4 on any of the 55 tested whole states. Action 5 and action 7 commute on all 55.

Action 7 coequalizes two preceding pairs:
- 1,7 and 2,7 return the same exact whole board on all 55 witnesses.
- 3,7 and 4,7 return the same exact whole board on all 55 witnesses.

Because these are exact returned-state equalities, any common suffix preserves them automatically. They are rewrite relations on action histories; they do not make 1/2 or 3/4 globally interchangeable as future actions.

Left-context recursion test:
- 1,3 = 3,1 survived all six one-action prefixes over all 55 states: 0 failures.
- 1,4 = 4,1 survived all six prefixes: 0 failures.
- 2,3 = 3,2 survived all six prefixes: 0 failures.
- 2,4 = 4,2 survived all six prefixes: 0 failures.
- 5,7 = 7,5 survived all six prefixes: 0 failures.
- 1,2 = 2,1 had exactly one left-context failure: prefix 2 from source history (2,2,2).
- 3,4 = 4,3 had exactly one left-context failure: prefix 4 from source history (5,5,4).
- 1,7 = 2,7 has the same single boundary as 1,2 = 2,1: prefix 2 from (2,2,2).
- 3,7 = 4,7 has the same single boundary as 3,4 = 4,3: prefix 4 from (5,5,4).

At those two boundaries, repeating the boundary action restores equality:
- the 1/2 split at (2,2,2) closes again under another 2;
- the 3/4 split at (5,5,4) closes again under another 4.

Current higher-level shape:
- stable commuting relations: (1,3), (1,4), (2,3), (2,4), (5,7)
- paired boundary relations: (1,2) and (3,4)
- 7 preserves/coequalizes the same paired distinction
- the pair boundary is recursive: one exceptional left split, then the same boundary member closes it again

No Level-3 closure was observed during these relation-algebra tests. Whole returned boards remain the witness referent.

### Level 3 shared-boundary return

The two prior exceptional boundary states were recursed as whole returned states rather than treated as separate exceptions.

Exact convergence:
`(2,2,2,1,1) = (5,5,4,5,7,2)`

This is exact whole-board equality. The common returned board became the next recursion input.

From that shared root:
- action 3 is an exact identity;
- action 4 is an exact identity;
- action 2 is exactly equal to the composite `1,7,7`;
- `1,2 = 2,1`;
- `1,7 = 2,7 = 7,1`;
- `3,7 = 4,7 = 7,3 = 7,4`;
- `5,7 = 7,5`.

Breadth-first recursion to depth 6 from the shared whole state:
- 3996 witnessed action edges;
- 1914 distinct whole returned states;
- no Level-3 closure;
- exactly two returns to the shared root, by one-step words `3` and `4`.

Thus at the shared root, 3 and 4 are not merely equivalent: each is the identity on the whole returned state.

A reduced-generator recursion over {1,5,7} to depth 10 produced:
- 2550 witnessed edges;
- 1279 distinct whole returned states;
- no Level-3 closure;
- no returns to the shared root.

Transport test of the new exact relations:
- `2 = 1,7,7` holds at the shared root, but fails after one-step prefixes 2 and 5.
- `3 = e` and `4 = e` hold at the shared root and after one-step prefixes 1,2,3,4,7, but fail after prefix 5.
- At prefix depth 2, every failure of the identity behavior of 3/4 lies in histories containing an activating 5 in the tested position.
- Action 5 therefore marks the principal boundary where dormant 3/4 behavior becomes active again; action 2 is an additional boundary for the specific `2 = 177` relation.

Whole returned boards remain the referent; these word relations are witnessed equalities at the stated contexts, not globally assumed rewrite rules.

### Level 3 five-phase transport

Continuing from the shared exact root `22211 = 554572`, action 5 exposes a transported relation regime.

Along the exact whole-state sequence generated by repeated action 5, every sampled board was distinct. Nevertheless the relation signature repeated with period 3 through at least 18 consecutive 5-actions.

At powers 5^(3k):
- action 3 is identity on the whole state;
- action 4 is identity on the whole state;
- 3 = 4;
- 2 = 1,7,7;
- 3,4 does not equal 1,2;
- 7 does not collapse all of 1,2,3,4.

At powers 5^(3k+1) and 5^(3k+2):
- actions 3 and 4 are distinct and non-identity;
- 3,4 = 4,3 = 1,2 = 2,1;
- 1,7 = 2,7 = 3,7 = 4,7;
- 2 != 1,7,7.

Thus action 5 advances a relation-phase with period 3 while the exact whole boards continue changing. This is not a board cycle.

Two additional witnessed hybrid signatures occur under other actions:
A = dormant 3/4 with 2=177.
B = dormant 3/4 with 2!=177.
C = active 3/4 with 2!=177.
D = active 3/4 with 2=177.

On the four representative whole states:
A: 1->A, 2->B, 3->A, 4->A, 5->C, 7->A.
B: 1->A, 2->B, 3->B, 4->B, 5->C, 7->A.
C: 1->D, 2->C, 3->C, 4->C, 5->C, 7->C.
D: 1->D, 2->C, 3->C, 4->C, 5->C, 7->C.

This four-state table is currently representative evidence only; it is not yet promoted to a global quotient until transition determinism is checked across multiple exact whole-state witnesses in each signature class.

### Correction: visible-board equality is not full environment-state equality

A later congruence test exposed that several relations previously described as exact whole-state equalities were established only by comparing rendered frame bytes.

The AR25 implementation carries additional mutable environment state that is not necessarily encoded in the rendered frame. Relevant examples include:
- `flqblmrxsla`: an undo/history stack consumed by action 7;
- `yvifanjrcyu`: the currently selected object, advanced by action 5;
- `qehjebksqcm`, `xukxeewuexo`, and other control flags/counters.

Source inspection confirms:
- action 7 pops an entry from `flqblmrxsla` and restores that stored positional state;
- actions 1-4 push snapshots when actual movement occurs;
- action 5 changes the selected object and control state.

Therefore equal rendered frames are observational collisions, not automatically equal environment states.

Critical recheck of the previously claimed Level-3 shared return:
- `22211` and `554572` return identical rendered frames.
- After `22211`: selected index 0, undo depth 5, qeh=False.
- After `554572`: selected index 0, undo depth 1, qeh=True.
- Actions 1,2,3,4,5 still return equal rendered next frames in the immediate one-step test, while preserving the internal differences.
- Action 7 immediately returns different rendered boards.

Thus `22211 = 554572` must be withdrawn as a full-state equality. The supported statement is:

`frame(22211) = frame(554572)`

with distinct internal environment states above that common observation.

Likewise, relations such as `2 = 177` at the rendered-frame level require reclassification unless their internal state coordinates also agree. One direct check already found equal rendered frames for histories `2`, `177`, and `727` while their undo depths differ.

The next recursion must therefore preserve the complete environment state, not only `frame[0].tobytes()`. The visible board remains evidence, but is a projection of the actual recursive state.


### AR25 closure after full-state correction

The A/B/C/D relation-signature quotient was useful as an observational projection, but it is not a full environment-state quotient. Its two transition breaks (A/B under action 7 and C under action 5) were symptoms of omitted state.

The omitted coordinates are concrete:
- rendered board is only a projection;
- reflector positions are active state;
- payload positions and pixel orientation are active state;
- selection, undo/history, and control flags are active state.

A true full-state convergence was witnessed between the two earlier boundary branches:
- branch 1: `22211 + 77775`
- branch 2: `554572 + 5`

At that convergence the full state key agrees, and every immediate action in {1,2,3,4,5,7} produces the same next full key.

From there, solving the remaining levels by the actual reflection geometry closes AR25:

- Level 3: horizontal reflector y=9; L payload at (11,14); cap payload at (3,14). 26/26 targets.
- Level 4: horizontal reflector y=9; wide payload at (11,6); vertical payload may be represented at the reflected-equivalent placement (13,3)/(13,10). 24/24 targets.
- Level 5: vertical reflector x=8; horizontal reflector y=9; single payload at (4,5). 23/23 targets.
- Level 6: vertical reflector x=6; horizontal reflector y=11; payloads at (2,12) and (7,15). 52/52 targets.
- Level 7: vertical reflector x=12; horizontal reflector y=7; payloads at (7,7) and the reflected-equivalent placement (8,1)/(8,10). 42/42 targets.
- Level 8: vertical reflector x=12; horizontal reflector y=11; payloads at (4,6) and (16,3). 60/60 targets.

The target renderer generates the orbit of payload cells under the available reflector axes and clips the orbit to the 21x21 board. This explains why Level 7's visible target set is not itself globally reflection-symmetric even though its generating geometry is: part of the reflected orbit lies outside the board.

A reproducible witnessed action decomposition for the complete 8-level solve is:

```python
SOL = [3]*5 + [2]*10 + [7,5] + [2]*5 + [5,3,5] + [2]*3 + [5,3]

L3A = [5,5,4,5,7,2,5,2,2,2,2,3,5] + [1]*8 + [3]*4 + [5] + [1]*8
L3B = [5] + [4]*8 + [2]*3 + [5] + [3]*8 + [2]*13

L4 = [2]*6 + [5] + [4]*7 + [5] + [4]*7

L5 = [2]*4 + [5] + [4]*5 + [5] + [3]*10 + [1]*7

L6 = [2]*11 + [5,3,5] + [3]*15 + [2]*4 + [5] + [3]*7 + [2]*12

L7 = [2]*2 + [5] + [4]*9 + [5] + [3]*10 + [1]*6 + [5] + [4]*3 + [1]*6

L8 = [2]*6 + [5] + [4]*9 + [5] + [3]*9 + [1]*7 + [5] + [4]*9 + [1]*4

FULL = SOL + L3A + L3B + L4 + L5 + L6 + L7 + L8
```

Executing `FULL` from a fresh `ar25` environment returns:
- `levels_completed = 8`
- `state = WIN`
- 287 witnessed actions

This witness is not claimed minimal.

Promotion result:
The four-state A/B/C/D quotient should not be promoted as the game-state automaton. It is a valid coarse relation-signature projection only. The promoted state description must retain the reflector axes and payload geometry (plus the engine's hidden control/history state where transition identity matters). Under that richer state, the apparent quotient breaks disappear into ordinary deterministic geometry.


### Promotion completed: geometry state is operationally sufficient

The richer state description was promoted by building an end-to-end solver that starts from a fresh AR25 environment and does not use any hardcoded per-level solution sequence.

State used by the solver:
- target-cell set;
- reflector axes that exist on the level;
- whether each reflector is movable or fixed;
- reflector coordinates;
- payload pixel geometry;
- payload coordinates;
- current selection only for compiling geometry into actions.

Completion semantics:
The game does not require equality between the rendered orbit and the target set. It requires every target cell to be occupied. Extra reflected cells outside the target are allowed. Therefore the solver searches for target coverage under the reflection orbit, not rendered-board equality.

For a payload cell p=(x,y), the generated orbit is formed by the available involutions:
- vertical reflection: (x,y) -> (2*a-x,y)
- horizontal reflection: (x,y) -> (x,2*b-y)

With both reflectors present, the closure contains up to four points:
p,
Rv(p),
Rh(p),
Rv(Rh(p)).

The orbit is clipped to the board. This clipping explains levels whose visible target set is not itself globally symmetric.

The solver:
1. reads the target set and current level objects;
2. distinguishes fixed reflector axes from movable reflector axes;
3. enumerates admissible axis coordinates only for movable reflectors;
4. enumerates payload translations;
5. computes reflected target-coverage masks;
6. chooses a minimum-movement covering configuration;
7. compiles the chosen geometry into action-5 selection changes plus actions 1/2/3/4 translations;
8. stops a movement plan immediately when the engine advances the level, preventing stale-object movement across level boundaries;
9. repeats from the newly returned level state.

Fresh-environment result:
- Level 1: inferred fixed x-axis 10, payload (1,15), 15 actions.
- Level 2: inferred movable x-axis 10, payload (15,14), 11 additional actions.
- Level 3: inferred horizontal axis y=9, payloads (11,14), (3,14).
- Level 4: inferred horizontal axis y=9, payloads (11,6), (13,10).
- Level 5: inferred axes x=8, y=9, payload (4,5).
- Level 6: inferred axes x=6, y=11, payloads (2,12), (7,15).
- Level 7: inferred axes x=12, y=7, payloads (15,1), (8,10). These are reflected-equivalent representatives of the previously witnessed closure.
- Level 8: inferred axes x=12, y=11, payloads (4,6), (16,3).

Execution result from fresh environment:
- levels_completed = 8
- state = WIN
- actions = 268

This improves the earlier hand witness of 287 actions and the first geometry-assisted witness of 272 actions. No global action-count optimality is claimed.

The decisive promotion criterion is therefore satisfied:
the retained geometry state is sufficient not only to classify the observed boards but to regenerate valid actions that solve all eight levels from the initial environment.

The A/B/C/D signatures remain useful observational summaries, but they are not the recursive state kernel for AR25.


### One layer up: engine-independent reflection-orbit kernel

The AR25 solution can be separated from the AR25 implementation.

Let a payload be a finite set S subset Z^2 and let t be its translation.
For a vertical axis a and horizontal axis b define involutions

Rv(x,y) = (2a-x, y)
Rh(x,y) = (x, 2b-y)

When an axis is absent, its involution is omitted. The generated support of one
payload is the board-clipped orbit

clip_B( <Rv,Rh> · (S+t) ).

For several payloads S_i+t_i, the visible generated support is the union of
their clipped orbits.

The completion predicate witnessed in AR25 is coverage, not equality:

T subseteq union_i clip_B( G · (S_i+t_i) ).

Extra generated cells are allowed. This distinction matters.

Actions then live one layer below the geometry:
- actions 1/2/3/4 translate the currently selected movable parameter;
- action 5 changes which parameter is selected;
- action 7 restores a prior engine state.

The promoted geometric kernel does not require action 7 to solve AR25. Undo is
part of the engine transition state, but not part of the minimal target-cover
description used by the fresh end-to-end solver.

A generic implementation of the geometry itself is now stored in:
`reflection_orbit_kernel.py`

This file contains no AR25 engine identifiers. AR25 is evidence that one game
can be translated into this kernel; the current local scan does not establish
that other ARC environments use the same reflector mechanism.


### Promotion above reflection: causal operator discovery

A stronger end-to-end result now supersedes the tag-aware geometry solver.

Static target geometry alone is not sufficient to identify the generating operator.
Counterexample:
- Levels 1-2 admit multiple legal affine involutions that cover the same target.
- Some accidental transformations produce fewer extra cells than the actual game operator.
Therefore target symmetry or minimum static description is not a sufficient witness.

The missing evidence is intervention.

Black-box action probes recover object roles from response dimensionality:
- a 1-D object responding only along x or y is a latent control parameter;
- a 2-D object responding along x and y is a source/payload;
- a fixed operator can still be inferred from opposite source/dependent motion even when the operator itself cannot be moved.

Level-2 causal measurements:
- moving the x-control by +1 moves the dependent copy by +2 while the direct source stays fixed;
- moving the source by +1 moves the direct copy by +1 and the dependent copy by -1.

Thus finite differences recover:
dq/da = 2
dq/dp = -1

and integration gives:
q = 2a - p + c.

For Level 2, c=0.
For Level 1, the fixed-operator probe gives:
q = -p + 20,
so the fixed axis is 10.

Level 5 independently recovers the same relation in x and y. At an automatically selected high-visibility intervention state, four clean copies appear. The discovered x and y controls commute observationally.

The promoted state language is therefore:

controls -> causal affine relations -> commuting operators -> generated orbit -> target coverage

rather than:

recognize reflection -> solve reflection puzzle.

A fresh-run causal-family solver was then built with the following procedure:

1. Level 1:
   - probe the only movable source;
   - infer the fixed relation q=-p+c;
   - recover fixed axis c/2;
   - infer and execute the minimum-movement covering placement.

2. Level 2:
   - discover one x-only control and one 2-D source from action responses;
   - probe source and control;
   - infer q=-p+2a+c;
   - verify the learned reflection signature;
   - infer and execute the minimum-movement covering configuration.

3. Levels 3-8:
   - do not rediscover the semantic label "reflection";
   - classify current objects only by action-response dimensionality;
   - transfer the learned affine operator family to the discovered x/y control dimensions;
   - solve target coverage over legal control coordinates and legal source translations;
   - execute the generated plan with level-boundary guards.

Fresh-environment result:
- all eight level goals were independently re-inferred;
- final levels_completed = 8;
- final state = WIN;
- no AR25 reflector tags were used to assign operator/source semantics;
- no per-level solution geometry was hardcoded after learning the operator family.

Key evidence files:
- causal_affine_kernel.py
- causal_operator_model.py
- causal_generator_promotion.py
- ar25_causal_operator_probe.py
- l1_fixed_operator_causal_probe.py
- l5_discover_latent_controls.py
- l5_causal_jacobian.py
- test_l5_discovered_operator_commutation.py
- ar25_causal_learn_then_act_l1_l2.py
- ar25_transfer_learned_operator_l3.py
- ar25_causal_family_full_solver.py

This is the current promoted edge.

The remaining unresolved layer is more general:
Can the same intervention-first machinery discover a non-reflection operator family in another environment without predeclaring the affine hypothesis class?
