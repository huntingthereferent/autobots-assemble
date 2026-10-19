# SP80 original-native terminal state and SDK scorecard audit

October 19, 2026. **Actual official public original ARC3/SP80 native game** using `arc_agi.Arcade(OperationMode.NORMAL)`, not a synthetic duplicate or a generated policy. This investigation is specifically about reported game outcome and level progress, rather than refitting the already verified visible-color effects.

## The official contract and why this matters

The [official ARC-AGI-3 game-state documentation](https://docs.arcprize.org/full-play-test) states that `WIN` is objective completion, while `GAME_OVER` means the game terminated (for an action cap or other condition). The [original official ARC toolkit examples](https://github.com/arcprize/ARC-AGI) check `GameState.WIN` separately from `GameState.GAME_OVER`; `levels_completed` and `win_levels` provide observable native progress and `Arcade.get_scorecard()` supplies score records.

Older experimental SP80 worker `steps_on_real_game` admitted complete frames without halting on explicit native terminal state, and attempted a **subsequent** action; the next empty/nonstandard frame was then recorded as the detected termination boundary. Consequently earlier research records mistakenly described the terminal as first arriving at stage1 *attempt* 46, rather than explicitly reading the valid stage1 **action45** `state` field. The earlier exact pixel-change maps are not retroactively false; their **terminal-state attribution was incomplete** and must be corrected.

## Prospective independent state/scorecard evidence

Four explicit original native action histories, each on **two independently reset original SP80 sessions**:
1. Genuine stage0 from reset, thirty-four requested ACTION4s (stop at first actual terminal).
2. Genuine stage1 after real six-action prefix `454545`, then forty-eight requested ACTION4s.
3. Same stage1 entry, then one ACTION5 at context step39 in an otherwise ACTION4 word.
4. Same stage1 entry, then an eight-ACTION5 prefix followed by forty ACTION4s.

The original SDK **state, `levels_completed`, `win_levels`, legal actions, complete/nonstandard frame status, source frame hash, first terminal state and exact native action** were observed directly after each action; the runner stops immediately on explicit `WIN` or `GAME_OVER`, **even if a valid 64×64 frame was returned**. An independent `Arcade` is created per trial. Official SDK `get_scorecard()` is read and only a tightly whitelisted subset of original scores, level counts and reported native run states is retained. API keys, GUIDs and scorecard identifiers are deliberately omitted from persisted data.

[Actual original-native workflow run #39219311533](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39219311533) **PASSED**, 286 real native SDK actions across **eight fresh original-game resets**. Retained actual native action/level/status JSON and original complete before/after full-frame NPZ in [artifact #12171171441](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39219311533/artifacts/12171171441), 14-day retention through November 2, 2026. Independently downloaded ZIP SHA-256 **`1e569cdfe059df192adfb3e1fc06a8b7c015ab732533f24be19866aec318e65d`** exactly matched GitHub's source artifact digest.

## Actual authoritative terminal results

| Genuine original control (two fresh resets each) | Native terminal context action | Terminal SDK state | Levels completed / win levels | Official SDK scorecard result |
| --- | ---: | --- | --- | --- |
| Stage0, only ACTION4 | **30** | `GAME_OVER` | **0 / 6** | score **0**; completed false |
| Stage1, only ACTION4 | **45** | `GAME_OVER` | **1 / 6** | score **4.761904761904762**; completed false |
| Stage1, one ACTION5 at context39 | **45** | `GAME_OVER` | **1 / 6** | score **4.761904761904762**; completed false |
| Stage1, first eight ACTION5 | **5** | `GAME_OVER` | **1 / 6** | score **4.761904761904762**; completed false |

In **all eight** independently executed native trials, `GameState.GAME_OVER` arrived alongside a **complete** original native frame of shape `[1,64,64]` (not an empty frame), and `levels_completed` equaled the official scorecard's cumulative completed-level counter. The scorecard's recorded run status was `GAME_OVER` and its `completed` value was false. **Zero** source observations ever reported `GameState.WIN`; **zero** native games completed all six levels. The positive native score is **partial progress**, not a game win. The precise numeric score is reported as an SDK scorecard value, not interpreted as percent of game won.

A next SDK request **after** this already terminal state may return an empty/nonstandard frame; that is a *postterminal action attempt*, not the first GAME_OVER transition. These attempted postterminal calls were intentionally **not made** in this bounded state audit. The prior first-terminal-state timing descriptions in the parent reports should be read with this correction.

**Independent source authentication:** raw ZIP downloaded, original digest independently recalculated, native JSON and NPZ present, and every trial's terminal action, actual SDK state, level counters, scorecard numeric fields and terminal-frame shape checked. No API key, GUID or private scorecard identifier appears in the retained report.

## Decision and next worker

The evidence rules out **calling any of these eight terminal episodes a WIN**. The original public-game returns a native **loss/termination state `GAME_OVER`**, although one complete level may have been credited before it occurred. What exact game mechanics trigger this state is still an *unproved causal explanation*.

The verified visible one-step full 64×64 transition relationships from preceding stage0/1 experiments remain valuable **within their earlier sampled domains**, but reconstructing visible frames is not equivalent to choosing a policy that completes six levels. Do not publish an ARC game success, competition score or original mathematical F3 rooted correspondence from this experiment.

**Next precise experimental and implementation boundary:** harden the shared original-native runner's terminal contract: preserve the first complete terminal state and its original frame; cease stepping on `WIN` or `GAME_OVER`; distinguish `NATIVE_TERMINAL_WIN`, `NATIVE_TERMINAL_GAME_OVER`, `UNKNOWN_NONSTANDARD_FRAME`, action withdrawal and real level-change events without claiming unobserved transitions. Add synthetic contract tests and a real native independent test; evaluate any changes to historical frame admission denominators separately before changing canonical research records. After that, investigate genuinely different game actions/objectives needed for 6/6 levels without inventing hidden mechanics or rewriting source F3 mathematics.

Original forty-eight F3 source laws and the canonical ARC agent are preserved.
