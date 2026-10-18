# SP80 — native before-color occupancy closes the tested boundary errors

**Research date:** October 18, 2026, America/Chicago. **Provider:** official public ARC-AGI-3 SP80 native game, arc-agi Arcade NORMAL. This is a continuation of the source-owned ORIGINAL 48-law F3 WindowCombined investigation, but it does **not** identify ARC actions with mathematical A/B or assert an F3 conjugacy.

## Previous evidence motivating the new hypothesis

The [earlier frozen color/boundary investigation](WINDOW48_SP80_COLOR_BOUNDARY_2026-10-18.md) established that two previously fitted stage-0-to-stage-1 geometric mappings, plus a predeclared bottom-row native 14-to-0 completion rule, covered all 1,070 observed level-1 ACTION4 native color changes from five fresh action-word contexts.

However, **only 18/32 complete action effects were exact**. Twenty extra 14-to-0 changes were predicted at the opposite/right board edge where the real native game did NOT change the pixels. That failure was preserved, not silently discarded or used to fit a geometric transform.

The two frozen mappings were:
- **T:** identity geometry then translation by native pixels (+8,+20).
- **R:** reflect native y then translation (+8,-8).
- Negative comparator: identity geometry with no shift.

The original 48 mathematical laws, their distinction of 16 rooted versus 14 full-state classes, and the canonical standalone F3-48 ARC agent are unchanged.

## New independently falsifiable constraint

**Hypothesis predeclared before collecting the next native game data:** For each previously predicted level-1 color transition (old_native_color,new_native_color) at native coordinate (x,y), KEEP the predicted change only if the **actual level-1 native frame BEFORE action** contains exactly old_native_color at (x,y), and old_native_color differs from new_native_color. This includes projected stage-0 native effects and the earlier independently specified bottom-edge completions.

This is a necessary source-color *occupancy* gate, NOT a general sufficiency law. It checks only the **pre-action** native image and does not consult the image AFTER action when deciding which changes to predict. Its failures remain admissible counterexamples. The original ungated model remains a frozen comparator and is scored on every trial.

This test remains **conditional** on (1) observing a real corresponding stage-0 transition and (2) reading the real level-1 pre-action frame. It does NOT predict how to solve a new stage from its root by itself.

## Actual official public ARC native experiment

- [Final successful native Actions run #39119743313](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39119743313).
- [Native raw 64x64 source/target frames and complete pre-color admission / rejection JSON](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39119743313/artifacts/12133866851). Artifacts have limited GitHub retention.
- [Native executable](../native_sp80_occupancy_gate.py), [pre-color regression suite](../../../network/tests/test_arc3_sp80_occupancy_gate.py), and [official native GitHub workflow](../../../.github/workflows/arc3-sp80-occupancy-gate.yml).

The six fresh native action words were fixed before first execution: 444444, 445444, 554444, 455444, 545454, 544554. Each word was tested at native level 0 on a fresh reset and separately at genuine native level 1, reached by first reproducing the already observed 454545 level-0 progression word. TWO independent level pairs were run per word.

| Native experimental quantity | Verified outcome |
| --- | ---: |
| Newly predeclared context words | 6 |
| Independent native level-0/level-1 pairs | **12 / 12 complete** |
| Real fresh native environment resets | **24** |
| Actual environment actions | **216** |
| Native ACTION4 before/after effects evaluated | **50** |
| Actual changed pixels with native old/new colors | **1,680** |

### Source-registered models, unchanged geometry

| Result | Frozen T before gate | Frozen T after gate | Frozen R before gate | Frozen R after gate |
| --- | ---: | ---: | ---: | ---: |
| Exact complete action-transition maps | 20/50 | **50/50** | 20/50 | **50/50** |
| Actual native changes predicted with correct native colors | 1,680 / 1,680 | **1,680 / 1,680** | 1,680 / 1,680 | **1,680 / 1,680** |
| Predicted changes that did NOT happen | **50** | **0** | **50** | **0** |
| Real native changes removed by gate | n/a | **0** | n/a | **0** |
| Wrong native old/new color labels | 0 | **0** | 0 | **0** |

**All 50 original extra predictions** were native color transition **14 -> 0**, but the true level-1 pixel BEFORE action had **native color 12**, not 14. Thus they were rejected by the source-color precondition, not by looking at the post-action frame or excluding the expected after-state coordinates.

In these six new contexts, the occupancy gate removed **exactly 50 false changes and zero real changes**, yielding **50/50 completely exact** stage-1 ACTION4 native pixel/color transition maps for both previously frozen spatial mappings. Each included every one of the **1,680** observed actual changes, with no misses and no color mismatch.

The no-shift identity negative control still performed badly even after the same pre-color gate: **0/50 exact** effects and only **80 of 1,680** actual native color changes covered, versus 1,680 under each shifted/reflected candidate. This guards against claiming the occupancy rule alone explains the action.

## Interpretation and unresolved boundary

This is an **independently reproduced, completely exact conditional transition relation for the specific tested native public SP80 ACTION4 observations**, stronger than the earlier 18/32 result. The gate is a verified source-colored constraint: the previous overpredictions occurred exactly where a real target pre-action pixel had native color 12 rather than the predicted 14.

**It does not establish** that an action must change a pixel merely because the pixel has the expected old color, nor that the same rule holds on untested SP80 stages/longer action histories/other ARC games. The two frozen geometry hypotheses remain observationally tied: both map the admissible observed changes exactly, so these trials do NOT prove reflection is necessary or that pure translation is the actual game rule. Board clipping and action-history-dependent bottom-row changes remain empirical features, not bijective conjugacy maps.

Most importantly, the tested mapping consumes a real stage-0 action effect AND a real level-1 pre-action image; it is **not** an autonomous prediction of the native next state from a level root and action alone, an independent goal-directed game policy, a complete SP80 game win, or any original Window48 F3-48 A/B generator or 16-rooted-class realization.

**Next admissible movement:** test the same frozen occupancy-conditioned relation at genuinely different native states that exhibit the rule's limits, or a different stage/action, without rebuilding a bot or fitting new pixels post hoc. The canonical original F3-48 single-file ARC agent and mathematical source remain untouched.
