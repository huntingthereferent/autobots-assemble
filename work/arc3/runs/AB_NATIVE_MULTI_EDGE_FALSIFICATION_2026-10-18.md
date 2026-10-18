# A/B: first reproducible native multi-edge geometry counterexample

**Status: FALSIFIED** — the original five-pixel-step / only-terrain-3-or-5-passable visible glyph hypothesis was held fixed before the native test. Do not change the frozen predictions or retroactively count the failures as successes.

## Independent owner-backed evidence

- [Original official LS20 GitHub Actions native run 39120013342 — FAILURE at genuine hypothesis boundary](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39120013342). First 13 source and regression tests passed. The 64 frozen trials then completed **470 actual official native actions** from one visible root; the independent raw-pixel verifier deliberately returned nonzero after discovering three mismatches.
- [Original full raw native pixels, source-frozen predictions, actual native action record, verifier and counterexamples](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39120013342/artifacts/12133349734).
- [A second separate original native execution 39120016493](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39120016493) produced **identical decompressed artifact SHA256s and the same three mismatches**. [Repeat independent evidence](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39120016493/artifacts/12133952131).
- Frozen source model derived from independently SHA256-pinned 84 actual prior position/action transitions (27+18+39). It exhaustively predeclared **52 two-consecutive-unobserved-edge paths** and selected **12 three-consecutive-unobserved-edge paths** out of 120 mathematically possible source-geometry candidates. Trial words were frozen before native execution, without a source-model simulator substitution.

## Actual outcomes

| Native action word | Original destination predicted | Native destination witnessed | Position of failed action |
| --- | --- | --- | --- |
| 11113323 | (30,24) BLOCKED | **(30,19)** movement | second novel step |
| 11113332 | (25,19) BLOCKED | **(30,19)** movement | second novel step |
| 33311413 | (30,24) BLOCKED | **(30,19)** movement | third novel step |

All three are new source-independent native observations of the exact same 5×5 destination at row 30, column 19, reached through different action histories and from different directions. They all produced the **same complete visible frame SHA16 `94380564157962f5deb754fc81783a1d`** at depth eight. Source-known prefixes replayed exactly; there were no interruptions.

The previously collected static root-map image shows this particular 5×5 destination is **20 pixels of color 3, three pixels of color 0, two pixels of color 1**, arranged internally. The original source-backed map collision hypothesis permitted only pixels of color 3 and 5. It therefore incorrectly predicted a blocked move when the glyph entered this special patch. This is a source **counterexample to the passability predicate**, not proof that every tile carrying colors 0/1 is traversable.

- **61/64 complete words matched** (50/52 two-edge paths and 11/12 three-edge paths).
- **137/140 new individual position/action predictions were exact**; three wrong predictions are all the same target mixed-color patch.
- Critically **140/140 witnessed novel transitions** still obey the *separate* geometric displacement envelope: either no movement, or an exact five-pixel step in the direction of ACTION1(up), ACTION2(down), ACTION3(left), ACTION4(right). **126 steps moved; 14 were blocked.** The global movement-distance/direction observation remains supported by this batch even though the original traversability classifier fails.
- No novel action was silently fed back into the fixed model before execution; the saved independent verdict reports all three true counterexamples. The workflow's red scientific gate is intentional for this predeclared falsified hypothesis.

## SHA256 receipt of BOTH independent native runs

The two run artifacts unpack to byte-identical four original files:

- Frozen predicted paths JSON: `c927b7f29d39a5a15bb2c3bb587155ed709aae6e7d30c594f0c478d7399eda7b`
- Actual native manifest JSON: `7025122684ce6aff64ffc6e3f73a450d2b0b640e7f51411bb113c4deab8b9991`
- Independent verifier JSON: `b22f258076713b4909e923ab05999c3ad6db37c1f908e316c1e5f5b4572f06a3`
- Original native raw-frame NPZ: `88605dc6f7ab0dfa214e23f4ad9475281d0daa6ffc29f134686119c36706a58d`

Both actual runs are preserved as separate GitHub Actions artifacts for the 14-day retention period. This permanent research record retains the falsification and hashes after artifact expiration. The upstream REA experiment is unrelated; `main` was not modified.

## Research boundary and next admissible movement

The correct next step is to **investigate this newly observed terrain class and its effect**. A new rule may be proposed, but only as a NEW hypothesis and tested prospectively on native words not used to create it. Independently compare post-entry ACTION1/2/3/4 continuations from histories producing the same raw visible state. Preserve any changes to the native frame, completion, and potentially hidden event indications without declaring unobserved hidden-state identity or claiming an ARC solve.

The finite observation cannot establish a universal A/B law, full native Markov state, or F3 correspondence. It *does* supply a reproducible, nontrivial counterexample that the current model needs to carry forward instead of eliminating by narration.
