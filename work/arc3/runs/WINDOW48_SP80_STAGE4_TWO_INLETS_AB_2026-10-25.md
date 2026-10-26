# ARC4 — original SDK success/failure boundary and two-source A/B audit
**Research date:** October 25, 2026 · **Scope:** genuine native SP80 original SDK. This is an observed-source experiment, not a solver proof or reconstructed private engine.

## Why cup fill and visual warning timing are not an objective

A read-only audit of [genuine Stage3 source frames, artifact #12352298969](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39616395169/artifacts/12352298969) covers 25 frozen original SDK Stage3 configurations. Their real outcomes and complete original 64×64 frame stacks support:

- The **one official Stage3→4 positive control** `catch_left3_up5` had all four genuine cup windows completely filled during returned animation frames27–28, then visibly changed to its next level. There was **no palette1→14 bottom-border transition** in the source frames before that official advancement.
- **17 other Stage3 controls** also had all four source cup windows completely filled for 7–8 frames, yet remained Level3. Each of these 17 did display a 180-pixel lower-border palette1→14 transition during its ACTION5 animation. Three further unsuccessful controls did *not* show this transition, but also did not fill all four source cup windows. These are finite observations; they do not establish that warnings cause or prevent success.

A separate read-only audit of six genuine Stage4 source experiment archives ([examples in the prior ARC4 investigation](WINDOW48_SP80_STAGE4_UPSTREAM_JUNCTION_2026-10-25.md)) found 50 original full-four-cup animated POUR sequences; **22 source sequences had all four cups filled before the first palette1→14 border transition** on any of the four measured outer borders (top/right/left/bottom), yet did **not** advance officially. Because repeated independently entered cases and configurations appear in more than one artifact, 22 is a **source sequence count**, not an independent experiment count.

Therefore `four_cups_full`, `four_cups_full_before_any_border_warning`, and `full_four_cup_duration` are all empirically **insufficient** as native SDK advancement criteria in the tested configurations. Original progress is **only** `levels_completed>=5` or `WIN`.

## Concrete Level4 source structure

The actual source-root 64×64 board at official Stage4 entrance contains two bottom palette6 patches, **A = x20–22,y56–58** and **B = x44–46,y56–58**. In the original native four-cup-complete frame from the `BASE` geometry, both patches belong to **one 4-neighbor-connected palette6 component**. The same single-component condition was verified across **88 first/next full-four-cup source frames** inspected in six retained original SDK experiment archives. These 88 contain repeated source geometries; no global connectedness claim follows.

This gives a candidate *geometrical A/B question*: can a native geometry support all four filled cups while separating the two source-connected paths? Such a configuration has not been witnessed. **It is not established as the hidden success condition**, and prior control moves often lose a cup before separating the flow.

## Fresh original SDK two-inlet selection controls

[Successful native Actions run #40271130743](https://github.com/huntingthereferent/autobots-assemble/actions/runs/40271130743) · [complete true original frame arrays and JSON #12628356360](https://github.com/huntingthereferent/autobots-assemble/actions/runs/40271130743/artifacts/12628356360) · [frozen executable original SDK protocol](../native_sp80_stage4_dual_inlet_contact.py).

The experiment fixes the verified **21-action Level4 four-cup geometry** and tests seven predetermined source interactions: no extra ACTION6; click real source A at (21,57); click real source B at (45,57); click A then B; click B then A; click palette12 background at (28,54); and reselect the genuine palette8 movable bar at (15,48). Every click's actual palette and coordinate is recorded and checked against real source pixel arrays. Two independently reset original SDK entry histories per condition produced **14 genuine original games**, every one returning `Level4/NOT_FINISHED`; no Level5/WIN.

**Exact results:** Every original POUR returned a 32×64×64 frame stack with four cups full in animation frames23–30; both original bottom source A and B were in the same single palette6 connected component of **675 source pixels** at first four-cup completion. Full returned 32-frame animation **outside bottom clock row y63 was identical byte-for-byte across all seven conditions and both original entry histories**. Only the y63 time counter differed, and the selected movable bar reclick altered the pre-POUR source selection highlight but not fluid animation. Original first upper/right border signals at frame20 were unchanged. Neither blue source point responded to ACTION6 in a way that altered the native observable fluid path.

This is a **negative causal test** for directly selecting the two source pixels in the currently verified root geometry. It does **not** prove the two inputs are physically identical, nor show that a disconnected flow is the objective; the genuine SDK may have other geometric interactions.

## Explicit referent and handoff

Keep `(true native original Stage4 entry, marked source action history, full original 64×64 pre-action image, action including exact ACTION6 coordinates, returned complete frame stack, official SDK level/state)`. Distinguish the **finite A/B observational quotient** (palettes, connectivity, clock) from the **verified exact mathematical rooted/nonrooted F3-48 certificate**; no mapping between six SDK labels and abstract A/B is proved.

**Next discriminating test:** pick a *source-grounded, currently manipulable* bar that forms or breaks an actual palette6 connection between lower input A and B. Compare exact source paths/cup reachability in one bounded original SDK A/B, rather than blanket search by cup-fill counts. A successful test would either (a) witness **two disconnected inlet components while preserving four full cup windows** or (b) falsify that geometry proposal for the chosen bar. Only a real SDK level>=5/WIN proves advancement. Stop invoking direct ACTION6 at non-movable inlet pixels: their measured source flow effect is null. Time-shifts and repeated four-cup controls have also been ruled out in the previous reports.

No changes to the original F3-48 mathematical laws or canonical agent. PR #537 remains open and unmerged.
