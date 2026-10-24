# ARC4 lane B — source-pinned intervention

**State:** source-pinned gate tested and genuine original SDK interventions executed in isolated draft PR #408; all reported experiments still official level4. Subsequent unapproved candidates remain gated.

## Relationship to [lane A — PR #407](https://github.com/huntingthereferent/autobots-assemble/pull/407)
Consume the exact emitted native JSON source record from lane A (not an imagined fluid simulator). Select a specific **first source-color-6 arrival outside cup windows** at row5 or row8, including both witnesses' identical frame/x record **and a matched negative control with a different native first arrival**. Merely finding the same pixel event in positive and negative cases is insufficient. Identify an already-authenticated native selectable-object click in the actual action receipts. The proposal must name both `case` and `contrast_case`; the positive must have a four-cup observation while the matched control does not. Candidate hypothesis must be written separately and admitted with `python -m work.arc3.arc4_intervention_gate --audit AUDIT.json --proposal PROPOSAL.json --out PLAN.json`.

## Intervention
The gate verifies the most recent original `ACTION6` click and its SDK receipts, then appends **one** legal movement `ACTION1..4` to the already-selected native object immediately before the existing genuine `ACTION5`. It deliberately does **not** add another click, which would confound movement with selection history. This is a **prospective experiment**, not a predicted causal solution. Run `python -m work.arc3.native_sp80_stage4_gated_intervention --plan PLAN.json --out OUT.json` only after the source audit has established the input and the exact source-derived plan has been inspected. The pinned paired experiment freezes a reviewed plan in `work/arc3/lanes/approved-*.json` and regenerates it from the original Lane A artifact before running; any mismatch fails closed.

The new separate manual GitHub Actions workflow refuses absent/noncanonical plans; the PR workflow itself only tests and compiles the gate. Both original native entry witnesses and full 64x64 returned frames are mandatory. Only official SDK level >=5 / WIN is game progress.

## First source-pinned paired native test — verified October 22

[Native run #39731621139](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39731621139) passed its original artifact SHA-256 check, regenerated source admission, reviewed-plan equality, contract tests, original SDK paired run, and artifact upload. [Raw original JSON/NPZ artifact #12405441391](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39731621139/artifacts/12405441391), ZIP SHA-256 `a88075b03d5a0b22d9e55bc5797beadf0a138e683af1d790483e2b8e0a38700c`, configured retention 90 days.

- Frozen matched comparison: original top-bar LEFT1 control versus identical word with one extra **ACTION2/DOWN1**, with no additional click.
- Actual original source selected-bar bbox moved from `[26,20,37,22]` to `[26,23,37,25]`. Original pre-pour and final source-frame hashes changed; the intervention was not a no-op.
- Both independent native stage4 A/B entrances agreed in each condition. Across all 4 genuine original SDK resets, official outcome remained **level4 / NOT_FINISHED**; **zero level5/WIN**.
- Despite the native geometry and final-frame changes, each of the four measured cup regions was first full at original animation frames `lateral=13`, `top_left=21`, `top_middle=21`, `top_right=21`. First top/right boundary change stayed at frame21; left/bottom remained unchanged in the measured source windows. First off-cup source6 row8/frame19 and row5/frame20 at x11–13 also remained unchanged.
- This **refutes this particular one-movement candidate as a stage5 solution**. It does not prove a private causal rule, nor that other vertical interventions cannot matter.

The audited, unmerged result is available to lane C as source-pinned evidence. No further candidate is automatically selected from the failed movement.

## Upper-bar horizontal source contrast — verified October 22

[Original SDK run #39754427647](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39754427647), [JSON/NPZ artifact #12414579575](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39754427647/artifacts/12414579575), ZIP SHA-256 `4757ad60c0aef5bee60727f659c2c9e1293026ce600fa2eb9e88fa732e2b8f20`, configured retention 90 days.

Six frozen upper-bar source action histories from identical verified D3L2/L3U2 lower arrangement, with two independent original-SDK A/B entrances each: **12/12 native resets remained official level4 NOT_FINISHED, zero level5/WIN**. Source-selected upper bar on `reselect` has bbox `[29,20,40,22]`, `LEFT1` bbox `[26,20,37,22]`, `LEFT2` bbox `[23,20,34,22]`. Source top-left 45-pixel cup was never palette13-filled for reselect/LEFT2/LEFT1→RIGHT1; it first filled at frame25 for LEFT1/LEFT1→UP1/LEFT1→DOWN1. LEFT1's other cups: lateral frame13, top-middle/right frame21. All observed top/right border first changes stayed at frame21.

**Source interpretation:** the tested upper-bar horizontal position admits a narrow positive source observation at LEFT1, not a monotonic claim that more left movement is better. Vertical continuations did not abolish the cup-filling observation in this bounded parent. The original SDK still did not advance. Aligning returned animation frame indices is observational and does not assert a common physical clock.

Next frozen test within this independent lane: different genuine movement histories that **end at the same source-selected upper-bar bounding box**, to determine whether tested cup fill depends only on apparent final placement or also the actual native movement path. Do not infer hidden-engine action rules.

## Identical upper-bar coordinates from different native histories — source verified

First original SDK run: [#39754800592](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39754800592), raw [artifact #12415351323](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39754800592/artifacts/12415351323), SHA-256 `3ecfa8fd00ff5fad6b3aa4843c97f1f092fd2b37d394ad8dc5390f4fc18b7414`.

Exact source-pixel verification was then made a standalone Python audit `work/arc3/audit_arc4_same_position_pixel_diff.py`. It passed as an independent CI step on [run #39755328707](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39755328707); combined native-source and pixel-comparison [artifact #12415019473](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39755328707/artifacts/12415019473), SHA-256 `a64546e50db61ca07a986e6afc142b85eec4b7501f5516ba2c670fcdf58b544a`. Both artifacts have configured 90-day retention; no separate durable repo archive of the raw ZIP has been verified.

Five frozen original SDK upper movement paths (direct LEFT1; LEFT→RIGHT→LEFT; LEFT→UP→DOWN; LEFT→DOWN→UP; LEFT→LEFT→RIGHT), two independent native entrances each = **10/10 genuine original SDK games**. All end with selected-bar bbox `[26,20,37,22]`, all cup first-full frames `lateral=13`, `top_left=25`, `top_middle=21`, `top_right=21`, first top/right boundary change 21, and official level4 NOT_FINISHED (zero level5/WIN).

Precise difference of each longer history against direct LEFT1, verified on both entrance witnesses:
- Immediately before ACTION5: original pixel source row63 `(x10,y63)` and `(x11,y63)` are palette14 with direct LEFT1 and palette0 in longer histories. This is **2 source pixels**; the semantics of that display region are unknown.
- At the final original pour frame: only `(x11,y63)` differs (14 vs 0).
- Across all **34 native pour animation frames**, each longer history and direct LEFT1 differ in precisely one pixel per aligned frame (`x11,y63`). There are **zero** differing pixel-frame values in rows `y0..62` across all 34 frames, for every compared history and both witnesses.

The original "bottom border" audit used only rows `y59..62`, excluding the last row `y63`. The earlier claim is restricted to that measured slice, not the full image bottom edge. Thus **the original visible interior animation is identical for these five observed movement histories, while a bottom-row pixel is different**. That is not proof of hidden game-state equivalence or a general movement law.

## Frozen same-position history lengths and individual native action timeline

[Original SDK run #39757263041](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39757263041), [raw JSON/NPZ artifact #12415838204](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39757263041/artifacts/12415838204), ZIP SHA-256 `aed9ae4f2cf04344159d92dcb9ef726659c7ee5067af93df06d2839fb6fc0406`. Seven source-frozen upper-bar histories with lengths 1,3,5,7 (two independent horizontal/vertical paths each at 3,5,7), each independently re-entered from original SDK witnesses A/B: **14 genuine games, all official level4 NOT_FINISHED, zero level5/WIN**. Every selected upper-bar pre-pour bbox remains `[26,20,37,22]`. All differences in recorded native pour animation frames relative to direct LEFT1 are **confined to row y63**, with zero differing values in y0–62. Cup first-full frames remain lateral13, top-left25, top-middle/right21 across all histories.

First source palette14 pixel in y63 just before the native ACTION5, by number of upper-bar movements: **1→x10, 3→x12, 5→x13, 7→x14**. Just after the native pour: 1→x11, 3→x12, 5→x13, 7→x15. Original SDK source raw files SHA-256: JSON `d393610b2f8e553343b2322dc8eaa5b9ff8e2dd49f608c3fb01693c127bb79df`; NPZ `da58e6c1896884095ab394d0736947ff8ad3cdb9997a3f5578fcfd5592b69288`.

The **independent source-timeline audit** `work/arc3/audit_native_sp80_stage4_row63_timeline.py` downloaded and authenticated both original run files, read the actual screen after **each** SDK movement (not only the pour), and verified A/B agreement and equality across all paths containing that action ordinal. [Successful source audit run #39757748694](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39757748694), [timeline artifact #12417295064](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39757748694/artifacts/12417295064), ZIP SHA-256 `6d75b8af562c6a4e39be9d82c288528808a2af743366ac6c2a86e7115f207c97`.

| Upper-bar movement number | First palette14 x in native row63 | Independent original SDK source records |
| --- | ---: | ---: |
| 1 | 10 | 14 |
| 2 | 11 | 12 |
| 3 | 12 | 12 |
| 4 | 12 | 8 |
| 5 | 13 | 8 |
| 6 | 13 | 4 |
| 7 | 14 | 4 |

This is **a native rendered row63 correlate of movement history under the tested sources**, not evidence for what the row represents internally. It does not establish an action counter, a hidden objective, or hidden-state equivalence. The y63 source differences make prior `bottom unchanged` statements valid only for their explicitly tested `y59..62` strip. Both new artifacts have configurable 90-day retention, not verified independent durable archival copies.

## Cross-object native selection and reversible movement controls — source-verified

[Original SDK run #39759703369](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39759703369), [source JSON/NPZ artifact #12417692024](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39759703369/artifacts/12417692024), ZIP SHA256 `acc0db18a0605ac5af2e8e7199dba83f395e4fa4a54cb0ed659773976f1b2cea`, configured artifact retention 90 days (no independent durable archive verified).

The frozen original D3 lower arrangement and final upper LEFT1→ACTION5 were unchanged. Five predeclared native conditions × two independent authentic SDK entrance witnesses = **10/10 real original-SDK resets, all level4 NOT_FINISHED and no level5/WIN**. The extra native `ACTION6` selected a source-observed right bar at (46,33); an extra re-click alone, or right-bar reversible LEFT→RIGHT, UP→DOWN, RIGHT→LEFT actions were run before re-selecting the upper bar. All conditions returned exactly the same **pre-pour board pixels in rows y0..62**, and all measured cup first-full times (lateral13, top-left25, top-middle/right21) remained unchanged.

| Added right-bar actions | Pre-pour row63 first palette14 x | Post-pour first palette14 x |
| --- | ---: | ---: |
| None | 10 | 11 |
| Extra right-bar source click only | 11 | 12 |
| Extra click, then LEFT/RIGHT | 12 | 13 |
| Extra click, then UP/DOWN | 12 | 13 |
| Extra click, then RIGHT/LEFT | 12 | 13 |

**Measured limit:** native row63 responds to additional selection actions **even with no added movement**. These results do not support an upper-bar-specific movement signal. They do not establish the actual semantics of row63, a general input counter, or whether it participates in the source game's official objective. The next narrowly frozen experiment compares source-authenticated background/object/upper selections without any extra movement.

## Object/background click-only source controls — independently reproduced

[Original SDK click-only run #39760058838](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39760058838), [complete original-source JSON/NPZ artifact #12416998822](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39760058838/artifacts/12416998822), ZIP SHA256 `12951757474f724765a8f00ec0edc2d484398382a7f00b6585f221775a960acc`, 90-day artifact retention configured (durable independent copy unverified).

Seven prospectively frozen source `ACTION6` click sequences, two independent original SDK entrance witnesses each: **14/14 original SP80 games reached official level4 NOT_FINISHED; no level5/WIN**. Lower original arrangement and final upper LEFT1→ACTION5 frozen. Compare no extra click, one extra authenticated click at right bar (46,33), background (5,16), upper bar (34,21), two clicks at right bar, two clicks at background, and one right then one background click. Original action receipts, actual pixel under click, pre-pour original frame and entire native pour stack were retained.

**Observed first palette14 pixel in source row63 before ACTION5:** no extra click x10; one extra click at any tested target x11; two extra clicks at any tested targets x12. **Pre-pour rows y0..62 were identical to the baseline** in every condition; all four measured cup first-full frame ordinals were unchanged (lateral13, top-left25, top-middle/right21). Original native A/B observations agreed. The row63 change therefore is not specific to movement of an upper bar nor to selecting the right/upper bar: background clicks also produce it in this controlled source arrangement.

The source-only result suggests a rendered input-history correlate, but does **not** prove what row63 internally represents (an action counter, timer, HUD, resource display, or other mechanism) or that it is irrelevant to actual native WIN logic. No objective conclusion or inferred hidden-state equivalence is licensed. Further work requires an independent source contrast tied to the game's official `levels_completed`, not more unrestricted row63 counting.

## Native lower-L one-step placement contrast — verified October 22

[Original SDK run #39761014684](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39761014684), [raw SDK JSON/NPZ artifact #12417598191](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39761014684/artifacts/12417598191), ZIP SHA-256 `c6723c5bf7a0f4d379601ab5e263c61c95cb5fd75ded172e6475ed8250286`. Raw internal JSON SHA-256 `d00f410f8d1caf4f5d61eea169f521803d5c86c5649d04020cd353a1e93fb494`; NPZ SHA-256 `efeeb4c333ffc889eae9a767c0c5cd4553ae50d6f928fb3b032aa20dbd3998ae`. Configured Actions retention 90 days; independent durable archive not verified.

Hold genuine D3 lower parent, native selected lower-L location `x23..28,y35..40`, upper source LEFT1 and original ACTION5 fixed. Five predeclared genuine source conditions × two independent original SDK entries = **10 native resets**, all official level4 NOT_FINISHED, **zero level5/WIN**.

| Actual original lower-L movement | Verified native selected bbox | First four source cup windows simultaneously 45/45 | First measured left x2..4,y2..61 change |
| --- | --- | --- | --- |
| Original | [23,35,28,40] | frame25 | none |
| Up 1 | [23,32,28,37] | none | none |
| Down 1 | [23,38,28,43] | none | none |
| Left 1 | [20,35,25,40] | none | none |
| Right 1 | [26,35,31,40] | none | none |

The original lower-L position uniquely retains the **four-cup transient visual observation among these five tested locations**. Every moved-L source case loses complete filling of the lateral cup (45/45 never observed); top-left timing can change. The complete first six screen columns **do** show source events in these conditions; this is distinct from the unchanging measured x2..4 left wall window. No assumption that any visual strip is part of official success.

An archived original SDK frame inspection also showed the **original** case with all four cup masks full on frames 25..32, then all four reset by the last returned frame33, while official SDK remains level4. This is now independently reproduced in the artifact-authenticated [cup persistence audit #39761902892](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39761902892) using the exact original source bytes. Do not equate first-full cup animation with a stable end condition or native progress.

## Exact original SDK cup persistence — independently verified

**Independent cup persistence audit passed:** [source-authenticated run #39761902892](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39761902892), [recomputed source JSON artifact #12418776390](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39761902892/artifacts/12418776390), ZIP SHA-256 `b14df9738695d1c11e4b8181b743414d8c0ab304cb13fe1609d5237ba68f36f6`. The original SDK source files passed the frozen SHA-256 checks first. All 10 independently reset genuine SDK cases passed A/B exact agreement. In the original lower-L placement all four 45/45 cup masks were simultaneously full for original animation frames **25..32**, then **0/45** in every cup at terminal frame33; original SDK `levels_completed=4, NOT_FINISHED`. In four moved-L cases only three cup masks were full in the penultimate frame, all zero at terminal. **This verifies temporary animated filling, not an official completion rule.**

## Original SDK success-versus-nonadvance transition comparison — source-verified

[Native source run #39762841397](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39762841397), [unaltered SDK full-frame artifact #12418353014](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39762841397/artifacts/12418353014), ZIP SHA-256 `67bd82eb42be10f4b53a16a5cd37ed47c453cab2cf8cd1c0065c2dd0d4f03c40`. Configured retention 90 days; **separate durable archive NOT VERIFIED**. Exact original code `work/arc3/native_sp80_stage4_success_failure_comparison.py` and the dedicated GitHub Actions workflow are in this isolated draft branch.

**Four authentic independently reset original SP80 SDK games**: two frozen stage4 conditions (original lower-L four-cup visual transient and moved-L three-cup negative), each with independent A/B original stage1→level4 entrance witnesses. Every session includes the **same actually successful stage3→4 ACTION5** and a later unsuccessful stage4→5 ACTION5, with genuine original SDK before/after levels/states recorded.

| Genuine SDK transition | Penultimate → final whole-screen palette13 pixels | Original returned frames | Official result |
| --- | --- | ---: | --- |
| Stage3 successful ACTION5 | `180 → 0` | 30 | `levels_completed: 3 → 4` |
| Stage4 four-cup visual transient | `180 → 0` | 34 | `levels_completed: 4 → 4` |
| Stage4 three-cup negative | `135 → 0` | 30 | `levels_completed: 4 → 4` |

The **actual successful stage3 terminal frame hash** is `fa8fd32d3bfd2c8b3ff7765aec373512`; this is independently verified to be the identical genuine stage4 initial root in both sessions. The failed four-cup source terminal hash is `6368d5185062bd3dbd25816bb7ef5887`, and the three-cup control terminal hash is `fc05051865ba1a38a75ef0a258d9da72`. Both independent SDK witnesses agree on original receipts, all frame signatures, four source cup masks, and official statuses.

**Bounded conclusion:** exact `180 → 0` clearing occurs in both real official progression and real official nonprogress, so visible palette clearing is **not sufficient to identify failure or success**. The original four-cup level4 transient does not independently satisfy the stage4 SDK success condition. Frame lengths and before/after source screen geometry differ, but the private completion rule remains unknown. Do not manufacture an objective from these comparisons; preserve native statuses and source arrays.

## Stage-specific native cup masks — source archive comparison

Source held constant: [original SDK success/nonadvance run #39762841397](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39762841397) and [raw artifact #12418353014](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39762841397/artifacts/12418353014), ZIP SHA256 `67bd82eb42be10f4b53a16a5cd37ed47c453cab2cf8cd1c0065c2dd0d4f03c40`; JSON SHA256 `d13dc2f2bdfce9a019a245d1853da82de22bfb066921387bde0f1622bd846830`, NPZ SHA256 `0be84942f119108b65ce0971fc6342ec049c07528052dfaf322b1c371e8a5d30`. These source bytes were independently inspected; the standalone CI verifier [cross-stage source mask workflow](https://github.com/huntingthereferent/autobots-assemble/actions/workflows/arc4-stage3-stage4-cup-mask-contrast.yml) is a separate verification gate, not automatically green merely because a source result is recorded.

Actual original pre-ACTION5 palette11 region inventory contains **four connected 45-pixel cups** in both stages. These are different level-specific coordinate sets: stage3 bboxes `[8,53,16,58]`, `[26,53,34,58]`, `[38,53,46,58]`, `[50,53,58,58]`; stage4 bboxes `[5,35,10,43]`, `[17,5,25,10]`, `[35,5,43,10]`, `[47,5,55,10]`. Each mask was derived from that level's actual pre-pour frame, not transferred from the other stage.

| Actual original SDK ACTION5 | Four source cups concurrently full | Final source cup color13 | Official level |
| --- | --- | --- | --- |
| Stage3 → 4 | frames27–28 of 30 | all 0 at frame29 | advances 3→4 |
| Stage4 original lower-L | frames25–32 of 34 | all 0 at frame33 | remains 4 |
| Stage4 moved-L negative | never | all 0 at terminal frame | remains 4 |

This independently checked original archive refutes **four simultaneously full 45-pixel cups** as a sufficient universal indicator of an SDK level transition, even when stage4 holds its four filled cup windows longer. It does not establish a shared hidden completion rule across the different source-level layouts. All official progress claims continue to depend on original SDK levels/states.

**Next frozen native test:** [right-bar horizontal timing workflow](https://github.com/huntingthereferent/autobots-assemble/actions/workflows/arc4-stage4-right-bar-timing.yml), keeping middle, lower and upper sources unchanged. Four predeclared native right-bar horizontal placements × two independent SDK witnesses. Distinguish official stage5 from image-only cup arrival differences; no claim until real SDK results are returned.

## Verified stage-specific cup masks and right-bar arrival control

**Pass 1 — independently verified original source masks.** [Source audit #39764626858](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39764626858) passed, with [audited JSON artifact #12418334984](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39764626858/artifacts/12418334984), ZIP SHA256 `9a3ff705ce2e62ce149cba0756d53e8a6fa17b33e36a7c3752835e66a65b6c68`. Original source JSON/NPZ hashes were checked before reading, and the original SDK A/B entrance witnesses agreed. Actual level3 successful source cup boxes [8,53,16,58], [26,53,34,58], [38,53,46,58], [50,53,58,58] fill together only frames27–28; official SDK transitions **3→4**. Actual level4 source cup boxes [17,5,25,10], [35,5,43,10], [47,5,55,10], [5,35,10,43] fill together at frames25–32 but official SDK remains **4→4**. The negative original lower-L control does not fill all four. Both actual level3-success and level4-nonadvance terminal cup masks clear; therefore these screen appearances **cannot independently determine SDK progression**.

**Pass 2 — native right-bar horizontal timing.** [Original SDK run #39764626974](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39764626974), [full original-source JSON/NPZ artifact #12418974951](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39764626974/artifacts/12418974951), ZIP SHA256 `0f9b5b16c7de7350c7cc7ec22e12efca92769255d457dfc4fd5ffd3f5a8d5f27`. Four prospectively frozen right-bar positions × independent original A/B entrances: **8/8 genuine native SDK resets, all official level4 NOT_FINISHED, zero level5/WIN**. Middle placement, lower-L placement and final upper LEFT1→ACTION5 were fixed. Native selected right source bboxes and cup first-full frames:

| Frozen right-bar movement | Actual selected bbox | Lateral cup | Top-left | Top-middle | Top-right | Four concurrent cups |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Re-click only | [41,32,55,34] | 13 | never | 19 | never | no |
| LEFT1 | [38,32,52,34] | 13 | 25 | 21 | 21 | frames25..32 |
| LEFT2 | [35,32,49,34] | 13 | 25 | 23 | 19 | frames25..32 |
| RIGHT1 | [44,32,58,34] | 13 | never | 19 | never | no |

**Bound:** the additional left movement changes opposite top-middle and top-right fill timing without native advancement. Animation frame indices are not physical time or engine causality. No rule about level4 completion may be inferred from this shift.

**Next original source question:** does a true successful transition produce a visible final-screen border redraw only on its terminal frame while native level4 nonadvances do not? Existing archive comparison suggests so, but the separate SHA-authenticated source workflow `arc4-stage3-stage4-screen-transition.yml` must finish before the result is promoted. Screen redraws can be **effects** of progression, not evidence for what triggers it.

## Verified terminal-screen and right-by-upper intervention result

**Authenticated successful-transition screen audit:** [original source audit run #39765735502](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39765735502), [source JSON artifact #12420678378](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39765735502/artifacts/12420678378), ZIP SHA-256 `7a542368640bcb51ec4de78669688e3ea488886c6b20dd6ebb599de23a64bc41`, configured 90-day retention. The original paired SDK JSON/NPZ source files were authenticated before the independent audit. Four actual native SDK sessions (A/B entrances × two frozen stage4 nonadvance conditions) all agree: the real successful level3→4 transition first changes the measured left wall x2..4,y2..61 **only on terminal frame29** (171 pixels), with **1,262 total changed terminal pixels** versus its pre-ACTION5 source. The unsuccessful stage4→4 four-cup pour causes **no measured left-wall changes**, with 82 total pre-vs-terminal changed screen pixels in that condition. This is evidence of a returned-screen transition consequence, **not a causal win rule**.

**Genuine two-factor native intervention:** [original SDK run #39766706911](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39766706911), [complete original JSON and full-frame NPZ #12421295935](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39766706911/artifacts/12421295935), artifact ZIP SHA-256 `ac607d630c259fb8840a47842c3da9bc8478c8a940c95f804f91574d2feccc04`. Six prospectively fixed source interventions, two independent original SDK entrance witnesses each: **12 original games, all official `levels_completed=4, NOT_FINISHED`; no level5 or WIN**. The middle/L placements were held fixed; native right-bar LEFT1/LEFT2 were crossed against upper LEFT1, LEFT1+UP1, LEFT1+DOWN1.

| Source right bar | Source upper bbox after movement | Cup first-full (lateral,top-left,middle,right) | Four simultaneous source cup frames | Official SDK |
| --- | --- | --- | --- | --- |
| LEFT1 bbox [38,32,52,34] | LEFT1 [26,20,37,22] | (13,25,21,21) | 25..32 | level4 |
| LEFT1 | LEFT1+UP1 [26,17,37,19] | (13,25,21,21) | 25..32 | level4 |
| LEFT1 | LEFT1+DOWN1 [26,23,37,25] | (13,25,21,21) | 25..32 | level4 |
| LEFT2 bbox [35,32,49,34] | LEFT1 [26,20,37,22] | (13,25,23,19) | 25..32 | level4 |
| LEFT2 | LEFT1+UP1 [26,17,37,19] | (13,25,23,19) | 25..32 | level4 |
| LEFT2 | LEFT1+DOWN1 [26,23,37,25] | (13,25,23,19) | 25..32 | level4 |

All six native source cases retain the same visual four-cup full frames, no measured left x2..4,y2..61 change, and no official advancement. An upper-bar one-step vertical displacement is not a differentiating native cup event in these particular configurations. Preserve actual source pixels and no hidden-state equivalence claim. Independent durable archive **NOT VERIFIED**.

## Same-game repeated native ACTION5: verified exact source audit

**Original SDK source run passed:** [native Actions #39768996710](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39768996710), [complete original JSON and returned-frame NPZ artifact #12422021789](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39768996710/artifacts/12422021789), ZIP SHA-256 `0ea3addf36bf716e8e9d006df32ec0b165d3b65aa61b97e9e4a9cf32a1c7ab2f`, embedded JSON SHA-256 `d4c59df2a07d476edb215c21ec2eee14bb5ef98d8c9c661d45f5b82c070ad44c`, original NPZ SHA-256 `5582db5ac26205a0f888450a90ac568d6d4f9177bd0deb8ade0db6e050335376`. Configured artifact retention 90 days; independently durable archive not verified.

**Original native design:** right-bar LEFT1 and LEFT2, same frozen middle/L/upper positions, **1, 2 or 3 actual ACTION5 pours without movement between pours** in the SAME original SDK game. Six source cases × independent original A/B entrances = **12 genuine game resets**; every SDK ACTION5 yielded `levels_completed 4→4`, `NOT_FINISHED`. All 12 original sessions preserve genuine 34-frame ACTION5 stacks with identical four-cup visual timing for the matching right-bar configuration. **Zero level5/WIN.**

An independent read-only pixel audit of the downloaded original artifact checked every animation frame and every first/second/third native pour for both witnesses:

| Original source right setting | First pour terminal changes | Second pour terminal changes | Third pour terminal changes |
| --- | --- | --- | --- |
| LEFT1 | 82 = 36 pixels 9→8 (old selected upper), 45 pixels 8→9 (new selected right), and `(10,63) 14→0` | only `(11,63) 14→0` | 0 |
| LEFT2 | 82 = same 36/45 selection transfer and `(11,63) 14→0` | 0 | only `(12,63) 14→0` |

The second and third native pours have **exactly the same pixel values across all 34 returned animation frames for rows y0..62** as the first pour in the same fixed arrangement. Where full frames differ, the only difference is one pixel at **y63** for each of the 34 animation indices (LEFT1 pour2/3 at x11; LEFT2 pour3 at x12). Original A/B source witnesses agree exactly. The SHA-authenticated full-frame source comparison was also exported as a separate local, machine-readable audit; GitHub source records remain the authoritative provenance.

**Research limit:** no new measurable board-region response from repeated pours without new movement, and no official advancement. Bottom-row change does not decode any private SDK counter/hidden state, and exact visible-frame equality does not prove equivalence of internal state. This is distinct from earlier stage4 second-pour studies because these original right LEFT1/LEFT2 clean four-cup parents and exact no-movement temporal controls were frozen separately.

## Original post-pour movement-order comparison — verified native SDK

[Independent original SDK run #39775056684](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39775056684) succeeded with **8/8 independently reset original SP80 games** (four predeclared arms × two authentic A/B entrance histories). [Original full native JSON/NPZ artifact #12423663752](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39775056684/artifacts/12423663752), ZIP SHA256 `7b46395f958143d6e469e9a9b1ae3c63d605afce17b925e0a35dd3019ecee1a4`. Internal authentic JSON SHA256 `ef8bf268e6ebcf044f3c60e3b58cf344f940d65b3b19bd7bfb3428540ae28d4b`, full original NPZ SHA256 `598acbfceca76eb25836b884d038ce07310af9b13f69afebe4270a221f83c43a` (independently rehashed and checked). Artifact configured 90-day retention; separately durable archive not confirmed. Native original level4 source root `fa8fd32d3bfd2c8b3ff7765aec373512`.

**Controlled original SDK action-history comparison.** Direct placement RIGHT LEFT1 or LEFT2 + fixed middle D3L2, lower L3U2, upper LEFT1, then genuine ACTION5, versus **after a failed four-cup ACTION5**, the SDK-selected right bar moved once toward the other verified placement, upper bar explicitly reselected with a source click, then a second native ACTION5. All source SDK positions were checked from actual palette9 selected bboxes, not assumed. Original right selected bbox [38,32,52,34] moves to [35,32,49,34] with post-pour LEFT1; the reverse post-pour RIGHT1 moves [35,32,49,34] back to [38,32,52,34]. Actual upper reselected bbox [26,20,37,22] in both. Independently verified SDK witnesses agree.

| Comparison | Authentic post-first-pour source action word suffix | Original pre-final-pour image differences | Aligned 34-frame final-pour image differences | Official outcome |
| --- | --- | --- | --- | --- |
| Direct RIGHT LEFT2 vs RIGHT LEFT1 → pour → right LEFT1 → reselect upper → pour | `5 3 6@34,21 5` | **0 on y0..62**, 1 on y63 (x11) | **0 on y0..62**, 34 changed pixels total, all row63 | Both level4 NOT_FINISHED |
| Direct RIGHT LEFT1 vs RIGHT LEFT2 → pour → right RIGHT1 → reselect upper → pour | `5 4 6@34,21 5` | **0 on y0..62**, 3 on row63 (x10..12) | **0 on y0..62**, 68 changed pixels total, all row63 | Both level4 NOT_FINISHED |

Source-native palette6 and palette13 masks match at **all 34 aligned frames** for each paired final ACTION5, with no changed frame pixels anywhere in y0..62. Both actual SDK witnesses repeat these exact source results and no level5 or WIN occurs in the eight games. This directly constrains the role of an earlier failed pour **within these precise native histories**, but does not prove hidden SDK state equivalence, generic action commutativity, or any inferred WIN condition. Avoid repeating these history arrangements as if their visible response had changed.

**CI note:** every ARC-specific workflow on the immediately previous Lane B head passed. The broader network `protocol-tests` failed separately on `test_workstation_equilibrium_ui.EquilibriumObserverTests.test_observer_counts_transitions_not_page_refreshes` (workstation/UI), not on the native ARC logic; this PR is not fully green on that head. Do not turn that failure into an ARC gameplay claim.

## Hold conditions
Unknown source contact, mismatching A/B witnesses, missing prior click receipt, or illegal action => stop at **UNKNOWN**. Do not widen to an uncontrolled search. Keep mathematical ARC-like models, WORLD, NIH, and other workers unchanged. Do not merge without native evidence and all required protocol gates.
