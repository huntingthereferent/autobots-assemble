# ARC / SK48 — Native A/B Level 5 completion, Level 6 transfer
2026-10-08 · evidence on authorized desktop · no GitHub merge, no official ARC submission

## Level 5 result

Stage entrance was generated through previously native-verified alternative action histories:
- Level 1: 14 actions, original independently generated single-stream native public route.
- Level 2: 31 actions, previously verified alternative route (reference-assisted).
- Level 3: 33 actions, previously verified reference-assisted alternative route.
- Level 4: 27 actions, reference-assisted adjacent-swap alternative.
- Each stage stops at the FIRST native levels_completed threshold; later candidate-list actions are discarded, never spilled into the next stage.

Level 5 native root SHA256:
32a1754a30999e08b85b9ad7d81678965cefe3c4893f09c0b1587e404a3a53ab

The previous generic color detector returned UNKNOWN because it expected four distinct legend colors. Actual native public Level 5 reference appears in row 57 as three color symbols:
8 -> 9 -> 8
There are three color-9 objects at x=12,18,24 and three color-8 objects at x=36,42,48 (all initially sharing y=25..28). The moving structure initially holds the left-side 9 group. Native ACTION1 raises that group, ACTION2 lowers it, ACTION4 initially preserves the public frame while aligned with the obstacle, and ACTION3 causes a small frame change. Level 5 is therefore a two-color-object rearrangement problem, NOT a four-distinct-color arrangement.

A separate OLD SAVED positive Level 5 route was used for calibration, explicitly as reference evidence rather than blind discovery. It consisted of 65 action inputs and passed native Level 5 completion at action 65 in 2/2 fresh games through the corrected alternative upstream stage route.
Evidence: sk48_l5_saved_positive_control_calibration.json.

Native A/B single-action deletion screen from the positive route:
- All 65 one-action deletions individually tested after acknowledged RESET and exact Level 5 entry replay.
- 0/65 deletions preserved native completion.
- Does NOT establish globally shortest route.
Evidence: sk48_l5_native_single_delete_ab.json.

Native A/B adjacent-action order intervention:
- 35 nontrivial swaps of adjacent DIFFERENT action values tested.
- Seven native-completing variants: swap indices 7,10,32,37,40,42,47.
- All seven still took 65 actions to complete.
Evidence: sk48_l5_native_adjacent_swap_ab.json.

Fresh-replay validation:
- Each of those seven variants tested TWICE on newly created native Arcade games with varied previously verified Level2 / Level3 / Level4 routes.
- All 7/7 variants passed; 14/14 fresh games advanced from Level 5 to Level 6 at Level 5 action 65.
- All had the same correct native Level5 entrance hash.
- These are reference-assisted local A/B variants, NOT blind Level5 solving or a claim about official competition status.
Evidence: sk48_l5_native_fresh_swap_witnesses.json.

## Level 6 native entry

Using the FIRST of the seven freshly verified Level5 alternative routes and native first-completion stage handoffs:

Native stage consumption lengths:
[14, 31, 33, 27, 65]

Native Level 6 entry levels_completed = 5.
Public frame SHA256:
9b190480212bb01f8732c6f56d7910f15d0a845b2f4ae42bc12886bfee11b060

The Level6 public frame has:
- A lower selectable control head (6-colored border) at x=5,y=26.
- An upper selectable control head (15-colored border) at x=29,y=2.
- Native color-9 pieces in the upper-right playfield and color-8 pieces lower-right.
- Two reference displays at the bottom, one for a repeated 9 group and one for a repeated 8 group. Do not claim the exact Level6 win predicate before observing native completion.
- Four native direction probes made from the correct reproduced Level6 entry. All returned levels_completed=5 (Level6 still active).
Evidence: sk48_l6_native_public_entry.json.

## Level 6 A/B active-control intervention

The earlier generic public sensor scans from y=6 and therefore missed the upper 15-bordered head at y=2. An additional native public pixel scan for the 15 border found its position without reading private game state.

Native ACTION6 click at x=31,y=4 (chosen from the visible upper control's observed head) changed 104 public pixels. Subsequent action effects clearly diverged from identical-direction moves under the initial lower control:

- ACTION1 / lower: 96 central-region pixels changed; upper selected: 12 upper-region pixels changed.
- ACTION2 / lower: 84 central plus 12 bottom pixels changed; upper: 8 upper and 4 central pixels changed.
- ACTION3 / lower: 12 central-region pixels changed; upper: 96 upper-region pixels changed.
- ACTION4 / lower: 12 central-region pixels changed; upper: 96 upper-region pixels changed.

Therefore, the Level6 future operator cannot be predicted by a frame-only directional control model that ignores which head is active.

Evidence:
- sk48_l6_public_native_control_switch.json
- _tmp_sk48_l6_switch_which_moves.py (native stdout region-delta controls)
- _tmp_sk48_l6_public_switch_probe.py (public pixel-selected ACTION6 click)

## A/B continuity and next boundary

The existing one-agent / Continuity evaluator should retain:
native frame + selected public control + observed color-object geometry + action history/phase when predictive counterexamples require it + exact first-completion stage handoff.

Unknown Level6 goal relation must not be conflated with evidence for the earlier Level5 8,9,8 pattern. The next native experiment is to move each selectable head through independently witnessed movement runs, model what moves on the other side, and test whether both color groups can be individually collected/sorted. Do not import a saved Level6 route as a search plan; positive prior evidence may be separately audited and must be labeled reference-assisted.

OLDER saved SK48 8/8 run remains separate regression evidence. No new GitHub repo or competition submission modifications were made.

All research files:
C:\Users\teepa\arc3\AB_ARC_EVIDENCE
