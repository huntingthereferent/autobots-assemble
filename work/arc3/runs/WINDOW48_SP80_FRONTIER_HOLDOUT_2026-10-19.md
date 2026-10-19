# SP80 — pre-action native bottom-row frontier holdout

October 19, 2026. One new official public native ARC3/SP80 experiment, not a source F3 or solver claim.

## Frozen prediction and independent original game run

From native original-game 11-step counterexample [#159](WINDOW48_SP80_EXTENDED_HISTORY_2026-10-19.md), predeclare the observable **row 63 frontier**, rather than refitting an absolute action-step clock:

1. In the ACTUAL stage-1 **pre-action frame**, choose the first native row-63 pixel whose value is nonzero, `x_frontier`. Prediction is admitted only if this pixel is native color 14, with all preceding row pixels native 0. Predict its `14 → 0` change at the next original ACTION4 or ACTION5.
2. The *stronger row claim* is that all changed native row-63 pixels are a contiguous `14 → 0` block starting at that pre-action frontier, with **width exactly 1 or 2**. Never read the after-frame to form the prediction.
3. Preserve frozen original geometry/occupancy stage-transfer baseline, previous nine-step spatial/timing candidate (already falsified at eleven steps), separate original step-clock row predictor, and negative-control identity geometry. Report all extra, missed and wrong native color transitions, and independently inspect every frame/step.
4. Do not count interrupted stages, withdrawn native controls, absent frame stacks, or stage-changing actions as negative observations. Do not manufacture missing samples.

Five fixed new 13-action original-game words, two independently reset stage0 and genuine stage1 histories each:

- `4444444444444` (ACTION4-heavy)
- `5555555555555` (ACTION5-only control)
- `4455454544454`
- `5544554455445`
- `4544545545454`

[Official native GitHub Actions run #39207477345](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39207477345) — successful executable native workflow, *not automatically a scientific success*. The workflow's separate synthetic unit negative controls passed, but are not counted as original native evidence.

**Original evidence:** [artifact #12165583665](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39207477345/artifacts/12165583665), native JSON and `npz` unmodified frame stacks; retention 14 days. Downloaded ZIP SHA256 independently matched GitHub original digest: `13852c6292bfae0110f1128ee39490c17c2894a7e792c5fbbf43c98f1766616e`.

## Exact observations (source-owned bounded result)

- **246 actual original native actions** across **20 fresh real game resets**.
- **98 admitted** genuine stage-1 ACTION4/ACTION5 steps with observed original before and after frames and unchanged native level 1.
- Of those: 58 ACTION4 and 40 ACTION5.
- The **pre-action first native 14→0 pixel prediction was observed on all 98/98** admissible steps. All 98 also had the complete row-63 contiguous 1-or-2-pixel advance: 58 one-cell, 40 two-cell advances.
- The prior frozen **absolute step-clock row predictor matched exactly only 66/98** admissible row effects. Failure was not confined to one action ID.
- These counts were independently reproduced from the original NPZ pre/post row arrays and retained JSON, with zero disagreement against the source-owned reported frontier measurements.

**Limits of admission:** The five words x two reset-pairs x 13 context steps would offer 130 possible stage-1 actions if complete. **32 did not yield admissible stage-1 after-frames** and remain UNKNOWN (8 each in two ACTION5-only runs, 4 each in two `5544554455445` runs, 3 each in two `4544545545454` runs, 1 each in two `4455454544454` runs). Original stage0 histories also lack 12 otherwise-possible paired ACTION4 effects following level changes; do not count these as complete stage transfer.

### Full stage0 → stage1 native ACTION4 comparisons

Only **46 matched original ACTION4 paired effects per geometric model**. This is a different and narrower denominator than 98 stage-1 boundary observations.

| Frozen native effect transfer model | Exact effects | Extra changes | Misses | Wrong native colors |
| --- | ---: | ---: | ---: | ---: |
| Translation+occupancy baseline | 30/46 | 74 | 6 | 0 |
| Translation + old spatial/timing condition | 38/46 | 6 | 4 | 0 |
| Reflection+occupancy baseline | 30/46 | 74 | 6 | 0 |
| Reflection + old spatial/timing condition | 38/46 | 6 | 4 | 0 |
| Identity negative control, old condition | 2/46 | 582 | 1028 | 0 |

Both original geometry interpretations are still observationally tied. Exact **row-63** prediction does **not** imply the complete 64×64 native transition has been predicted, much less hidden state or a game-solving policy.

## Current decision and next precise question

**Retain the bounded pre-action frontier relationship as observed (98/98)**. It is stronger on this new sample than the old position-only clock (66/98), but a visible row of pixels may simply track one local native animation/progression; **no independent causal mechanism or cross-game generalization** is established.

The *first uncleared native pixel* predicts a minimum boundary change but does **not yet predict whether one or two cells will advance**. The next discriminating test should infer width from an observable pre-action feature and then predeclare a new set of native histories. The 58 one-cell vs 40 two-cell effects must not be silently used as successes for an untested width rule. Preserve native pre-action neighboring pixels/rows, native level, action order and controls. Compare against frozen first-pixel, old step-clock and full-transfer predictions; retain every mismatch and nonstandard frame as explicit source-owned evidence.

The original mathematical 48 F3 laws and ARC canonical agent are unchanged. No F3 control mapping, native hidden-state isomorphism, full-game win, autonomous solver, competition score, or general ARC claim follows from these public SP80 samples.
