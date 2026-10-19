# SP80 native visible-state transition: held-out quantized boundaries + stage-specific interior

October 19, 2026. Official **original public ARC3/SP80** `arc_agi.Arcade(OperationMode.NORMAL)` investigation. No mathematical Window48 F3 source law, canonical agent, native game implementation or external solver was changed.

## Frozen prospective hypothesis

Genuine prior native SP80 boundary histories (through **elapsed context action 26**) suggested that original native row-clearance widths may be discretized from two different constant rates, **not** from an already-verified hidden clock. Predeclare the exact integer half-up candidate **before running any new native word**:

```python
C(stage, t) = min(64, floor((128*t + P_stage)/(2*P_stage)))
P_stage0 = 30
P_stage1 = 45
predicted_next_width(stage,t) = C(stage,t) - C(stage,t-1)
```

Here `t` is every genuine context ACTION4 **or** ACTION5 elapsed since original stage root; stage1 root is independently reached using public `454545`. The last native **PRE-ACTION** frame determines the stage-specific frontier: row0 rightmost nonzero native color14 for stage0, and row63 leftmost nonzero native14 for stage1. Predict original **14→0** of the next `predicted_next_width` contiguous boundary pixels (stage0 leftward, stage1 rightward). The expected pre-action frontier position from `C(t-1)` is also checked independently; after-frame pixels are never used to make their own prediction.

Combine with the unchanged prospective, independently verified **stage-specific interior ACTION4 ordinal exact color-coordinate formulas** from [PR #165's original native study](runs/WINDOW48_SP80_STAGE_MASKS_2026-10-19.md). Those 32-pixel, two 4×4 block transitions apply only to ACTION4 ordinal k1..8 in stage0 (native y16–19) and k1..6 in stage1 (native y36–39), with the exact native **9→12 and 12→9** labels. ACTION5 and later ACTION4 ordinals have empty interior transition maps.

Freeze four **full native 64×64** comparisons: interior+quantized exact boundary; interior+fixed minimum boundary width (stage0 2/stage1 1); interior+fixed maximum boundary width (stage0 3/stage1 2); interior+first native frontier pixel; interior-only negative control. Retain complete original changed-pixel and from/to-color dictionaries, all errors, withdrawn/missing/level-changed UNKNOWN events and original frame hashes.

## Original native holdout beyond historical 26-step samples

Four new **34-action** histories fixed before the native run: `4444444444444444444444444444444444`, `4444444445444444444445444444444444`, `5555444444444444444444444444444444`, `4444444444444444444455554444444444`. Each with two fresh actual stage0 attempts and two independently achieved genuine stage1 attempts. **16 original native resets, 568 real native actions** (including genuine stage1-entry prefixes and terminal interrupted actions).

[Official native GitHub Actions run #39215981810](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39215981810) **PASSED**; source-owned original JSON and native before/after full 64×64 NPZ frames in [artifact #12169960503](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39215981810/artifacts/12169960503), 14-day retention, original zip **SHA-256 `ffc1768dc9a7de6da33537c3d4b06e48b19f976f4d0f1d75d8a186fd2b282123`**. ZIP digest independently recomputed and exactly matched GitHub.

### Prospective exact complete native pixel/color results

| FROZEN model | Stage0 (admitted 240) | Stage1 (admitted 272) | Full-grid extra/missed/wrong-color changes |
| --- | ---: | ---: | --- |
| **Interior + quantized stage-specific boundary width** | **240/240** | **272/272** | **0 / 0 / 0** |
| Interior + fixed minimum boundary width | 208/240 | 160/272 | Stage0 32 misses; Stage1 112 misses |
| Interior + fixed maximum boundary width | 32/240 | 112/272 | Stage0 200 extras/16 misses; Stage1 160 extras |
| Interior + first-only boundary minimum | 0/240 | 160/272 | Incomplete by construction |
| Interior only | 0/240 | 0/272 | No boundary pixel predictions |

**Critically novel 27–34 step subset, not just replaying old n≤26:**
- **Stage0 actual steps 27–30:** 32 genuine admitted actions; **32/32** exact full original changed pixel/color dictionaries, pre-action frontier alignment 32/32, exact stage0 next-width prediction 32/32.
- **Stage1 actual steps 27–34:** 64 genuine admitted actions; **64/64** exact full original changed-pixel/color maps, pre-action frontier alignment 64/64, exact next width 64/64.
- **TOTAL NEW HORIZON:** **96/96 exact entire original 64×64 native pixel/color transition dictionaries**. No extras, misses or original native color-pair errors. Controls materially weaker.
- Stage0 actions at steps31–34 had **32/272 unavailable native frame comparisons** in total across eight attempts, following original native nonstandard terminal responses; **UNKNOWN**, not failures, successes, proof of game completion, or invented null frames. Stage1: **272/272** observable actions (0 UNKNOWN).

**Independent source verification, not CI assertion alone:** downloaded original ZIP, confirmed original digest, decoded full NPZ and JSON, reconstructed every one of **512 accepted genuine native stage0/1 original frame transitions** directly from original before/after pixel arrays, independently reconstructed stage-specific ordinal exact interior native-color masks and boundary progression from pre-action frontier + fixed integer-rate candidates. **ZERO** differences in full changed-pixel positions, before/after original native color pairs, and 96 previously unseen horizon transitions. Recomputed scores agree with source JSON and GitHub job log.

## Meaning, limitations, next boundary

This is a strong, bounded **one-step predictor of the original game's visible native 64×64 pixel transitions** under ACTION4/ACTION5, conditioned on the actual observed original pre-action stage0/1 frame, known native stage, cumulative ACTION4 ordinal and elapsed native context action count. It is NOT a complete autonomous policy: it does not demonstrate that hidden native state is determined by the screen, that the public game can be won, or that this maps to the 48 concrete F3 source laws or mathematical A/B generators.

The rates 64/30 and 64/45 are **empirically fitted**, not proven internal animation-timer semantics. No future action after the native stage0 terminal frame was observed. A green worker itself proves execution, and matched heldout original frames support only the stated action/state domain.

**Next falsifiable test:** separately test whether the stage1 64/45 rate remains exact through previously unobserved elapsed context steps **35–45**, while retaining original stages, exact 64×64 color-coordinate scoring, native action checks, prior fixed width/zero controls, stage0 terminal UNKNOWN, and all original source evidence. Stage0 beyond its native terminal boundary must remain UNKNOWN unless real source observations permit more. Do not extrapolate the native stage0 model to other game levels or replace the actual public SDK with a constructed world. Do not declare an ARC score or game win without witnessed original-game results.

Original F3-48 mathematics and canonical agent remain unchanged.
