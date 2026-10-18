# LS20 — Predicting real native movement from witnessed geometry

**Research date:** October 17, 2026, America/Chicago (GitHub logs in UTC October 18). **Evidence:** Official native ARC-AGI-3 LS20, not an imitation, saved winning route, or hidden benchmark run.

## Source and independent replay

- [Initial prediction / negative control — run #39089328325](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39089328325), [raw frames and report](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39089328325/artifacts/12121793483)
- [Geometry correction and held-out native validation — run #39089550992](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39089550992), [raw frames and per-step predictions](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39089550992/artifacts/12122365688)
- [First native predictor](../native_factor_prediction.py), [geometry-corrected predictor](../native_factor_geometry.py)
- [Earlier source evidence](LS20_F3_NATIVE_RELATIONS_2026-10-17.md), [native suffix and exact F3 obstruction](LS20_F3_SUFFIX_2026-10-17.md)

These native artifact files expire after GitHub's 14-day configured retention. Committed scripts and recorded conclusions retain a reproducible path; they do not mean the code has been exercised on unknown games.

## Predeclared visible factors and predictions

From earlier real native observations, the model first identifies a mobile glyph as **15 exact native color-9 pixels + 10 exact native color-12 pixels**, calibrating the source coordinates with **one native ACTION3 step from a fresh reset**. It leaves the other native colors unchanged.

The initially admitted prediction was a five-pixel translation for directional controls, with ACTION2 blocked at the initial lower boundary, plus a separate two-cell trace changing native color 11 to 3 on each environment action in successive columns from x=13, rows y=61 and 62.

The predictor **constructs its expected full 64×64 frame before each native action**, then records the actual observed frame hash, complete pixel mismatch count, glyph-mask match, trace-mask match, and counterexample coordinates. A mismatch is not silently repaired during that trajectory.

## First falsification

Eight mixed native action words contained 34 actions. The original unrestricted translation rule matched **28/34 complete native frames** and **28/34 glyph masks**, but correctly predicted the trace on **34/34**. Specific counterexamples:

- The word 3214, ACTION1 after a prior ACTION3/ACTION2 context: predicted upward-moving glyph pixels would occupy native wall-colored cells near x=29..33, y=40. Native frame retained those wall pixels and the attempted movement was blocked.
- The word 113422, ACTION3 after two upward moves: predicted left translation intruded into wall-colored cells around x=29..33, y=35; native movement was blocked.

These six total pixel-prediction failures were *evidence against* assuming free movement across static obstacles, not a deficiency in F3 algebra.

## Independently specified geometry correction

Before rerunning any native game, the next executable model was written with one correction: create a static native background by removing the calibrated moving glyph and restoring its original locations to native color 3. Before any move, if the predicted destination glyph overlaps a static pixel other than native background color 3, **block that move**. Retain the separately observed ACTION2 lower-root boundary. Regardless of blocked glyph movement, advance the two-cell native progress trace.

No F3 arithmetic is performed on grid colors, geometry coordinates, or action IDs.

The old eight words were retested. **Eight additional, predeclared, previously untested mixed sequences** formed a held-out validation set:

| Group | Native actions | Exact full-frame predictions | Exact glyph-mask predictions | Exact trace-mask predictions | Complete words |
| --- | ---: | ---: | ---: | ---: | ---: |
| Previously failed/tested words | 34 | 34/34 | 34/34 | 34/34 | 8/8 |
| New mixed words | 35 | **35/35** | **35/35** | **35/35** | **8/8** |
| Total | 69 | **69/69** | **69/69** | **69/69** | **16/16** |

The held-out native words were 1312, 3114, 1432, 112233, 1324, 3311, 4112, and 22114. They were specified in the code before running this evaluation. The native source reset produced the same initial frame for each game trajectory. A separate, independently counted native calibration ACTION3 preceded both evaluation groups. The scripts record both model versions and all actual frame arrays.

## Mathematical boundary and next investigation

This is an **observed exact local transition model for these native LS20 paths**, not a proof of a general ARC game engine or a score-winning policy. No new LS20 level was completed.

The repository's original F3 A/B transformations and nine family members are unchanged. The measured native model is not presently an F3³ transition system: the native 2-cell trace is history-dependent and visibly irreversible over these observations, and native blocking also defeats literal invertibility. Previous native A³ and suffix-convergence counterexamples are still in force.

The supported next mathematical question is whether there exists a **nontrivial, source-witnessed native-to-F3 correspondence on some explicitly identified factor or subdomain** that both preserves the tested transitions *and* predicts an independent, unseen equality/inequality of native action words. Do not impose modulo-three coordinates to make the equations true. The current observation model is a concrete input to that test, not its proof.

**Current status:** native local mechanics predicted, no proven F3 correspondence, no ARC win. Existing single-file F3 agent is not rewritten to claim these results as a successful competition solver.
