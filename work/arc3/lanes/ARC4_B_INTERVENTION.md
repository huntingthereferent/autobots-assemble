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

## Hold conditions
Unknown source contact, mismatching A/B witnesses, missing prior click receipt, or illegal action => stop at **UNKNOWN**. Do not widen to an uncontrolled search. Keep mathematical ARC-like models, WORLD, NIH, and other workers unchanged. Do not merge without native evidence and all required protocol gates.
