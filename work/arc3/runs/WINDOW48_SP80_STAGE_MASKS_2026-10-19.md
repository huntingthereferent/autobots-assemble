# SP80 genuine native stage0/stage1 interior mask and bounded translation

October 19, 2026. Independently executed original public ARC3/SP80 `arc_agi.Arcade(OperationMode.NORMAL)`, retaining exact native 0–15 pixel color IDs and full 64x64 frames. These are empirical visible-board relations, not the original 48 F3 source law, rooted equivalence or an autonomous ARC solver.

## Prospective exact hypothesis

From the prior original real [stage1 exact-mask holdout](runs/WINDOW48_SP80_EXACT_ACTION4_MASK_2026-10-19.md), separately inspect authentic original stage0/1 frames: stage0 displayed an additional two cumulative ACTION4 movements, plus native row y0 progress; stage1 displayed six movements in rows y36..39, plus native row y63 progress. The previous frames suggested a fixed `(+8,+20)` geometry for corresponding block pixels, but those previous observations are discovery data, not independent validation.

Before a fresh native action was issued, freeze separate **INTERIOR y=1..62** changed-pixel/color dictionary predictions:

- **Stage 0, native ACTION4 ordinal k=1..8:** original rows y16,17,18,19; x=8+4k through 11+4k native color **9→12**; x=28+4k through 31+4k native color **12→9**. Each predicts 32 exact pixels. Later ACTION4 and ACTION5 predict no **interior** changed pixels.
- **Stage 1, native ACTION4 ordinal k=1..6:** rows y36,37,38,39; x=16+4k through 19+4k **9→12**; x=36+4k through 39+4k **12→9**. Each predicts 32 exact pixels. Later ACTION4 and ACTION5 predict no **interior** changed pixels.
- **Matched real stage0→stage1 ACTION4 pairs only for k<=6:** translate the actual original stage0 pixel/color effect by exactly `(dx,dy)=(+8,+20)`, preserving original native from/to color labels; independently compare complete translated interior dictionaries with observed genuine stage1 interior effects. This transfer is *conditioned on observed genuine stage0 source change*, not independent prediction of a future original-game action or hidden-state identity.
- **Controls:** absolute action-word step in place of cumulative ACTION4 ordinal; wrongly impose the stage1 formula on both stages; predict no interior native changes.

The native row **y0 and y63 are explicitly NOT predicted by these interior equations**, but original before/after pixel/color changes on both boundaries and full frame stacks are retained as separate evidence, not discarded or inferred to be static. Interrupted original native actions, stage advancement and nonstandard frames are UNKNOWN, not scored.

Six new fixed mixed ACTION4/ACTION5 sixteen-action histories: `5544444444444444`, `4455444444444444`, `4545454444444444`, `4444555444444444`, `5445454444444444`, `5555444444444444`. Two independently reset original genuine stage0 and independently entered genuine stage1 trajectories per word (stage1 original native entry prefix `454545` witnessed). 24 actual original game resets.

[Official native original-game workflow #39213286441](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39213286441) **PASSED**. 416 actual native actions. Source-owned original JSON plus raw compressed native full 64x64 frame NPZ preserved as [artifact #12168501470](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39213286441/artifacts/12168501470), retained 14 days through 2026-11-02. ZIP SHA256 **e7794fe60870add857da199fadae067f4a4826cd60b2ce6408a2e9c5729dda65** independently recomputed and exactly matches GitHub artifact digest.

## Independent original-frame test result

| Real original native evidence | Exact | Wrong extras | Misses | Wrong native colors |
| --- | ---: | ---: | ---: | ---: |
| Stage0 specific cumulative ACTION4 ordinal masks | **148/148** | 0 | 0 | 0 |
| Stage1 specific cumulative ACTION4 ordinal masks | **192/192** | 0 | 0 | 0 |
| Observed genuine stage0→stage1 `(+8,+20)` translation at matched ACTION4 ordinals 1..6 | **60/60** | 0 | 0 | 0 |
| Stage0 absolute word-step mask control | 86/148 | 1,280 | 1,984 | 0 |
| Stage1 absolute word-step mask control | 134/192 | 832 | 1,856 | 0 |
| Stage0: wrongly impose stage1 mask | 72/148 | 1,920 | 2,432 | 0 |
| Stage1: predict all interior pixels unchanged | 120/192 | 0 | 2,304 | 0 |

**Original native admissions:** 148 accepted stage0 actions and 192 accepted stage1 actions out of 192 candidate steps in each stage. Stage0 had **44 UNKNOWN** original actions: final 11 context positions in each of four stage0 trajectories (two repeats of `4545454444444444` and two repeats of `5445454444444444`) after real level change/nonstandard responses. Stage1 had **zero unknown** in this sample. Sixty valid cross-stage matching original ACTION4 effects had original observed source and target pairs and genuine same-ordinal native actions.

**Independent raw-frame verification:** source ZIP downloaded and SHA256 authenticated. For every admitted stage0/1 step, read the actual 64x64 before/after images at the retained native stage root index, recompute every original interior color/pixel change from raw arrays and compare to both saved original JSON and the predeclared equations. All **340 accepted** stage-specific native effects matched without a single pixel position or color disagreement; 60 source-target transfers matched independently. This is not an after-frame fit.

## Interpretation, limits and exact next question

The new original data support a **bounded stage-dependent visible-block action relationship**, with different maximum movement ordinals (eight genuine ACTION4 actions in stage0, six in stage1), geometry offset (+8,+20), and original native color-pair preservation for observed matched ordinals. The action-count distinction is directly falsified against absolute word position on this sample. The different stage endpoints are observed native visible-state limits, **not proof of hidden-state stasis** or an identification of the mechanics.

What remains UNKNOWN is the original boundary y0 behavior in stage0, boundary y63 behavior in stage1, and how to predict full native 64x64 action effects across stages without observing the target after-frame. Previously incomplete row63 frontier-width hypotheses and falsified seven-pixel spacing must remain separate; do not treat exact interior masks as if they repaired these boundary errors.

**Next native question:** compare the two original visible boundary rows as separate stage-specific effects, predeclare a test of a real **pre-action** frontier/color transition relationship and any corresponding stage translation/reflection ONLY if supported by genuine native source observations, then test on fresh original-game histories and retain the earlier negative controls. Do not silently paste stage0 row0 progress into stage1 row63 as an F3 action mapping.

Original 48 mathematical F3 laws and canonical ARC agent were not changed; no alternative game, bot, full 64x64 exact native predictor, hidden-state equality, full-game win or ARC benchmark score has been established.
