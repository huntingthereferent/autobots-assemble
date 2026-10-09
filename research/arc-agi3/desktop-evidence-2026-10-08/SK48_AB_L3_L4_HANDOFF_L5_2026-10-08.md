ARC / SK48 — A/B native continuation: Level 3, Level 4 handoff, Level 5
Date: 2026-10-08
Local evidence only. No GitHub edits or official competition submission.

STATUS
Level 1: independently discovered public-native route, 14 actions.
Level 2: reference-assisted macro variation; 8 completion routes, 16/16 fresh trials.
Level 3: reference-assisted macro variation; 8 alternative routes different from old saved route, 16/16 fresh native trials to Level 4. Shortest route 33 actions.
Level 4: reference-assisted positive-action mutation; 27 deletions failed; 3 adjacent swaps survived in its native reference context. After first-completion stage gating, all 3 alternative routes passed 6/6 fresh trials to Level 5.
Level 5: native entry and immediate action probes completed. New goal relation remains UNKNOWN.
The prior 8/8 saved SK48 replay remains separate regression evidence. This report does NOT claim a blind all-level solve.

1. LEVEL 3 FALSE COLOR MATCH CORRECTED
The old frame sensor treated color in the control head's row as attached even across a blank gap. Native counterexample: UP x4 brought head to y18 and aligned color 8 on y19, but a background gap remained. RIGHT x3 after UP x4 closed the visible 1/2 body-pixel bridge to that tile. Conservative sensor _sk48_public_connected_goal.py requires unbroken native pixel connection; frame-only row alignment is not progress. See sk48_l3_public_connection_validation.json.

2. LEVEL 3 CAUSAL TRANSPORT
After attached color 8 moved DOWN, color 12 was physically pushed down as well; control reversal did not automatically restore displaced tile positions. These native observations demonstrate color-object transport and geometric interaction beyond control coordinates. The first short constrained second-color attempt tested 219 directions without acquiring a second connected target.
Evidence: _tmp_sk48_l3_color_transport_probe.py and sk48_l3_native_connected_second_color_ab.json.

3. REFERENCE-ASSISTED NATIVE MACRO A/B FOR LEVEL 3
Previous Level 3 positive history was used only in separate calibration to identify relevant spatial operators; the macro search scripts executed generated action strings, not the original saved sequence. Explicitly mark this method reference-assisted, not blind.
From native connected 8, parameterized DOWN / LEFT / DOWN / RIGHT: 138 distinct tests, 15 connected [8,12] states.
From witnessed second-color states, UP / LEFT / UP / RIGHT: 180 tests, 15 connected [8,12,9] states.
From witnessed third-color states, DOWN / LEFT / UP / RIGHT: 162 tests, 18 native Level 3 completion observations.
Source files:
sk48_l3_native_macro_second_color_ab.json
sk48_l3_native_macro_third_color_ab.json
sk48_l3_native_macro_final_color_ab.json

4. LEVEL 3 FRESH NATIVE VERIFICATION
sk48_l3_native_fresh_macro_wins.json contains 8 generated alternative full action lists. Each was played twice from newly instantiated native SDK game instances with different previously verified Level 2 entrance routes. All 16 trials reached native levels_completed >= 3. All 8 strings differ from the old saved Level 3 positive list. Some candidate strings have 1 or 2 trailing moves AFTER the first Level 3 completion; these are not part of Level 3 once the stage is complete.

5. LEVEL 4 POSITIVE-REFERENCE ACTION CONSERVATION
Initial Level 4 connected colors [9,14,8,12], target [8,12,9,14]. The positive witness rearranges spatially across rows, not by merely sorting one continuous horizontal line.
27/27 single deletions of the saved 27-action positive route broke native completion in its tested context. Of 17 nontrivial adjacent swaps, three (indices 7,8,14) preserved native completion.
Evidence: sk48_l4_positive_regression_calibration.json and sk48_l4_native_reference_mutation_ab.json.

6. CRITICAL INTERLEVEL HANDOFF FIX
First Level 4 fresh-swap experiments appeared inconsistent across different upstream Level 2/3 routes. The true cause was overrun: one or two actions were still present after the native Level 3 completion signal and were accidentally applied to Level 4. Unexpected Level 4 entry frame fc1af49b... matched a real single ACTION4 movement from the correct entry. This was a stage-boundary bug, not evidence of incompatible hidden Level 4 states.

CORRECTIVE CONTRACT: For each level, execute staged actions only UNTIL the first returned native observation with levels_completed >= intended target. Close that action handoff immediately; preserve unused action-list residue separately, never execute residue in the next level. Record the native before/after frame hashes and level transition.

Corrected experiments used different verified Level 2/3 upstream routes, truncated Level 3 tails (0,1,2 actions as appropriate) and then replayed all three Level 4 swap alternatives. 6/6 native fresh trials passed; all Level 4 entry hashes matched 4ea7e6e712f045e4..., and all alternative Level 4 routes completed at action 27.
Authoritative: sk48_l4_native_handoff_corrected.json.
The earlier failed experiment sk48_l4_native_fresh_swap_witnesses.json is preserved as a counterexample to naive handoff.

7. LEVEL 5 NATIVE ENTRY AND NEXT UNKNOWN
Entered Level 5 with corrected staged consumption lengths [14,31,33,27]. Reproducible entry frame SHA256:
32a1754a30999e08b85b9ad7d81678965cefe3c4893f09c0b1587e404a3a53ab
Native levels_completed=4. The previous four-color target legend is absent; only color-8 and color-9 clusters remain in the playfield. Palette 12/14 absent. Head (5,24); one ACTION1 changes 192 pixels, moving head to y18; ACTION2 changes 192 pixels, moving it to y30; ACTION3 changes 4 pixels; ACTION4 leaves the immediate public frame unchanged. Do not apply the old ordered-color goal to Level 5. It must be observed afresh.
Authoritative: sk48_l5_native_public_handoff_entry.json.

8. NEXT A/B OPERATION
Remain on the existing A/B / Continuity agent contract and lineage; no new agent architecture. Promote the witnessed native first-completion handoff rule and reject frame-only state aliases when their future continuations diverge. On Level 5, establish a native reference for its two-color cluster geometry, test actions against public observations, and retain UNKNOWN until a real goal relationship and completion witness exist. Preserve blind-vs-reference-assisted provenance.

Local evidence location: C:\Users\teepa\arc3\AB_ARC_EVIDENCE
No GitHub modifications or official ARC competition submissions in this continuation.
