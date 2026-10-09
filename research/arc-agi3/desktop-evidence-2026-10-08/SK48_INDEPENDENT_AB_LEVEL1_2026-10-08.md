# SK48 — Native A/B independent Level 1 and state quotient

Date: 2026-10-08

## New independently searched movement

A bounded breadth-first search on the real local SK48 environment, using only the public 64x64 frame, level-completion status, and native direction actions 1,2,3,4, reached the next level in 14 actions. It did not read the saved route or inspect private game structures while choosing the sequence.

New route:
`1,1,1,4,4,4,4,3,2,2,4,3,1,4`

Earlier separately saved route:
`4,4,4,1,1,1,4,3,2,2,4,3,1,4`

The two are different histories reaching the same witnessed Level 1 completion. This is an environment-forked *local search*: using `copy.deepcopy` of game instances to explore hypothetical continuations is not yet a deployable public-observation-only ARC competition policy. The solver found a native level-completing branch at depth 14; no shorter solution was found in its exhaustive public-frame-deduplicated breadth-first search through depth 13 under the four-direction action set.

Evidence: `_tmp_sk48_public_bfs_frontier.py`.

## A/B on competing prefixes

The two routes share the seven-action suffix `3,2,2,4,3,1,4`.

The preceding seven actions each have 3 upward (ACTION1) and 4 rightward (ACTION4) moves. Every one of the 35 possible permutations was executed on an actual local SDK clone from the same initial environment. Results:

- 35 histories collapse to 4 distinct public-frame states after seven moves.
- The four classes have 20, 10, 4, 1 histories.
- The classes are perfectly determined in this family by the trailing count of consecutive upward actions: 0, 1, 2, or 3.
- Appending the common seven-action suffix completes Level 1 for exactly the 20 histories with zero trailing upward actions. The other 15 remain at Level 1.
- Thus a quotient of 35 histories to four public states predicts this tested continuation, without requiring the full seven-action history.

Evidence: `_tmp_sk48_level1_public_ab_permutations.py`, `sk48_level1_public_ab_permutations.json`.

## Immediate continuation closure

For each of the 35 histories, the next action 1,2,3,4,7 was tested separately. Within all four public-frame classes, each action's native next-frame and level/state continuation was identical. No class needed an additional history relation at this one-step horizon.

Evidence: `_tmp_sk48_public_horizon1_undo.py`, `sk48_level1_public_horizon1_undo.json`.

## Held-out family correction

The trailing-up rule was then tested against five other balanced or unbalanced action multisets:

| Up actions | Right actions | Histories | Public classes | Trailing-up sufficient? |
|---:|---:|---:|---:|:---|
| 2 | 4 | 15 | 3 | Yes |
| 4 | 4 | 70 | 5 | Yes |
| 4 | 5 | 126 | 5 | No |
| 3 | 3 | 20 | 1 | No (over-distinguishes) |
| 2 | 5 | 21 | 3 | No |

The history rule is not a universal SK48 state function. In some held-out families, distinct trailing counts share the same frame; in others, a fixed trailing count spans different visible frames.

For all 126 histories with four upward and five rightward actions, A/B again tested each native next action 1,2,3,4,7. Within each of the five public-frame equivalence classes, all five next-action observations agreed. No one-step history-dependent counterexample appeared despite the failure of the simpler history descriptor.

Current promoted relation for these local families: **public-frame continuation-equivalence classes**, not trailing-up-count classes. Longer rollback horizons and unrelated movement families remain untested; no global Markov conclusion is warranted.

Evidence: `_tmp_sk48_trailing_up_heldout.py`, `sk48_level1_trailing_up_heldout.json`, `_tmp_sk48_heldout_public_alias_continuation.py`, `sk48_heldout_public_alias_continuation.json`.

## Boundary

- Local SK48 previously replayed 8/8 in 280 actions with public click coordinates and 13 native switch witnesses.
- This continuation independently discovers a **different Level 1** route, not a complete fresh independent eight-level solver.
- Planning uses local game forking and cannot yet run as a competition policy operating solely on one live agent observation stream.
- A/B is preserved as the operation; the candidate 4-state compression is evidence-local and deliberately corrected by held-out counterexamples.
- No new GitHub merge or official ARC competition submission has occurred.

Next native edge: test longer undo histories for apparent public aliases, and implement action choice without `copy.deepcopy` access.
