# ARC / SK48 — public-controls A/B continuation (2026-10-08)

## Current witnessed result

The existing 280-action SK48 route, including 13 ACTION6 switches in Levels 6-8, was replayed from native public SDK observations in two fresh runs.

- Local SDK: **8/8, WIN, score 100.0**, each run 280 actions.
- Level completion action indices: **14, 44, 77, 104, 169, 205, 256, 280**.
- Public A/B replay versus the earlier source-assisted baseline: **all 280 returned frames identical**.
- Public control-location recognizer: finds the two 6x6 bordered sprites directly in the 64x64 frame.
- Visual motion after directional actions assigns which key is active (15 control-0 and 9 control-1 witnessed movements in each fresh causal-control replay).
- When neither recent motion nor action history distinguished the active control at the first Level-8 switch (action 259), a provisional **level-start control 0** hypothesis was applied, then tested by the actual remaining actions and successful Level-8 completion.
- Other ACTION6 clicks follow the observed selected key from the preceding switch or directional movement.

## Integration with existing Continuity A/B agent

A separate fresh 280-action game run registered a real `ARCFrameObservationProvider("sk48")` with `EcosystemService(native_observer=provider)`. It activated a distinct existing `AgentLineage` handoff for each of the 13 SK48 switch actions and supplied the actual native before/after frame pair after each action.

All **13/13** native switch observations produced:
- `ExecutionResult.status = COMPLETE`;
- `ab_state = MOVE`;
- exactly one native `movement witness` admitted through the existing lineage;
- no duplicate execution.

None was `PARTIAL` or `UNKNOWN`. Source hashes and before/after locators are preserved in `sk48_native_to_lineage.json`; the temporary runtime journal was not deployed.

The integration does **not** claim that the evaluator planned the direction actions. It observed switches, tracked effects, and verified native movement. It does not attest independent operator-selection predictions or close all task loops.

## First counterexample and correction

The initial frame-only heuristic assumed no active key after level transition and clicked the first visible key at action 174. The successful baseline instead had key 0 active; clicking key 0 left the desired route, producing 140 distinct output pixels relative to the correct transition. The corrected hypothesis selected the other visible key and restored exact frame equality through all 280 moves.

A stricter motion-first controller later reached a genuine `UNKNOWN` at action 259 of Level 8: the first two directional actions failed to reveal the current selected key. A reset-to-key-0 hypothesis, grounded in earlier witnessed level starts, continued to 8/8 twice. The hypothesis is **game-specific evidence, not a universal rule**.

## What survives / next edge

Survives:
- one A/B evaluator contract;
- native public observations and provenance;
- prior `AgentMove` / `AgentLineage` / `Handoff` boundaries;
- witnessed control-switch transitions across a second game;
- exact frame equality with earlier private-assisted reference replay.

Still unknown:
- a public-only policy that *discovers* the 280 directional moves in SK48;
- how to infer the level-start selected key without a reset hypothesis when direction probes do not disambiguate it;
- general transfer to held-out games under the same action budget;
- an official competition submission (none made).

## Local evidence files

- `_tmp_sk48_public_switch_diagnostic.py` — public-frame sprite witness plus private *audit-only* landmarks.
- `_tmp_sk48_public_switch_route.py` — public-frame selection with explicit learned reset convention; two fresh 8/8 runs.
- `_tmp_sk48_public_switch_ab_compare.py` — finds first counterexample and confirms 280/280 frame equality (baseline reads engine internals for *audit only*).
- `_tmp_sk48_public_causal_controller.py` — active-control inference from public motion, two independent 8/8 runs.
- `sk48_public_causal_280.json` — milestone, click, hypothesis and score record.
- `_tmp_sk48_native_to_lineage.py` — native ARC->Continuity A/B evaluator witness run.
- `sk48_native_to_lineage.json` — all 13 native locator pairs, observations and admitted witness references.

These are local evidence-stage files only. The current GitHub main and competition agent have not been modified by this continuation.
