# SP80 — independent native frontier-width holdout

October 19, 2026. An official public native ARC3/SP80 experiment, not an F3-48 mathematical correspondence or full-game solve.

## Frozen prospective width hypotheses

After [the independently verified 13-step pre-action frontier observation](runs/WINDOW48_SP80_FRONTIER_HOLDOUT_2026-10-19.md) (98/98 minimum native 14→0 and contiguous 1/2-cell row-63 advances), this experiment fixes three candidate **NEXT WIDTH** predictions *before the new original-game execution*:

- **X3:** first native pre-action row63 nonzero/color-14 frontier at x; predict width 1 if x divisible by 3, otherwise width 2.
- **ALT:** if a preceding actual native action produced an observed one-pixel advance, predict 2; if it produced a two-pixel advance, predict 1. At an original root with frontier x=0, predict 1. After an interrupted/unknown predecessor, do not predict.
- **ONE negative control:** predict width 1 for every admissible native stage1 step.

X3 and ALT were exploratory, nonexact candidates with already visible earlier counterexamples; their old discovery-sample fit is **not** counted as validation. All current predictions are formed with genuine native **pre-action** row pixels and (ALT only) the **previously observed** native width. Current-action after-frame never enters its own prediction. Compare to the old absolute-position clock and frozen native full stage0→stage1 geometry/occupancy/spatial-timing models separately. ACTION4/ACTION5 histories are distinct from mathematical F3 action labels.

**New fixed 17-action words:** `44444444444444444`, `44444544444444444`, `45444445444445444`, `54444454444454444`, `44554444455444444`, `55544444445554444`. Each has two independently reset actual stage0 attempts and two independently entered stage1 attempts via genuine native `454545` prefix.

[GitHub Actions native width run #39209887708](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39209887708) finished **successfully**. Official native SDK `arc_agi.Arcade(OperationMode.NORMAL)`, not a reimplementation, simulator or abstract test fixture.

[Retained full original JSON + native before/after NPZ frames, artifact #12167157318](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39209887708/artifacts/12167157318). Original ZIP SHA-256 `a6434a918b884d2efcbff95c7a5d3be7e571da2f6b464f9332bdf3f007f12c52`; independently recomputed and matched original GitHub digest. Retention 14 days.

## Actual native result

**464 real native actions, 24 independently reset native SP80 environments**, 12 stage pairs total. **194 genuine admissible** level1 ACTION4/5 before/after frame comparisons, including 162 ACTION4 and 32 ACTION5. The minimum frontier advance and a contiguous width in {1,2} remained observed on **194/194** admissible effects. Actual widths: **114 one-pixel, 80 two-pixel**; old absolute step-clock row was exact only **84/194**.

| Prospective row-63 width model | Exact native row changes | Extras | Misses | Wrong color |
| --- | ---: | ---: | ---: | ---: |
| ALT (alternate previous observed width) | **172/194** | 22 | 0 | 0 |
| ONE negative control | 114/194 | 0 | 80 | 0 |
| X3 (frontier x modulo 3) | 108/194 | 66 | 20 | 0 |

ALT outperformed both explicitly predeclared comparators but was not exact. All 22 erroneous predictions were overpredictions of the **second** row63 pixel; no target-first-pixel error was observed.

**All ALT counterexamples:** exactly two repeated native frontier sites:
- **Context step 8, original pre-action frontier x=10**: actual width 1 while ALT predicted width 2, **12 independent paired native trials** (ACTION4 and ACTION5 both represented).
- **Context step 13, pre-action frontier x=17**: actual width 1 while ALT predicted width 2, **10 independent paired native trials** (both native ACTION4 and ACTION5 represented).

Raw original frames independently reproduce every evaluated before/after frontier x, row63 color transition, exact/nonexact verdict and both exception coordinates. These are repeated observations of the same public game's progression, **not twelve or ten separate games** and not evidence for a universal hidden clock.

**UNKNOWN:** the `55544444445554444` word ended after native step 12 in each replicate with `UNKNOWN_NONSTANDARD_FRAME`; its final five prospective stage1 context actions per replicate have no admissible native frame, so **10 of the 204 planned stage1 actions remain UNKNOWN**. The other ten stage pairs reached all 17 context steps. Unknowns are not negatives.

### Full 64×64 stage transfer is a separate result

Only matched stage0→stage1 ACTION4 comparisons qualify (**162**, not 194). The frozen geometry+occupancy baselines matched **64/162** effects, while the old spatial/timing condition matched **88/162** with 66 extra and 54 missed changes; translation and reflection still tie. Identity control with old condition matched only 2/162. Neither local 194/194 minimum-frontier witnessing nor ALT's 172/194 width predictions is an independent exact 64×64 stage transfer.

## Decision and next research question

The **one/two-pixel local frontier relationship remains supported within these admitted native observations**, but neither X3 nor ALT predicts width exactly. The two ALT exceptions are visible phase/position **counterexamples**, not permission to patch an after-the-fact x=10 or x=17 lookup and claim held-out success. In particular, whether they reflect a native rule, a hidden timer or some other process is UNKNOWN.

Next inspect original native **pre-action** state around these two transitions and use a newly predeclared, falsifiable width candidate on fresh native histories that reach additional previously unseen frontier coordinates (rather than reusing these exceptions as confirmation). Retain an untreated ALT control, ONE and X3 controls, genuine ACTION5 contrasts, raw frames, native levels, interrupted states, exact errors and source identity. Any counterexample must remain evidence, not get silently refit.

No original 48-law F3 mathematics change, canonical ARC agent change, native-game implementation change, alternative game/bot, source/native rooted conjugacy, autonomous solution, full-game win or competition score is established.
