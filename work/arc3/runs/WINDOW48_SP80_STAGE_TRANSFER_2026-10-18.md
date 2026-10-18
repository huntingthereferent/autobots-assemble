# Original Window48 — SP80 native stage-transfer test

This investigates actual PUBLIC ARC-AGI-3 SP80 under official arc-agi Arcade NORMAL. The original 48-law F3 WindowCombined mathematics and its marked/rooted 16-class versus full-state 14-class distinction are unchanged. The historical nine-world model is not part of this experiment.

## Previous verified observation

[Prior SP80 native composite witness](WINDOW48_NATIVE_COMPOSITES_SP80_2026-10-17.md): native word 454545 (ACTION4 and ACTION5 repeated three times) advanced the real public game from levels_completed=0 to 1 on action six in 2 of 2 independent resets; native game state NOT_FINISHED. This was authentic one-LEVEL progress, not a complete ARC game win and NOT an F3 A generator (original F3 A³ is identity).

## New predeclared experiment and raw evidence

- [Successful native stage-transfer run #39099362353](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39099362353).
- [Per-action native frame stacks, raw source observations and JSON](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39099362353/artifacts/12125748140) (14-day GitHub Actions retention).
- [Native executable](../native_sp80_stage_transfer.py), [GitHub CI](../../../.github/workflows/arc3-sp80-stage-transfer.yml).

From 22 independent new game resets, execute the previously witnessed 454545 prefix, REQUIRE native 0->1, then test one predeclared level-1 suffix. Eleven suffixes were tested twice each: empty, 4, 5, 45, 54, 4545, 5454, 454545, 545454, 444444, 555555. Raw 64x64 color values, exact frame hashes, color counts, changed-pixel masks, source-level counters and terminal state are retained. No game engine source, stored solved route, F3 modulo projection, or fabricated native game is involved.

| Measured result | Count |
| --- | ---: |
| Independent full native resets | 22 |
| Actual native environment actions | 208 |
| Reproduced 0 to 1 level prefix | **22/22** |
| Distinct level-0 initial full frames | 1 |
| Distinct level-1 initial full frames | 1 |
| Level-1 suffix 454545 completes level 2 | **0/2** |
| Native second-level advances in all tests | **0** |
| Post-level tests completing with no level 2 | 20 |
| Post-level tests interrupted by nonstandard frame | 2 |

The two interrupted suffix tests involved repeated native ACTION5; they remain UNKNOWN and are not used as evidence that the action never causes level progress.

**Result:** the known level-0 progression word 454545 does NOT transfer directly to level 1. Both fresh replays of a second 454545 leave actual levels_completed at 1.

## Measured pixel relationships

The level-0 and level-1 starting observations differ at exactly **1,136 native pixels**. The entire exact old-to-new color change table is included in the JSON; its full difference bounding box is (0,0,63,63), and the source pixel/color differences are IDENTICAL across all 22 reset trajectories. The level-1 frame is independently repeatable but not equal to the level-0 frame.

Under the SAME ordered suffix 454545, stage-specific per-step pixel effects are:

| Step | Actual action | Level 0 changed pixels | Level 1 changed pixels | Level 0 changed bounding box | Level 1 changed bounding box |
| --- | --- | ---: | ---: | --- | --- |
| 1 | 4 | 34 | 33 | (12,0,63,19) | (0,36,43,63) |
| 2 | 5 | 2 | 2 | (60,0,61,0) | (1,63,2,63) |
| 3 | 4 | 34 | 33 | (16,0,59,19) | (3,36,47,63) |
| 4 | 5 | 3 | 2 | (55,0,57,0) | (4,63,5,63) |
| 5 | 4 | 34 | 33 | (20,0,54,19) | (6,36,51,63) |
| 6 | 5 | 1168 | 2 | (0,0,63,63) | (7,63,8,63) |

At stage 0 the sixth action changes the full board by completing a native level. At stage 1 the same sixth action only changes two observed pixels and does not advance the native level counter.

An observation-grounded *next question* is whether the upper-to-lower change in these affected regions admits any consistent spatial transformation. The different action-4 pixel cardinalities (34 versus 33) already rule out an **exact bijective** pixel permutation mapping those stage-0 changed-pixel sets to stage-1 changed-pixel sets. No reflection, rotation, affine identification, hidden-state map, or F3 conjugacy has been demonstrated.

## Boundary

This record supports real native state-dependent effects and a failed word transfer between two observed game levels. It does NOT prove the game has an F3 state/action realization, satisfy the source A³ identity, establish one of 16 rooted mathematical classes, solve the full ARC game, or imply a competition result. The canonical 48-law agent is unchanged.

Next admissible mathematical work must derive a source-witnessed state/action relation; separate empirical progress from algebraic correspondence. A predeclared visual geometry test may refine the native observation without being promoted to a mathematical field mapping.
