# Finite A/B chatbot — bounded backtracked goal extension

**Date:** 2026-10-12
**Question:** When two greedy priorities miss a goal, can the existing mathematical chatbot discover a compatible rooted path through bounded branching, preserve its witnessed pairing, and investigate additional A/B edges without sacrificing the goal?

**Representation boundary:** A and B in this code denote two specified finite transformations on 27 states. A/B as language for noticing and continuing relationships is not defined by these programs.

## Integrated behavior

The new `BacktrackedGoalExtender` reuses three existing components, in this order:

1. `BranchDiscoverer`: enumerates consistent path prefixes to declared depth; retains replayable separating equality witnesses on rejected branches.
2. `PathUnionAgent`: selects an admitted jointly compatible path subset, preserving alternate candidate histories.
3. `UnionEdgeExtender`: checks missing edges from the joined path pairing; it can exclude edges while retaining a witnessed rooted goal.

No action word, mapped coordinate, or pairing is supplied to the constructor. Both owners' pinned source edges are observed and cached, and each `advance()` call has a limit on *new* edge reads across its stages. All stages are replay-audited on continuation. An incomplete observation budget is not treated as unreachable; stale versions or tampered caches block claimed success; remote origin is not promoted to local owner witness.

## Reproducible finite result

Original `phi=(0,0,1)`; changed `phi=(1,0,1)`; root `(0,0,0)`; requested source goal `(1,1,2)`; max path depth 6.

- Independent fixed-priority calculation: neither of the previous `AB`-first and `BA`-first extensions includes the requested source goal.
- Bounded path search discovers `ABBBBB` (old end `(1,1,2)`, changed end `(1,1,1)`) and other compatible candidate paths.
- After selecting a consistent path union, the existing extender obtains 27 paired states, 42 admitted labeled edges, and 12 excluded labeled edges under the **selected** pairing.
- Because of those 12 exclusions, the result **does not** establish full A/B conjugacy across the 27 states. The 27 paired states alone are not closure.

The independent GitHub sidecar reproduces the word witness and 27/42/12 counts, but does **not** implement origin-aware pinned HTTP observations or the full language bridge.

## Tests (local, 2026-10-12)

```
python -m unittest -q test_ab_chatbot_backtracked_extension.py
python -m unittest -q test_ab_chatbot_alternative_extension.py
```

A module-by-module run of **all 22 local test modules completed: 330/330 passed.** The new layer contributes 9 focused tests; 321/321 tests are existing earlier modules, including the previous alternative-extension layer. See `REGRESSION_BACKTRACK_2026-10-12.txt` for per-module counts. This is local execution, not GitHub Actions.

The committed GitHub standalone experiment is at `work/arc_like_maze/chatbot/bounded_backtracked_goal.py` with `test_bounded_backtracked_goal.py`, research report, and folder README in commit `a7b9db94172c06779e2192c2ec256279c45e595b`.

## Exact scope and next movement

This version can find a *path-compatible* goal witness beyond two fixed greedy extensions, then grow **one selected pairing**. It does not search every possible maximal partial correspondence, prove finite completeness outside its bounds, infer general natural language, or prove a physical couplesense mechanism. A selected branch can exclude transitions that an alternate pairing would allow.

**Next:** compare multiple separately completed path-seeded extensions and their incompatible target mappings using the same replay contract; choose according to explicitly declared goal coverage and edge evidence, without treating selection as uniqueness.
