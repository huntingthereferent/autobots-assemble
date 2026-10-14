# A/B mathematical chatbot — conflict-guided continuation (2026-10-12)

**Current referent:** A/B is relational language; the letters in this executable finite experiment name two *particular* transformations on 27 states. Ask whether replayed, rejected transitions can inform which already-witnessed **alternative partial relation** to examine next, without confusing a local failure with global impossibility.

## Executable behavior

The new `ConflictGuidedPortfolio` composes the **unchanged** `PostExtensionPortfolio`, `PathUnionAgent`, `BranchDiscoverer` and `UnionEdgeExtender`. It never reads the hidden finite owner law to choose a path. It starts with the existing seed ranking, fully observes one extension, and inspects that extension's replay-checked `ExcludedEdge`s. If an untried *witnessed seed* has **already admitted the same old source/action**, it prioritizes that seed for the next independently replayed extension. It only labels an alternative as admitting the formerly excluded edge **after** the second complete extension verifies that edge. The rejected state's preexisting image is retained, so a collision of pairings is not confused with a disagreement in the raw A/B step.

Two separate partial pairings can legitimately treat the same old edge differently; this does **not** mean their full state mappings can be combined. A failed search, a short path bound, an exhausted observation budget, and a selected pairing's excluded edges remain scoped results.

## Reproduction

From the extracted ZIP folder:

```bash
python run_conflict_guided_demo.py
python -m unittest -q test_ab_chatbot_conflict_guided.py
python finite_conflict_guidance.py
python -m unittest -q test_finite_conflict_guidance.py
```

Controlled local laws: original phi=(0,0,1), changed phi=(1,0,1). Goals (0,1,0) and (0,1,1). Both the original three-trial method and the guided three-trial method carry 2/2 goals with 41 admitted edges in the best selected completed trial. **There is no goal-coverage or admitted-edge improvement in this fixture**. What was added is a distinct verified capability: the next seed is selected in response to a concrete excluded transition, and the exclusion can become admitted under its *different* mathematically consistent pairing. The source-collision witness and changed assigned target image can be replayed independently against FiniteSystem, and tampered caches/source revisions invalidate the result.

The independent finite-law witness passed 4/4 focused tests. In that standalone calculation the first pairing has 27 states / 41 admitted edges, and its alternative has 24 states / 40 admitted edges, with the same checked rejected-edge admission. This is a separate deterministic witness and not the snapshot-backed observer.

The heuristic is **not guaranteed to improve** completed goals, admitted edges, efficiency or optimality. In a separate four-trial control on these same laws, the original ordering yields 42 admitted edges and this heuristic yields 41. Both must be kept as regression evidence, not hidden.

## Witness / status boundaries

- LOCAL_OWNER_VERIFIED is about the controlled code-bound local finite owner, **not** physical or external provenance.
- REMOTE_REPORTED is never upgraded to local ownership merely because transitions match.
- `UNKNOWN_VERSION`, `WALL_OBSERVATION`, and `UNKNOWN_BUDGET` withhold previous success/repair claims.
- `remaining_candidates_not_tested` means the trial cap truncated examination of a larger seed pool.
- The guided layer does not prove maximal partial conjugacy, whole-state equivalence, general linguistic competence, or material A/B.
- Historical 51-test result belongs to the preceding package; the focused and regression results of this version should be reported independently.

**Next boundary:** Learn whether counterexample-driven ordering adds new verified goal coverage for any declared finite family when measured against fixed-order search under *equal* observation and trial budgets. Only adopt it as the default when controlled comparisons support improvement.
