# Native ARC-AGI-3 saved-action evidence

*Extracted and normalized from `arc3.rar`, October 10, 2026.*

## Provenance

These three JSON documents contain actual saved action sequences from the uploaded local research archive. The uploaded files are the source of the numbers and route data; **the JSON files here are normalized selections, not byte-for-byte copies**, and their `origin_sha256` values (where available) identify the corresponding original local JSON files.

| Game | Saved action route | Local report | Qualification |
| :--- | :--- | :--- | :--- |
| [FT09](ft09_route.json) | 75 coordinate clicks / 6 levels | WIN, 6/6, score 100 | Source-assisted solver; [original report on profile](https://github.com/huntingthereferent/huntingthereferent/blob/main/SELECTED_WORK.md) |
| [LS20](ls20_route.json) | 309 native actions / 7 levels | WIN, 7/7, score 100 | Saved replay, not independent first-contact solving |
| [SK48](sk48_route.json) | 280 action IDs / 8 levels | WIN, 8/8 | Saved route uses private SDK state for ACTION6 coordinate selection |

The [archived local SK48 causal report](https://github.com/huntingthereferent/huntingthereferent/blob/main/ARC_EVIDENCE.md) explicitly marked its 280-action runs `not_independently_solved`. Source-assisted and replay evidence must not be promoted into independent autonomous-game capability.

## Mathematical feasibility boundary — no agent required

[**Observation sufficiency theorem and synthetic counterexample**](OBSERVATION_SUFFICIENCY_PROOF.md) · [Pure-Python finite checker](observation_sufficiency.py) · [Six offline tests](../../network/tests/test_arc_observation_sufficiency.py).

This separate research lane proves a criterion for when the current observable state can support exact deterministic A/B transitions and gives a history-dependent counterexample. It does **not** run ARC, change game policies, reuse winning action routes, or prove a new ARC win. A native game-specific witness remains open. This mathematical work is independent of the paused, more expensive ChatGPT Run agent experiment.

## Replay interface

[Replay source](replay_saved_paths.py) drives ARC's native `Arcade`/ `GameAction` SDK with the saved routes and compares actual returns to recorded milestones:

```bash
python -m pip install arc-agi
python research/arc_native_runs/replay_saved_paths.py ft09
python research/arc_native_runs/replay_saved_paths.py ls20
python research/arc_native_runs/replay_saved_paths.py sk48
```

**FT09 causal solver source:** [Visible-frame causal agent](ft09_visible_causal_agent.py) reconstructed from the archived local implementation, with only the absolute Windows vendor path removed and the runnable loop placed under `__main__`. It derives actions from observed frames rather than consuming the saved route; its local claims have not been reproduced in this transfer environment. Requires the ARC-AGI-3-Agents package on `PYTHONPATH`.

**Independent negative controls:** [Autonomous public-frame trial outcomes](AUTONOMOUS_TRIALS.md) report SK48, LS20, and AR25 trials that did not win. Different actor/policy, different result.

**Archived replay script sources:** [LS20 replay transcription](original_ls20_complete_replay.py) · [SK48 replay transcription](original_sk48_complete_replay.py). Their action tuples were checked against the uploaded archive's saved route data. These are source transcriptions rather than byte-for-byte uploads; the original archive retains the source files. The SK48 script reads engine-private controller data.

The exact SDK dependencies and permitted engine interfaces must be supplied. **These commands were not executed in this artifact transfer environment.** A route is a reproducible input; independent verification requires executing it against a compatible native SDK and retaining actual outputs/scorecards.

The SK48 route depends on game-private objects in the archived replay and may not execute under other SDK versions. It should not be represented as a general public-only controller.

## Evidence level

- **Available in this repository:** saved level-by-level action sequences and executable replay code, with original-local-file provenance.
- **Not yet included here:** full per-step observation frames, original solver-development history, native SDK binaries, complete scorecards, and a captured verification run under the present repository revision.
- **Different result:** the independent `AB_CYCLIC_AUTONOMOUS` experiment had separately recorded runs ending without full-game wins; those must not be confused with these saved-route completions.

[Public ARC evidence index](https://github.com/huntingthereferent/huntingthereferent/blob/main/ARC_EVIDENCE.md) · [Existing native observer](../../runtime/arc_native_observer.py) · [Mathematical construction research](../../work/arc_like_maze/README.md)
