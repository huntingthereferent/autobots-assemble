# Original SP80 stage0 — ACTION4 count versus observed bar displacement

October 19, 2026. Original public native `arc_agi.Arcade(OperationMode.NORMAL)` SP80; **not** the separately developed mathematical F3 source laws, game replacement, or six-level solution.

## Why this source experiment was necessary

The [stage0 ACTION4/ACTION5-only discovery](runs/WINDOW48_SP80_STAGE0_PROGRESS_ACTION5_2026-10-19.md) and [independently frozen held-out ACTION4/ACTION5-only test](runs/WINDOW48_SP80_STAGE0_COUNT_HOLDOUT_2026-10-19.md) showed actual source SDK level0→1 advancement when an ACTION5 occurred after exactly three prior ACTION4 calls. The prior domain did **not** include leftward ACTION3 or up/down ACTION1/2. Therefore the claim that the total number of earlier ACTION4 calls itself explains success remained untested against motion cancellation.

The new worker `native_sp80_stage0_position_ordinal.py` precommits **22 mixed-native-action words**, two independent original-game resets per word, incorporating native left ACTION3 after/before right ACTION4, vertical source ACTION1/ACTION2 movements, original root/position restoration and controls with four/five ACTION4 uses but horizontal cancellation. Every action is checked against genuine SDK advertised legality. All returned native SDK images, official level and WIN/GAME_OVER, actual preaction selected-color9 position and full-screen hash are saved. Source objective labels come ONLY from actual SDK `levels_completed` and state.

## Real original source execution and independent audit

[Successful original native SP80 run #39308252281](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39308252281): **44/44 genuinely reset original stage0 games**, **244 actual SDK action responses**, **44 true ACTION5 responses**, **26 actual SDK level0→1 advances**, 18 source no-progress outcomes. Native progression stops at SDK level change. All commands ACTION1–5 used only when advertised.

[Untouched actual original native JSON + complete 64×64 returned-frame NPZ artifact #12213939999](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39308252281/artifacts/12213939999), archive ZIP SHA256 independently recomputed **`ea140f92bd27e11ac806f6a956fcbca5a23ffed9a2346d9d6256e60f4afc4f14`**, matching GitHub source artifact.

**Independent raw-source audit:** downloaded original archive, decoded all original SDK NPZ arrays and source event JSON, reconstructed actual `(x,y,before_native_color,after_native_color)` changes for **all 1,188/1,188 real returned SDK frame transitions**, including each intermediate ACTION5 animation frame, and checked SDK native color6/9/11/14 counts for every frame. **ZERO mismatches** across 244 actual SDK responses. This checks authentic original frames, not a generated game.

## The earlier ACTION4-count explanation is falsified

| Original net horizontal native control displacement (ACTION4 uses minus ACTION3 uses) before ACTION5 | Actual source ACTION5 responses | Original SDK level0→1 | Returned source images per ACTION5 |
| --- | ---: | ---: | --- |
| 0 | 2 | 0 | 22 |
| 1 | 4 | 0 | 22 |
| 2 | 12 | 0 | 28 |
| **3** | **26** | **26** | **20** |

For all sampled games, each advertised stage0 ACTION4 moved highlighted native color9 20×4 bar four pixels right and each ACTION3 moved it four pixels left in the tested positions. Original starting bar `x12–31,y16–19`; **all 26 genuine native advances had pre-ACTION5 selected bar at `x24–43`**, exactly three four-pixel net steps to the right, even when different horizontal histories led there and even when vertical y varied.

**Decisive paired source counterexamples:**
- `4445`: three right ACTION4, zero left ACTION3; bar x24–43 and source SDK advanced at ACTION5, which returned **20 frames**.
- `44435`: still three right ACTION4 but one left ACTION3; bar **x20–39**, and ACTION5 returned **28 frames** without progress. `34445`, `44345`, `43445` reproduced this negative with the same net displacement in different native ordering.
- `444435` or `443445`: **four** ACTION4 with **one** cancelling ACTION3; pre-ACTION5 bar **x24–43** and actual SDK advanced, ACTION5 20 returned frames. This is a direct counterexample to any strict rule requiring exactly three preceding ACTION4 uses.
- `44444335`: **five** ACTION4 and **two** ACTION3, again net-right three; official native level advanced and ACTION5 returned 20 frames.
- `44415`, `14445` (up), and `44425`, `24445` (down) also genuinely advanced after net-right three with pre-ACTION5 x24–43 but different actual selected-bar y locations. Up/down and restore controls likewise preserved advancement where horizontal position matched.

Thus in this bounded experiment **net original horizontal bar position** is more predictive than raw ACTION4 count; the earlier 36/36 correctly predicted source outcomes only **within its restricted ACTION4/ACTION5 domain**, where ordinal count and horizontal displacement were inseparable. Do not erase or retroactively describe those records as wrong observations: their classification was correct, their broader causal attribution is now falsified.

These are original source-visible motion and true SDK outcomes, **not** proof that color9 x24–43 is the entire hidden native engine predicate under every possible history, starting object, level or state. A 20-frame ACTION5 is an observed source response associated with progress here, not a game trigger mechanism.

## Next original source research movement

Prospectively test horizontal-location sufficiency with independent source-native stage0 controls at x24–43 using further varied histories including coordinate-selected native ACTION6 and vertical offsets, and explicitly check counterexamples. More importantly, stage1 has three genuine selectable native bars and previously failed to advance under various individual positioning experiments. Stage1's objective must be investigated independently, perhaps coordinating multiple bars' horizontal positions before ACTION5. Do **not** transfer the x24–43 stage0 rule as an assumed universal or claim source level2 progress.

Preserve all SDK animation frames, real source clicks with `data={"x":x,"y":y}`, historical negative evidence, F3 current mathematical working anchors, canonical ARC agent and owner rights unchanged. No fake SP80, bot, hidden-state equivalence, or competition win.
