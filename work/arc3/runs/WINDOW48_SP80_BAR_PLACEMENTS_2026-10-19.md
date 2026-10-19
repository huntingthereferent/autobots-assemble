# Original SP80: placing coordinate-selected bars at other observed bands

October 19, 2026. Genuine public original `arc_agi.Arcade(OperationMode.NORMAL)` SP80 game and all actual returned native SDK frames. Not a clone, simulated physics, autonomous policy, or claimed solution.

## Why this experiment was necessary

Earlier original-native trials [matched action age and changed selected-bar geometry](runs/WINDOW48_SP80_MATCHED_GEOMETRY_2026-10-19.md) and established real ACTION5 temporal responses returning 22,23,26,28 frames, but none advanced beyond the original level1. Independently sourced original stage1 screen pixels show three selectable horizontal regions:
- selected native color9 20×4 bar `x20..39,y36..39`;
- unselected upper native color8 12×4 bar `x8..19,y16..19`;
- unselected lower native color8 12×4 bar `x28..39,y24..27`.

These are **observed movable/selected colored objects**, not sourced puzzle target semantics. The new experiment tests specific source-native placements with proper native coordinate clicks, independent of predicting animation length.

## Frozen original native game instructions

Before any new game execution, fix 16 source action programs with two genuine independent Arcade.NORMAL original resets each:
- control `1115` without click;
- select lower bar using proper SDK `ACTION6,data={"x":32,"y":25}`, move left×5 and up×2 toward upper bar's original coordinates, in both action orders, then ACTION5;
- select upper using `ACTION6` at `(12,17)`, move right×5 and down×2 toward lower bar's original coordinates, in both orders, then ACTION5;
- select first already-highlighted bar `(24,37)`, move left×3/up×5 toward upper or right×2/up×3 toward lower, including opposite order controls, then ACTION5;
- move clicked lower/upper toward the former selected bar position and opposite-direction variants;
- two sequential bar selections/placements aiming to put multiple bars on one observed row;
- matched upper→lower/lower→upper click-order controls and an upward-to-native-top source-region control.

Each source trial enters genuine original stage1 by witnessing actual `454545` original SDK level0→1 prefix. Each action is checked as legal before use. Every ACTION6 click has its actual pre-action source pixel recorded because a previously moved image can change which object exists at a fixed coordinate. Every SDK response's **entire actual `obs.frame` returned stack** is saved, never only `[-1]`; actual source `levels_completed`, `WIN`, `GAME_OVER` and all native pixel/color changes are recorded. Actual SDK level2 or WIN is the ONLY permitted progression claim.

## Independent source execution and audit

[Original native GitHub Actions run #39299998030](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39299998030) PASSED, **32/32 genuinely reset original SP80 stage1 games**, 16 frozen programs × two independently reset copies, all native programs COMPLETE, **446 original SDK action responses**, **38 properly coordinate-bearing original ACTION6 clicks**, and **zero actual level2 advancements, zero WIN, zero GAME_OVER**. Every final SDK report is `levels_completed=1`, `GameState.NOT_FINISHED`.

[Untouched actual source SDK NPZ full returned 64×64 frames and JSON — artifact #12210636667](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39299998030/artifacts/12210636667), original ZIP SHA256 independently recalculated `607ee005475b299bd3cfda5f940ca14f743a1d9ea073b10d92aa554b76724b64` matching GitHub's artifact digest, retained for 14 days.

**Independent complete returned-frame audit:** downloaded the actual original artifact, decoded all original NPZ and JSON, and for each of the 446 real SDK action responses independently reconstructed **3,270/3,270** original `(x,y, before_native_color, after_native_color)` change dictionaries from consecutive source-returned full frames, including intermediate ACTION5 images. **ZERO mismatches**. All 38 original ACTION6 `(x,y)` arguments and actual pre-click pixel colors were also independently rechecked against genuine preceding native frames, with zero mismatches. No simulated frames or discarded counterexamples.

## What the original native source actually did

| Frozen source program category | Real observed final native color9 selection | SDK objective outcome |
| --- | --- | --- |
| No-click `1115` control | x28–39,y24–27 (12×4), original lower band | level1 NOT_FINISHED |
| Select lower and move left×5/up×2 (both orders), then ACTION5 | x20–39,y36–39, original first bar | level1 NOT_FINISHED |
| Select upper and move right×5/down×2 (both orders), then ACTION5 | x20–39,y36–39, original first bar | level1 NOT_FINISHED |
| Select the first bar, move toward upper or toward native top, then ACTION5 | x28–39,y24–27, original lower bar | level1 NOT_FINISHED |
| Select first bar, move up×3/right×2, then ACTION5 | x28–47,y24–27 (20×4) | level1 NOT_FINISHED |
| Select upper/lower bars in both orders, then ACTION5 without movement | x20–39,y36–39 | level1 NOT_FINISHED |
| Select first, move upward, then select lower and move it upward | x28–39,y16–19, upper-row 12×4 location shifted to right | level1 NOT_FINISHED |
| Select upper, move it down twice, select first and move it up three times | x28–39,y24–27, lower-row 12×4 selection | level1 NOT_FINISHED |

Every table category was replicated on genuine independent resets with the full source record. Some final frames visually return the selected highlight to another bar after ACTION5: **pre-ACTION5 placement and post-ACTION5 selected bar are distinct observable events**, and neither is yet verified as a native puzzle goal.

In the original first-to-lower/up-first case, color9 remains a **20×4 bar** at x28–47,y24–27 with original color8 total48, distinct from the ordinary color9 12×4 selection of the lower bar. This confirms actual varied source geometry was reached rather than only frozen-word controls. None advanced the official level.

## Research boundary

The observed original-game placements—including two-bar same-row arrangements and source-contact attempts—were **not sufficient** to trigger original SDK stage1→stage2 in these samples. The earlier finding that geometry changes ACTION5's returned animation remains independent and valid, but neither geometric contact nor frame-count variation has been shown to be the game objective.

Next research should inspect an **independently sourced native objective/progression cue** rather than automatically declare any color intersection a target. One source-grounded direction is to compare the full SDK frame stacks of ACTION5 on successful stage0→stage1 events (real prefix `454545`) with level1 non-progress events, preserving actual source level-change timing and any transient pixel event that differentiates progression from ordinary ACTION5 pulses; then predeclare a fresh native level1 intervention. Do not assume a displayed glyph is a score or copy a hidden game engine. Original 48 F3 mathematical laws, canonical agent, rights and all source game records are unchanged. No six-level solve or scientific proof of hidden state.
