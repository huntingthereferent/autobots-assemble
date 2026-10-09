# SK48 — Native A/B route-blind Level 2 discovery and full-chain verification

Date: October 8, 2026
Workspace: C:\Users\teepa\arc3\AB_ARC_EVIDENCE
GitHub: unchanged
Official ARC-AGI-3 competition submission: NOT performed

## Outcome

A new 30-direction-action Level 2 path was constructed entirely from
current native Level 2 action/frame experiments and the public color
reference. None of the Level 2 search scripts read a saved Level 2
positive route or a preexisting Level 2 partial-success checkpoint.

The final Level 2 action history, frozen before the reference comparison:

    [4,4,4,4,4,1,1,1,4,3,3,1,4,4,3,3,3,1,4,4,4,3,3,3,3,1,4,4,4,4]

The native SDK returned levels_completed == 2 at action 30.
Fresh independent Arcade instances confirmed 3/3 Level 2 completions;
the root and completion public frame hashes agreed across all three.

A POST-HOC comparison with the previously saved positive Level 2 action
route confirmed that these two full direction sequences differ. This
comparison was made in the downstream verification script only, AFTER
the newly generated route was frozen.

The new Level 2 path was inserted into the existing native verified
first-completion 8-stage controller; levels 3-8 used the earlier
REFERENCE-ASSISTED alternatives. Three fresh full-game tests all
returned levels_completed == 8 and native state WIN:
    Run 0: 280 SDK actions
    Run 1: 281 SDK actions
    Run 2: 282 SDK actions

This is not a blind all-level solver or an official competition score.

## Exact L2 route-blind A/B progression

The target sequence [8,12,9,14] was read from the native visual
legend. Color progress was credited only when public pixel-connected,
not merely horizontally aligned with a control.

### A. Root -> first and second color

The first native route-blind search used the previous independently
discovered Level 1 route ONLY as an entrance to Level 2.
No saved Level 2 positive or partial action path was read.

A/B retained full replayable histories, scored connected target prefix,
and kept lower-ranked alternatives alongside the best observed scores.
The native observations found:
- First connected color [8] at Level 2 action 9.
- First connected pair [8,12] at Level 2 action 14.
- Native SDK calls including resets and replays: 37,002.

Evidence: sk48_l2_route_blind_a_b_search_2026-10-08.json

### B. Two colors -> three colors

The 14-action witness was reproduced twice in fresh native Arcade game
instances, with identical public frame hashes.
A continuation search retained lower-ranked histories to permit
retraction and sideways movement.
- Found [8,12,9] at Level 2 action 21.
- Additional native SDK calls: 31,433.

Evidence: sk48_l2_route_blind_third_color_2026-10-08.json

### C. Bounded single-action beam WALL

A separate ordinary-action beam from the new three-color witness tested
seven extra action depths using 49,988 native SDK calls.
- No four-color visual target witness.
- No native Level 2 completion.
- The test preserved an explicit negative result, NOT an invented win.

Evidence: sk48_l2_route_blind_fourth_color_2026-10-08.json

### D. A/B of generic motor-action relations after the WALL

Using ONLY the newly found 21-action three-color witness, a native
A/B search enumerated generic, symmetric horizontal
extension/retraction and vertical-shift macros. It did NOT read a
saved successful Level 2 action program.

The 377th distinct macro candidate was:
    LEFT x4 -> UP -> RIGHT x4
Numerically:
    [3,3,3,3,1,4,4,4,4]

Applied to the new three-color route, this returned native
levels_completed == 2 after 30 Level 2 moves.
Macro search SDK calls: 16,784.
The returned public frame hash was the known Level 3 entry:
    7c7c422d6cacbdd9b4a7af5eb11fe5193c7b37c824f89dd776a7e7519917a334

Evidence: sk48_l2_route_blind_fourth_macro_2026-10-08.json

All four discovery experiments used 135,207 native calls combined,
including resets, parent replays and the unsuccessful beam.

## Reproducibility

The verified route and full-chain progression is recorded in:
SK48_ROUTE_BLIND_L2_NATIVE_WIN_INTEGRATION_2026-10-08.json

A reusable local one-command runner:
    sk48_route_blind_l2_runner.py

To verify already witnessed files:
    python sk48_route_blind_l2_runner.py

To rerun native A/B discovery from Level 2 (does not load an L2 solution):
    python sk48_route_blind_l2_runner.py --run

The verify-only mode PASSED in this continuation.
The --run pipeline is provided, but the full end-to-end --run replay
was not separately reexecuted after writing the runner. Individual
component experiments and the integration tests were executed and passed.

## Precise provenance and remaining limits

- Level 1 route: discovered independently in earlier native public SDK
  research; the Level 2 controller uses it as a known entrance.
- Level 2 action plan: ROUTE-BLIND with respect to saved Level 2
  action histories. All prefixes here came from its own live
  native observations and continued A/B interventions.
- Level 2 observation interpretation: PRIOR-RULE-AWARE. The public
  color sensor, connection test, action vocabulary, scoring and
  macro-generator grammar were informed by prior SK48 research.
  This is not untouched zero-shot task evaluation.
- Native state/history: full candidate paths were retained for
  actual replays. Some beam dedup heuristics use frame plus truncated
  history signatures; a universal sound Markov quotient has NOT been
  proven. Earlier frame-only and undo-shortcut counterexamples remain
  valid. The native SDK completion signal is the final win witness.
- Levels 3 through 8: earlier verified REFERENCE-ASSISTED route
  alternatives were used in the complete 8/8 integration test.
- No new repo architecture, no GitHub modifications, no ARC
  competition submission, and no proof of cross-game generalization.

## A/B continuation

The next meaningful holdout is to freeze this same visual-sensor
and native movement-operator grammar BEFORE trying a genuinely unseen
ARC-AGI-3 environment or newly reset unknown puzzle, record every
public source and action, and promote only native completion witnesses.
Do not confuse rereplaying SK48 with an unseen-task holdout.
