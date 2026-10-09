# ARC / SK48 — Native A/B Level 2 completion and Level 3 transfer
2026-10-08. Local evidence stage only. No GitHub merge or official competition submission.

## Verified status

- Independent native public-only Level 1 discovery: 14 actions on a single native game with acknowledged RESET/replay; this was previously witnessed.
- Native Level 2 completion using a reference-assisted A/B macro family: 8 distinct Level 2 action routes, 30–34 actions, each independently replayed twice in newly created native SDK game instances. 16/16 trials advanced from Level 2 to Level 3.
- Seven of those eight Level 2 action routes differ from the old saved Level 2 route. Shortest novel alternative: 31 Level 2 actions.
- Level 3: successfully entered through a validated alternative 31-action Level 2 path, with public sensor and immediate native action probes. No Level 3 solve yet.
- Older complete SK48 8/8 WIN, 280-action saved-route replay remains regression evidence. This work does NOT establish blind independent solution of all 8 levels.

## Source and methodology disclosure

A previously saved positive Level 2 execution was consulted separately as a regression reference to identify the visual ordered-color goal and necessary retract moves. Candidate macro generators did NOT read the original Level 2 action list as their execution plan. Thus the new Level 2 result is reference-assisted generalization with alternatives, NOT blind independent discovery.

The public native color sensor, _sk48_public_goal_sensor.py, extracts the 6x6 control head, bottom reference legend [8,12,9,14], and the colors actually visible on the moving structure. Calibration against successes and failures established that removing all colored tiles is not enough: attached color order must be correct.

## Counterexample preserved: action phase

Visually identical states can have different native next-action behavior following directional-action or undo histories. At the Level 2 entry, four phase classes were witnessed; 768 three-action native continuations across three source-history variants per class produced zero within-phase conflicts. One-step undo was NOT safely compositional after chained actions, and the old undo-optimized checkpoint was quarantined.

Native RESET requires explicit levels_completed==0 acknowledgement. Replay must verify the exact public parent frame before admitting any branch. A/B keeps the witnessed action relation whenever frame-only aliases diverge.

Evidence: SK48_NATIVE_PHASE_AB_REPORT_2026-10-08.md and sk48_l2_ab_recursive_phase_quotient.json.

## Observed goal and action-selection correction

Native Level 2 reference legend: 8 → 12 → 9 → 14.

A greedy 24-wide public goal beam stalled at prefix 1 through search depth 21; a geometric 444 seed stalled at prefix 1 through depth 16. Separate positive-control analysis found why: extending the structure increased the greedy score, but two necessary retract moves decreased it. This is a policy counterexample, not a board impossibility.

From a first-color state produced by that native beam, bounded native A/B search tested all action continuations through extra depth 4. It discovered the second color at additional actions [4,3,3,1], extending the native Level 2 partial path to [4,4,4,1,1,4,4,1,4,3,3,1]. No witness arose at additional depths 1–3.

Evidence: sk48_l2_native_second_color_ab.json and sk48_l2_goal_beam_positive_regression.json.

## A/B over movement-run operators: third and fourth colors

The next research operation parameterized movement-run lengths rather than reading one exact action list.

Third-color macro: RIGHT^a, LEFT^b, UP, RIGHT^c, UP, RIGHT, DOWN, with a=1..4, b=1..6, c=1..3. Native 72-candidate A/B: 21 reached the public [8,12,9] color order. Multiple distinct run parameters converged to identical returned frames.

Fourth-color macro: RIGHT^a, LEFT^b, DOWN^c with a=1..3, b=1..4, c=1..3. Four distinct witnessed third-color endpoints, 144 native tests. Fourteen reached [8,12,9,14]; eight completed Level 2 after up to three further rightward actions.

Evidence: sk48_l2_native_macro_third_color_ab.json; sk48_l2_native_macro_fourth_color_ab.json.

## Fresh native completion verification

Eight complete generated Level 2 routes replayed twice each in freshly instantiated Arcade instances. All 16 native runs advanced exactly to levels_completed=2 at the expected route end.

Route lengths: 32, 33, 30, 32, 31, 33, 32, 34.
Routes different from old saved Level 2 route: 7 of 8.
These are native level completion checks, not official competition wins or a generalized solver for all levels.

Authoritative route arrays, hashes, and trial results: sk48_l2_fresh_macro_completion_witnesses.json.
Test implementation: _tmp_sk48_l2_fresh_macro_verify.py.

## Transfer to Level 3: current native boundary

Entered Level 3 using a fresh verified 31-action alternative Level 2 route.
Native public entry: levels_completed=2, bordered head at x=5 y=42, same bottom legend [8,12,9,14].
At Level 3 root, native ACTION1 moved the visible head to y=36 with 96 changed pixels; ACTION2 returned the same frame; ACTION3 and ACTION4 changed 12 pixels each. An additional color-11 motif (4 pixels) appears on Level 3 board.

The visual goal reference and control format transfer, but Level 3 board layout and this additional motif require new native A/B checks. No saved Level 3 route was loaded by the Level 3 transfer probe.

Evidence: sk48_l3_public_goal_sensor_transfer.json, _tmp_sk48_l3_public_transfer.py and _tmp_sk48_l3_public_ref_count.py.

## Next edge

Use the existing Continuity A/B evidence contract, not another agent architecture. Preserve current public frame, witnessed directional phase, action causality, and target color order; build and test a Level 3-specific movement-run operator family against native Level 3 observations. Do not promote a solve absent levels_completed=3. No GitHub writes or official ARC submission have occurred here.

All research-stage files are local under C:\Users\teepa\arc3\AB_ARC_EVIDENCE.
