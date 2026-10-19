# Genuine original SP80 — held-out ACTION5 temporal signatures and six counterexamples

October 19, 2026. Public original ARC3 `arc_agi.Arcade(OperationMode.NORMAL)` native SP80; no substitute world, inferred internal clock, claimed hidden state, or solved game.

## Frozen source hypothesis — BEFORE independent native runs

The [earlier full native frame-stack archive](runs/WINDOW48_SP80_ACTION5_SDK_FRAME_STACKS_2026-10-19.md) retained 2,258 actual original SDK-returned 64×64 frames and found **20/20 stage1 ACTION5 responses** in its sampled source contexts had 22 returned frames, a shared original color6 pixel-count ramp, shared top color11 blink, and no original color9 pixels in frames 0–20.

This new `native_sp80_action5_temporal_holdout.py` froze **four exact falsifiable hypotheses** before new original source actions:
1. H1: Every stage1 ACTION5 returns exactly **22** native 64×64 images.
2. H2: The original native source **color6 count** over all returned frames equals `[16,32,48,64,80,96,112,128,144,160,176,192,208,224,224,224,224,224,224,224,224,16]`.
3. H3: The original native **color11 count** equals `[240]*15 + [0,240,0,240,0,0,240]`.
4. H4: The source **color9 count is zero in EVERY intermediate returned frame** before the final frame.

Neither frame index nor pixel count is a measured wall-clock unit or a decoded game score. A failed hypothesis is saved rather than discarded.

Ten genuinely new, predeclared original native stage1 histories (each two new independent SDK resets): mixed ACTION1/2/3/4 movements after coordinate-selecting original upper/lower color8 bars, the reverse selection order, click after moving, two distinctly timed **second ACTION5** invocations after additional movement, plus 24 ACTION4 or 24 ACTION1 actions before a late ACTION5. Every source ACTION6 uses explicit real `data={"x":x,"y":y}`. All 20 runs witness native stage0→1 prefix `454545`, preserve every actual SDK-returned image, native level and terminal state and every source x/y before/after color change.

## Original native execution and source verification

[Successful original-game native GitHub Actions run #39265891712](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39265891712): **20 independently reset genuine original stage1 sessions**, **310 actual SDK action responses**, **24 admitted native ACTION5 events**, **554 full source-returned ACTION5 images**, and **2,180 total original returned 64×64 action frames**. Every source run concluded SDK `levels_completed=1`, `GameState.NOT_FINISHED`, **0 level2 advances, 0 WIN, 0 GAME_OVER**.

[Full original JSON and raw NPZ source artifact #12193855886](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39265891712/artifacts/12193855886), SHA256 **`6f3b7362d9549d4dd3c87c80b3189ae95a02eb7f39f7d90e9b8a1eb68dcc9487`**, independently downloaded and recomputed, matching source GitHub artifact digest. Fourteen-day retention to November 2, 2026.

**Independent raw source audit:** loaded original native NPZ for all 20 source sessions and native JSON. For every returned source action stack, rederived every consecutive `x,y, original previous color, actual next color` dictionary from the full 64×64 images, including within each ACTION5 animation. **2,180/2,180 matches to source event records, zero differences**, and all real frame counts reconcile to the original NPZ shapes. This is independent scoring of source arrays, not a proxy animation reconstruction.

## Falsified versus supported source hypotheses

| Predeclared native stage1 hypothesis | Match / all admitted ACTION5 events | Decision |
| --- | ---: | --- |
| H1: exactly 22 original frames | **18/24** | FALSIFIED as a universal rule |
| H2: frozen 22-frame color6 ramp | **18/24** | FALSIFIED as a universal rule |
| H3: frozen 22-frame color11 blink | **18/24** | FALSIFIED as a universal rule |
| H4: native color9 absent from all intermediate frames | **24/24** | Supported **on this bounded sample** |

Source-retained counterexamples reproduce **in both genuinely reset trials** for each of three histories:

| Prospectively fixed native history | ACTION5 context | Original native frames per response | Direct original temporal evidence |
| --- | ---: | ---: | --- |
| Select upper (12,17), select lower (32,25), ACTION4 twice, ACTION2, then ACTION5 | context6 | **23,23** | native color6 ramps to **368** source pixels; source color11 blinks `80/0` in late frames |
| Select lower (32,25), ACTION1, ACTION5, ACTION4, **second ACTION5** | context5 | **28,28** | native color6 peaks at **560**; color11 temporarily holds **160/80/0** before restoring |
| Select upper (12,17), ACTION3, ACTION5, ACTION4, **second ACTION5** | context5 | **28,28** | same native color6 maximum **560**, with partial source color11 counts |

For comparison, the *first ACTION5* in each two-ACTION5 trial still returned **22** source frames; the other two stage1 source routes with different first/last selected bar and mixed movements also returned 22 images. A late single ACTION5 after **24 actual movement actions** still returned 22 in both tested histories. Thus chronological lateness by itself is not sufficient in these source observations to explain the 28-frame response. Selection order may matter, but this study does not isolate every relevant state variable.

**What the evidence actually proves:** ACTION5's number and timing of **SDK-returned source frames** and its source color6/color11 visual pulse vary with the sampled native action histories. All genuine source game responses and color counts are observed directly, not inferred from an imitation or assumed internal timer. The sampled zero-color9 intermediate behavior is stable across 22-, 23- and 28-frame source observations, but is NOT established as a universal engine law.

## Decision and next bounded discrimination

Do not silently update the previously frozen 22-frame template to fit these source counterexamples and call it verified. The three distinct observed response lengths are now **22, 23 and 28 frames**, with visibly distinct native color6/color11 patterns. The fact that the original SDK returns multiple frames is a separate, firmly witnessed observation; exact temporal prediction beyond sampled contexts remains an OPEN research problem.

The next original-game experiment should **separate two candidate causes** with predeclared independent controls: (a) sequential coordinate-selection order (upper→lower versus lower→upper) at the same number of source movement actions; and (b) a prior ACTION5 within the same level, without conflating that with a different current bar position. Use genuine original frames, verify same pre-action interior/full image where applicable, record the entire SDK frame stack, and only treat native `levels_completed>=2` or `GameState.WIN` as actual game progress. Do not claim to know hidden game timing or source target semantics from pixel counts.

The original F3-48 mathematical laws, canonical ARC agent, native source game, rights and all earlier owner-backed evidence remain unchanged.
