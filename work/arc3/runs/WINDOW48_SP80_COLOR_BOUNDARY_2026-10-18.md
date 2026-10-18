# SP80 — native color transfer and frozen boundary prediction

**Research date:** October 18, 2026, America/Chicago. Real official public ARC-AGI-3 SP80 game, arc-agi Arcade NORMAL. The mathematical context is the ORIGINAL 48-law WindowCombined construction; there is still no witnessed native F3 A/B correspondence, rooted conjugacy, or ARC game win.

## Provenance

- [Earlier actual stage-specific native frame registration](WINDOW48_SP80_HELDOUT_GEOMETRY_2026-10-18.md) found two equally scoring candidate changed-mask maps: identity + shift (8,+20) and reflect_y + shift (8,-8). The changed-mask overlap was 32/33 on stage-1 ACTION4, not exact. Mathematical F3 was NOT used to fit either mapping.
- [Real native ACTION4 color-context experiment #39101363234](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39101363234), [original native frames and exhaustive transition labels](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39101363234/artifacts/12126891069).
- [Reproducible native color-context script](../native_sp80_frozen_color_contexts.py), run by [its original native GitHub Actions workflow](../../../.github/workflows/arc3-sp80-color-contexts.yml).
- [Separate actual native blind boundary-rule test #39101668708](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39101668708), [real frames, per-pixel predictions and failures](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39101668708/artifacts/12126233317).
- [Frozen-boundary prediction executable](../native_sp80_boundary_prediction.py), [independent regression](../../../network/tests/test_arc3_sp80_boundary_prediction.py) and [live native CI](../../../.github/workflows/arc3-sp80-boundary-prediction.yml).

All raw native pixel frames use exact original colors 0 through 15; no image-coordinate or palette modulo-three mapping was applied.

## First newly observed experiment: unchanged native color labels across stages

Before actual native actions, seven new context words were specified: 4, 44, 54, 544, 444, 5454 and 5. Each was run independently on level 0 and then on a newly reset game advanced to genuine level 1 by the previously witnessed word 454545. There were TWO independently reset level-pairs per word, a total of **28 fresh native game resets, 148 real actions, 14/14 completed context pairs**.

The two spatial maps were frozen BEFORE this experiment. When projected stage-0 pixel changes overlapped actual stage-1 changed pixels, the EXACT native old-to-new color pair also matched on **704/704 overlaps**, across 22 actual ACTION4 responses. The mean native changed-mask F1 was **0.9751623**. ACTION5 negative controls overlapped zero source-mapped pixels. Neither model was an exact entire mask.

The 34 unpredicted stage-1 ACTION4 changes, aggregated over those 22 observations, were ALL color **14 to 0**, all on the real bottom row **y=63**, at observed x coordinates among 0 through 5. The 44 source clipping occurrences were also native color **14 to 0**, on the stage-0 top row, near x=56..63. Both frozen maps showed the SAME residuals.

This gives an observationally motivated spatial boundary candidate; it does NOT justify declaring any native color an F3 field element or preferring reflection to pure translation.

## Frozen native bottom-row completion hypothesis

A source-owned action-history pattern was specified BEFORE the NEXT official native trial. For ACTION4 at position n of a stage-1 word, add exact native color change 14 to 0 on bottom row y=63:

| Level-1 word position n | Predicted additional changed x cells |
| --- | --- |
| 1 | 0 |
| 2 | 1 and 2 |
| 3 | 3 |
| 4 | 4 and 5 |
| 5 | 6 |
| 6 | 7 and 8 |

For odd n, x = 3*(n-1)//2. For even n, x = 3*(n-2)//2 + 1 and the next x. This is **empirical native step indexing**, not mathematical F3 addition. Frozen before subsequent test, including the unchanged geometry alternatives.

## Second test: completely new native action words

The separate blind native test fixed five previously unobserved context words: 4444, 5544, 45444, 54454 and 54544. Each word was independently tested at level 0 and level 1, twice each. There were **20 fresh native resets and 152 real environment actions**, with **10/10 complete stage pairs**. The corresponding actual level-0 transition colors and pixel positions were projected to level 1 using each frozen geometry rule, out-of-bounds pixels were clipped, and the predeclared row-63 completion rule was applied. Every resulting entire changed-pixel and original old-to-new-color map was compared with the ACTUAL native level-1 observation, including false positives.

| Native result | Frozen translation + boundary rule | Frozen reflection + boundary rule | Unshifted identity control |
| --- | ---: | ---: | ---: |
| Real ACTION4 comparisons | 32 | 32 | 32 |
| Entire transition effects EXACT | **18/32** | **18/32** | 0/32 |
| Actual native changed cells | 1,070 | 1,070 | 1,070 |
| Correct actual native old/new color labels and locations | **1,070/1,070** | **1,070/1,070** | 46 |
| Actual changes NOT predicted | **0** | **0** | 1,024 |
| Wrong native color at an overlapping predicted change | **0** | **0** | 0 |
| Extra predicted native changes absent in the real game | **20** | **20** | 1,096 |

The two frozen geometry hypotheses remain tied. Both correctly included every one of the **1,070 actual native pixel color changes** in the resulting target responses but neither predicted all action effects exactly.

**Falsifying residuals:** 14/32 complete ACTION4 predictions overpredicted one or two native 14-to-0 changes near the RIGHT board edge, absent in the actual game. Under translation they were at (63,20), or (61,20) and (62,20). Under reflection they were at the corresponding (63,55), or (61,55) and (62,55). There were **20 such false predicted changes** in total. These are real errors and were NOT retroactively removed or explained away.

This is not 1,070 independent game situations; it is 32 same-game native action effects over 10 matched pairs of fresh stage tests. Stage-0 frames for corresponding native actions were provided to the transfer model; this is **not** a standalone agent able to predict native level-1 behavior or select solving actions solely from its own initial observation.

## Research boundary

Established: repeatable partial **native color-transition plus geometric** transfer between SP80 public levels 0 and 1, including a concrete action-history boundary pattern. Its completeness remains contradicted by twenty reproducible missing-to-native overpredictions. The next admissible step is to predeclare an obstacle/edge admissibility explanation for those extra changes, then check it with independent native interventions without refitting on the held-out failures.

Not established: a unique native spatial conjugacy, any Window48 F3 law realized by SP80, mapping to the source 16 rooted classes or 14 full-state classes, hidden-state equivalence, completion of SP80, other ARC wins, or a general ARC solver. The original mathematical WindowCombined source and canonical F3-48 agent were not changed.
