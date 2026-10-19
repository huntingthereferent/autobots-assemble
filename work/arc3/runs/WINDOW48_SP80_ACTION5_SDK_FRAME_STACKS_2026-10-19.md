# Original SP80 — every SDK-returned frame during ACTION5

October 19, 2026. Genuine original public `arc_agi.Arcade(operation_mode=OperationMode.NORMAL)` and official original native SP80 game, **not** a simulated game, a fabricated solver or the mathematical F3-48 system.

## Corrected observation boundary

Earlier independently verified original ARC experimental workers used `native_sp80_stage_transfer.py:frame_view`. That helper explicitly selected `obs.frame[-1]` when the native SDK returned a three-dimensional `(frames,64,64)` pixel array. Its final-frame images, transitions and native `levels_completed` observations remain genuine and correct **for the last frame**. But those archives were NOT complete recordings of all images returned within an ACTION5 response. Prior visual-color models must not be interpreted as covering intermediate native animation without an independent observation.

The new source worker `work/arc3/native_sp80_action5_frame_stacks.py` retains every original `obs.frame` array from every original reset, all actual six `454545` stage1-entry actions and every context action in original typed SDK `uint8` arrays, **without interpolation**. It saves the complete source stacks into original NPZ, and every consecutive original native frame-to-frame `(x,y, native_before_color, native_after_color)` change dictionary, raw payload shapes/byte digests, SDK state, level counters, and exact click coordinates into JSON. A native SDK response without a complete frame is marked unknown and cannot silently become an admitted observation. All native ACTION6 clicks carry real `data={"x":x,"y":y}`.

## Prospectively fixed independent original-game run

Twelve real original stage1 source plans, two independently reset official original games per plan: no-movement ACTION5; movement `1115` and upper-band `111113335`; initial properly selected original lower/upper color8 bar followed by ACTION5; both orders of selecting two source bars then ACTION5; selected bar shifted by native ACTION3 or ACTION4 before ACTION5; background-click control; and two coordinate-bearing ACTION6 negative controls.

[Actual original native GitHub Actions run #39262110791](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39262110791) **PASSED**. Across **24 independently reset original-game sessions**, it recorded **230 genuinely executed native SDK action responses**, of which **20 were level1 context ACTION5**. These action responses yielded **2,258 actual original SDK-returned complete 64×64 images** total. Every original trial ended `levels_completed=1` and `GameState.NOT_FINISHED`; **zero genuine stage2 advances, WIN or GAME_OVER**.

[Retained original source JSON and ALL complete SDK returned frame stacks in NPZ — artifact #12191772198](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39262110791/artifacts/12191772198), original ZIP SHA256 **`4b4b059c4886f4c4d94df57bf432ab78d2675ddeb1b9f66434ae69cbd9aaa75b`**, independently recomputed from the downloaded artifact and matching original GitHub artifact digest. Retained for 14 days through November 2, 2026.

**Independent full native source audit:** verified original ZIP byte digest, loaded actual native JSON and NPZ, and independently recalculated each of **2,258/2,258** original consecutive returned-frame pixel/color change dictionaries (including first response frame against the preceding action's last frame and every intermediate-to-intermediate transition) directly from original arrays. **ZERO discrepancies.** The digest proves retained archive identity, while the separate NPZ-vs-JSON audit verifies the source event consistency.

## Material native evidence

| Original native SDK action context | Actual original SDK response shape | Source-observed responses |
| --- | --- | ---: |
| Stage1 ACTION5 (selected/unselected and moved controls) | **(22,64,64)** | **20/20**, all two independent replicates |
| Stage1 ACTION1, ACTION3, ACTION4, correct coordinate ACTION6 | **(1,64,64)** | 66 total context non-ACTION5 responses |
| Genuine stage0-entry ACTION4 | **(1,64,64)** | **72/72** |
| Genuine stage0-entry ACTION5 | **(20,64,64)**, **(22,64,64)**, **(28,64,64)** | **24 each** across 72 actual stage0 entry ACTION5 responses |

The three genuine stage0-entry ACTION5 lengths show the animation-frame count is **not globally fixed to 22**. The source supports a 22-frame ACTION5 response in the sampled stage1 contexts, not a universal duration or internal game-timing law.

**Material information discarded by last-frame-only extraction:**
- Every observed stage1 ACTION5 supplied **21 earlier source frames plus its final image**. The retained 20 genuine ACTION5 responses therefore contain **440 real source-returned images**, instead of only 20 final images.
- Across the sampled ACTION5 contexts, original **704–784 pixels** per response differ from the pre-action image at an intermediate returned frame but return to that pre-action color in the final frame. Net last-frame changes range from **one** pixel (unmoved case) to **130** pixels (upper geometry/source selection). Thus a small final-frame difference is **not evidence that little happened during the source animation**.
- The untouched original no-movement `ACTION5` example returns **22 images, 18 byte-distinct**. In its first 21 returned frames native color9 selected bar is absent; during frames 0–13 the number of native color6 pixels advances 16,32,...,224; source top color11 pixels alternate between their visible 240-cell image and zero in late intermediate frames. In the final frame (index21), color9 returns as an 80-pixel selected bar, native color6 returns to 16 cells, and native top color11 returns to 240 cells. These are **observed source color/pixel events**, not proven game goal semantics or hidden mechanics.
- Source all-frames tests preserve exact native pixel counts and coordinate click actions. They do not establish any automatic level2 advance or WIN.

## Decision and next experiment

**The earlier final-frame predictors remain locally valid but are incomplete temporal descriptions of the actual original SDK output.** This correction is structural, not a retroactive fabrication of old intermediate-frame evidence. Do not relabel previous 512/512 final-frame changed-color predictions as full animation predictions. Do not assume every ACTION5 returns 22 frames, since genuine stage0 returns 20/22/28 on different source actions.

A successor should use the **complete observed source animation stack** to test a prospectively specified temporal event or a score/level condition, preserving the exact order of all original returned images, original SDK state/levels and properly coordinate-selected multiple native bars. Investigate whether differences in the **animation stack**, rather than only its last image, distinguish candidate native game progress. Only `levels_completed>=2` or `GameState.WIN` supports solving progress. No source F3-48 mathematical equivalence, synthetic physics, hidden-state identity, AI bot, six-level win or competition score is established.

The original F3-48 source mathematical laws, canonical ARC agent, owner rights and earlier source evidence remain unchanged.
