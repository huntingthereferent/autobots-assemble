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


## Follow-up: actual two-source junction intervention vs ineffective lower-bar motion

**Native source evidence (all genuine normal SDK from verified Stage0→4 entry):**
- [Successful right-middle gate A/B run #40315154593](https://github.com/huntingthereferent/autobots-assemble/actions/runs/40315154593), [full original 64×64 frame arrays/receipts #12646576816](https://github.com/huntingthereferent/autobots-assemble/actions/runs/40315154593/artifacts/12646576816), [executed source](../native_sp80_stage4_right_gate_connectivity.py).
- [Successful lower-bridge bar A/B run #40315876524](https://github.com/huntingthereferent/autobots-assemble/actions/runs/40315876524), [actual original frame arrays/receipts #12647041827](https://github.com/huntingthereferent/autobots-assemble/actions/runs/40315876524/artifacts/12647041827), [executed source](../native_sp80_stage4_lower_bridge_cut.py). The first submission #40315695411 failed on an unnecessary `scipy` import before any native SDK game; it was replaced with standard-library/NumPy 4-connected-component traversal, and the frozen actual SDK conditions succeeded unchanged in the second run.

### 18-game right-middle gate test: distinct water geometry, same inlet connection

Fixed original 21-action four-cup source configuration `BASE`, then genuinely select native palette8 right-middle bar at original SDK position x42,y33 and move it one or two steps (UP, DOWN, LEFT, RIGHT, DOWN+LEFT/RIGHT). One baseline and one reselect control. Nine distinct prospectively frozen programs × two independently reset actual original Stage1 entry histories = **18 genuine SDK games**; all stayed `levels_completed=4`, `NOT_FINISHED`, zero Level5.

At original returned ACTION5 frame23 under the ordinary four-cup geometry, the measured source palette6 water band x35..55/y35..37 contained **63 palette6 pixels**. Genuine right-middle bar UP1 produced just **9** palette6 pixels in that band while *still* fully filling all four original cup windows at frames23–30. DOWN1/DOWN2 gave **18** pixels with the same four-cup timing; LEFT1 gave 54 pixels, with four cups full later at frames25–32. RIGHT1 removed four-cup completion. Every observed full-cup frame in each case still had **one 4-neighbor-connected palette6 component containing both original bottom patches**. The two source patches can be disconnected before flow reaches them or in the post-animation cleanup frame; that is not equivalent to two disconnected inlets while all cups are simultaneously full.

A read-only independent graph walk through the archived actual returned frames identified the **alternative lower bridge** that makes the UP1 result unsurprising: after the upper junction band is nearly depleted, native palette6 still traverses **approximately x32–45/y44–46**; both bottom source patches retain a path through this region. Do not call x35..55/y35..37 the only connecting channel.

### 16-game lower-bar alternative-bridge intervention: source water invariant

Using real right-middle gate UP1 as common A/B parent, the source SDK next selected the actual lower palette8 bar at x15,y48 (source component x11..19/y47..49) and froze alternative sequences RIGHT4/RIGHT5/RIGHT6, UP1/UP2 and order reversal. Eight fixed conditions (including gate-only/reselect controls) × two separate genuine original entries = **16 SDK games**, all officially Level4 NOT_FINISHED, zero Level5/WIN.

The original before-POUR source shows the bar genuinely moved onto the proposed lower bypass area: e.g. source selected palette9 component **x26..34/y44..46**, **x29..37/y44..46**, or **x29..37/y41..43**. All eight original flows filled all four cups beginning at returned frame23, and both inlets stayed in one connected source palette6 component at every four-cup-full returned frame. The graph remained separated at early empty stages (frames0–16) and frame31 as normal, which does not count as a four-cup/flow disconnection.

**Important independent raw NPZ audit:** comparing each entire **32×63×64 nonclock** SDK animation to the common gate-UP1 baseline, the lower-bar **reselect-only** case had zero differing pixels; moved-bar cases showed 1,728–1,773 nonclock changed pixels caused by the changed rendered bar positions. However the exact Boolean array `(source_palette == 6)` across **all 32 frames excluding y63** was **bitwise identical** in **all eight lower-bar conditions**, including the attempts overlapping the visible lower bridge. Consequently these lower-bar moves changed **rendered movable geometry** without changing the actual source palette6 flow topology in the tested setting. Do not infer a physical cut from visual overlap with a palette6 stream.

### Mechanism limit / best next action

The only nearby object in these tests **demonstrably changing the original source palette6 water graph** is the genuine right-middle movable bar. Yet UP/DOWN/LEFT controls have not separated both live source inlets while retaining four full cups, and no source observations establish that separating streams is a winning criterion. Avoid another unguided parameter grid to chase disconnection.

A genuine next Level4 candidate must be grounded in a new source feature **that actually affects the returned water mask and predicts official advancement**, not simply pixel-window cup fill, clock timing, direct ACTION6 inlet clicks, or movable bars drawn across a stream without changing its source6 trajectory. Preserve full original SDK returned frames, root and action words, and explicit F3-48 mathematical referent separation. The truthful conclusion is still **Level4 unresolved**.


## Oct 26 A/B correction: where the two sources actually join

Re-examining the **saved original SDK 64×64 source frame at first four-cup completion t23** in [artifact #12646576816](https://github.com/huntingthereferent/autobots-assemble/actions/runs/40315154593/artifacts/12646576816) revealed that the earlier narrative calling **x32..45/y44..46 a cross-inlet "lower bridge" was incorrect**. It was a spatially nearby part of the right inlet's own vertical stream, **not a water connection running horizontally between the two inlets**.

Native original source palette6 rows **y44–46** at full-cup t23 contain only **x20–22 and x44–46** source pixels, disjoint at those rows. A direct four-neighbor breadth-first search on the *actual* native palette6 mask from A=(x21,y57) to B=(x45,y57) gives an **88-edge shortest source path** through **x29–34 at y25**, the genuine **upper-middle shared horizontal route** underneath the movable upper bar originally x29..40/y20..22. The baseline and right-middle-gate-UP1 paths both have this exact 88-edge length and measured crossing. Therefore the earlier lower-bar attempt was **not targeted at an actual A/B cross-inlet edge**, which explains why moving that bar did not affect even one source6 flow pixel.

The research is now grounded in this corrected original path, and the new [upper-bridge-plus-right-middle compensation source protocol](../native_sp80_stage4_upper_bridge_compensate.py) tests the relevant junction using the genuine original SDK. No synthetic engine, no F3/native mapping, and no implicit win criterion is introduced. Only original SDK `levels_completed>=5`/WIN counts.
