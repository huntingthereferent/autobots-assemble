# SP80 stage1 original-native steps 35–45: frozen full-frame predictor and terminal state

October 19, 2026. Native original public ARC3/SP80 `arc_agi.Arcade(OperationMode.NORMAL)` only. This test is not an F3 source 48-law identity, autonomous native puzzle solver, or an ARC win.

## Exactly frozen prospective research boundary

The previous independent [full-frame stage-specific SP80 holdout](runs/WINDOW48_SP80_QUANTIZED_FULL_FRAME_2026-10-19.md) showed **240/240** complete original stage0 pixel+color changes and **272/272** complete original stage1 changes exact, including **96/96 observations at previously untested steps 27–34**. It used source-frozen ACTION4-ordinal interior 4x4 native color masks and two empirically fitted integer half-up cumulative boundary-clearance rates:

- Stage0 y0, right-to-left: `C0(t)=min(64,floor((128t+30)/60))`, saturating at 30 context actions.
- Stage1 y63, left-to-right: `C1(t)=min(64,floor((128t+45)/90))`, saturating at 45 context actions.

`t` is original actual context-action count (ACTION4 or ACTION5). Predict exact next boundary width by `C(t)-C(t-1)`, from original **PRE-ACTION** stage frame; combine with the prior unmodified ordinal-specific interior masks (original ACTION4 count k1..8 on stage0 y16..19, k1..6 on stage1 y36..39, each two 4×4 native 9→12 and 12→9 blocks). The *current after-frame* is only the independently observed verification target, never a prediction input.

Freeze this entire candidate and controls **before executing the new actions**. Test a genuinely unseen stage1 horizon **steps 35–45** on four new fixed original native 48-action histories: 48 ACTION4, eight ACTION5 then forty ACTION4, 24 alternating ACTION4/ACTION5, and twenty ACTION4 + eight ACTION5 + twenty ACTION4. Two independently reset original stage0 and independently reached original stage1 runs per word, for **16 fresh original native resets**. Keep original full frame NPZ, JSON records, action IDs, stage and source hashes, original colors and nonstandard terminal evidence. Models: frozen quantized full grid, fixed min-width full grid, fixed max-width full grid, interior+first-only, and interior-only negative control. No rules, words or rates changed upon seeing the results.

## Actual original native execution and authenticated source

[Successful official original SP80 native run #39217198445](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39217198445); 16 fresh native resets and **364 genuine original native actions**, including stage1-entry prefixes and terminal calls.

[Original JSON and full before/after NPZ evidence artifact #12169504932](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39217198445/artifacts/12169504932), 14-day retention through November 2, 2026. Original downloaded ZIP SHA-256 **`0248ea4542c390a5c1fceedea34c53fd880cb263bfd80aedead5ca1228b02e28`** exactly matches GitHub's recorded digest.

### Genuine native admissions

| Fixed native word | Stage0 admitted per reset | Stage1 admitted per reset | Genuine terminal response |
| --- | ---: | ---: | --- |
| `4` repeated 48 | 30 | 45 | Original `GameState.GAME_OVER`, nonstandard empty frame on next action |
| `5` repeated 8 then `4` repeated 40 | 5 | 5 | Original `GameState.GAME_OVER` before additional contexts |
| `45` repeated 24 | 5 | 10 | Original `GameState.GAME_OVER` for stage1 after context10; stage0 changed levels after context5 |
| `4` repeated 20 + `5` repeated 8 + `4` repeated 20 | 25 | 25 | Original `GameState.GAME_OVER` after context25 |

Each row occurred in **two independently reset native trials**, with the exact original stage-entry/action histories, before/after frames and interruption metadata retained. The next nonstandard `GAME_OVER` frame is **not** assigned a replacement state, counted as a tested pixel transition, or interpreted as a witnessed win.

**Actual measured effects:** **130 stage0**, **170 stage1**, **300 genuine admitted native before/after 64×64 color dictionaries** from 768 originally requested context positions (384 potential per stage). Thus **254 stage0 and 214 stage1** proposed positions unavailable/UNKNOWN after native terminal or level-changing events. Native SDK supplied no valid after-frame for these; zero claims inferred.

### Exact score, including the prospective unseen horizon

| Frozen original full-frame model | Stage0 exact | Stage1 exact |
| --- | ---: | ---: |
| **Quantized stage-specific boundary + prior exact ordinal interior masks** | **130/130** | **170/170** |
| Fixed minimum stage-specific boundary width plus interior | 112/130 | 98/170 |
| Fixed maximum width plus interior | 18/130 | 72/170 |
| Interior only | 0/130 | 0/170 |

The quantized original **whole 64×64 changed pixel + before/after color** predictions were exact in every admitted transition: zero extra cells, missing changed cells, or wrong original native color pairs.

**New stage1 steps 35–45:** Only the **all-ACTION4** word reached that horizon. Each of two genuine fresh stage1 resets produced eleven exact source action effects, so **22/22 prospective previously unseen observations** had the original pre-action frontier at the predicted x, predicted native color14 and **exact complete original changed-pixel/color dictionaries**. Old fixed-minimum control was exact 12/22; old fixed-maximum 10/22. No original stage0 native run reached step35. No eligible stage1 effects after step45 survived before the game's actual nonstandard `GameState.GAME_OVER` response.

This is a bona fide independent held-out test of the frozen model for **the all-ACTION4 trajectory**, **not** 22 independent game types and **not** generalization to the three mixed-action words. Those contexts terminated too early to test stage1 actions35–45, and must remain UNKNOWN at that horizon.

### Independent actual-frame recheck

Original ZIP downloaded, SHA-256 recomputed from its bytes and matched against GitHub. Original NPZ arrays and JSON were separately decoded. For each of 300 admitted original native effects, independently reconstructed the before/after actual 64×64 changed cell and color-pair dictionary and recalculated the unchanged source ACTION4 ordinal block masks and `C0/C1` pre-action quantized frontier. **All 300 predicted complete transition dictionaries were exactly equal to original observed dictionaries**, including all 22 previously unseen stage1 step35–45 effects. No disagreement with the committed original source model scores.

## Decision, strict limits, next research move

The empirical fitted `64/45` boundary rate and prior interior color masks **survive the new original native 35–45 stage1 horizon when the action history is entirely ACTION4**. At the very next requested action, the original public SDK returned `GameState.GAME_OVER` with an empty/nonstandard frame; whether that corresponds to puzzle success or failure cannot be determined from this frame alone and must **not** be asserted as a win. Other native ACTION4/ACTION5 histories reach that state much earlier. Their lack of stage1 step35–45 frames is a genuine experimental reachability limitation, not a falsification of the rate.

**Next discriminating experiment:** vary exactly one *LATE* ACTION5 placement in an otherwise all-ACTION4 native stage1 history (for example context positions 33, 35, 39 or 43), leaving all earlier words/periods/region masks untouched. Independently record the real native `GAME_OVER` onset, original stage, state, last complete valid frame, genuine action and successor observation, and whether the frozen 64×64 prediction remains exact **if** original stage1 actions35–45 are still admitted. Keep an exact all-ACTION4 native control. Do not silently infer a state transition from missing frames, treat `GAME_OVER` as proof of winning, or replace the original public game with a simulation.

The original Window48 F3 48 mathematical laws, canonical agent, and source rights remain unchanged. No autonomous game-solving policy, source-native A/B generator equivalence, native hidden-state identity, or ARC benchmark score was established.
