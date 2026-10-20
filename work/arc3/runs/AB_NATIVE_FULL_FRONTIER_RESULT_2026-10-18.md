# A/B native LS20 — complete known-reachable geometry frontier

Recorded October 18, 2026. Actual native experiment, not a source-model simulation, REA implementation, hidden-state/F3 identification, or ARC game completion.

## Falsifiable rule frozen before experiment

Source PR #99 commits 3f81fdb63ae3f1a7f5f4c61f3373b1f6de95b8c0 and 85028c521834d761a06ebf1819c047dcf19a5fca fix the source, test selection and GitHub workflow BEFORE execution.

The existing visible glyph/map hypothesis remains unchanged: a full 5x5 glyph footprint is shifted 5 pixels by ACTION1/2/3/4, upward/downward/leftward/rightward, respectively. A destination consisting entirely of original visible colors 3 and/or 5 is passable. Any destination containing a wall or another color is blocked. A missing destination beyond the map boundary blocks movement.

Before making new observations, the freezer validates the SHA-256-pinned original 27-edge training artifact and separately validates every raw frame/action of the last independently observed 18-edge experiment. Exactly 45 recorded source edges and 21 presently reachable glyph positions are retained. All 45 reproduce the unchanged geometry function.

It then *exhaustively* takes every as-yet-unmeasured action from every vertex reachable using ONLY those independently confirmed source edges. This identifies 39 distinct unknown (glyph-position, action) pairs, rather than a convenient handpicked sample. Expected outcomes: 28 movements, 11 blocked moves. Raw destination categories: 28 all-color-3 patches, eight all-color-4 walls, two mixed 3/4/5 patches, and one mixed 5/9 patch.

Every unknown edge is tested twice: (a) via the shortest measured prefix to its starting position; (b) after three independently recorded ACTION1/ACTION2 return loops, then the same known prefix. The second route adds six actions and changes time/history while returning the glyph to the same observed starting position. Both outcome predictions are frozen in the same pre-native artifact. Overall 78 predeclared native LS20 action words, lengths 3–13. The collector does not score the prediction; a different module verifies original native pixels and all intermediate known movements.

## Native independent result — PASS

- [GitHub Actions run 39101728758 — SUCCESS](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39101728758).
- [Four original evidence records: frozen predictions, complete native manifest, raw 64x64 pixel arrays and independent verdict](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39101728758/artifacts/12127120433). GitHub Actions artifact retained for 14 days.
- 13/13 regression/source-boundary tests passed.
- **78/78 exact native geometry outcomes passed**: 39/39 direct routes and 39/39 delayed histories.
- **39/39 direct/delayed pairs agreed** at the same glyph-position/action pair.
- 28/28 moving and 11/11 blocked cases were correct under BOTH histories.
- Every one of the 78 previously known prefixes was replayed exactly. No interrupted native trajectories.
- **638 actual native LS20 actions**, across separately reset trajectories sharing one native root.
- Longest tested route 13 actions.

Particularly important boundary predictions (native word -> predicted and observed end position):
- 1111111: at upper glyph position (15,34), moving upward enters mixed native 5/9 terrain and was BLOCKED; remains (15,34).
- 1111113: from (15,34), left destination contains 3/4/5 and was BLOCKED; remains (15,34).
- 1111114: from (15,34), right destination contains 3/4/5 and was BLOCKED; remains (15,34).

These are explicit boundary/terrain counterexample opportunities, not post-hoc exclusions.

## Actual source SHA-256 receipts

- Frozen forecast JSON: 566344fddadc42a4b39de3ae64aa8522ba5873ad22e5390ed30429d1f5be9dae.
- Original native manifest JSON: 01336fcf72873596c23c411352711f76b09afd202b77e32cc412230cc7632bd9.
- Complete raw native NPZ frames: 022a5f41cc034297d99139b50da953c35686b1c2f2e5ad1f69e1622bd3393152.
- Independent verdict JSON: ccee061e5dbf1fad1f9d517b4d0ad18755f3e521391346a45ca516f6567f5fe0.

## Precise scope of the result

The tested map rule predicted all **currently source-reachable unmeasured edges**, and the same visible glyph positions persisted across two tested action histories for each edge. This is strong finite **visible geometry** evidence, but it does not establish total underlying LS20 game state, all native maps and tiles, action reversibility in hidden state, a general F3/world correspondence, an ARC solve, or that any path of arbitrary length is Markov-complete in glyph coordinates.

The next real test can admit these independently verified new edges, expand the reachable graph, and predeclare **multi-step routes that contain TWO or more transitions absent from the previous training graph**. Such a test would go beyond a known path plus one unknown step, without rewriting the successful geometry rule.
