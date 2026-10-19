# SP80 shared original-native runner — terminal observation contract repaired

October 19, 2026. Original native ARC3 SP80, not source F3-48 law or autonomous solver.

## Observed defect

The shared `work/arc3/native_sp80_frozen_color_contexts.py:steps_on_real_game` previously treated a **complete native frame** as proof that the game was still active. On authentic stage0/1 runs, the official SDK returned `GameState.GAME_OVER` **alongside that valid terminal frame**. The old worker kept stepping, then labeled a *subsequent* empty/nonstandard frame `UNKNOWN_NONSTANDARD_FRAME`, sometimes describing that later action as the terminal boundary. The independent [official terminal and scorecard audit](runs/WINDOW48_SP80_TERMINAL_SCORECARD_2026-10-19.md) instead witnessed `GAME_OVER` on genuine stage0 context action30, stage1 all-ACTION4 context action45, with valid 64×64 terminal images; six levels required to win, and only 0 or 1 level completed. `GAME_OVER` is **not** `WIN`.

## Bounded repair

The existing shared helper now:

- Classifies the **explicit original SDK state** (`WIN`, `GAME_OVER`) independently of the original frame's shape; it does not infer winning from a cleared animation or a reported level.
- **Preserves the real full terminal frame and original frame hash**, native level, exact SDK action index, context action position and explicit terminal state in `terminal_observation`.
- Stops at the **first original terminal report** without attempting a further original game action, even when the terminal frame is complete.
- Separates `NATIVE_TERMINAL_WIN` and `NATIVE_TERMINAL_GAME_OVER` from genuine `UNKNOWN_NONSTANDARD_FRAME` and action withdrawal.
- Leaves the original nonterminal transition data and native 64×64 before/after image saving intact; no fabricated next frame or hidden-game code introduced.

### Actual validation

[Native terminal regression GitHub Actions #39220155147](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39220155147) PASSED the **three bounded synthetic unit tests**, and separately executed fresh genuine original public SP80:

| Native original replay | First reported terminal | Real SDK actions performed | Complete source frames saved | Extra postterminal steps |
| --- | --- | ---: | ---: | ---: |
| Stage0 from reset, ACTION4-only | `GameState.GAME_OVER` at context30 | **30** | 31 (reset + 30) | **0** |
| Genuine stage1 after six native `454545` entry actions, ACTION4-only | `GameState.GAME_OVER` at context45 / native index51 | **51** | 52 (reset + 51) | **0** |

Both terminal states were observed on valid original `64×64` native terminal frames. Stage1 root index remained **6**. A separate older [native-color-context regression](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39220155083) also passed after the shared helper change; earlier experiments were not rewritten.

[Original-native regression JSON artifact #12171815101](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39220155147/artifacts/12171815101) has an independently recomputed original ZIP SHA256 **`01154039920dbbbce4991640ca6e242b7132928f32240131286a359c8d7a701c`**, exactly matching GitHub's digest, retained 14 days through November 2, 2026.

## Research boundary

This is a **native observation contract fix**, not a retroactive rerun of all older original SP80 artifacts. Historical exact 64×64 changed-pixel/color predictions have their own source lineages and are not silently changed; however historical `UNKNOWN_NONSTANDARD_FRAME` statuses when the worker stepped AFTER a terminal must be interpreted with this verified source correction. Avoid combining old and new admission counts without explicit re-execution and reconciliation.

A native `GameState.GAME_OVER` response still denotes termination without a WIN report. The independent official scorecard study found original stage0 **0/6 levels**, stage1 **1/6**, `completed=false`, and partial SDK score on stage1. A valid terminal frame or exact pixel predictor is **not** evidence of game completion.

Next work should trace actual native level objectives/actions and test genuine progression beyond one completed level. Preserve the original F3-48 mathematics, canonical agent, rights, raw original source evidence, and negative controls. No synthetic game or autonomous solved policy was introduced.
