# SP80 — held-out native spatial registration between game levels

**Date:** October 18, 2026 (America/Chicago). **Game source:** official public ARC-AGI-3 sp80 via native arc-agi Arcade NORMAL; raw original 64x64 frame pixels retained. Mathematical context is the original 48-law WindowCombined F3 construction; **no A/B native correspondence or F3 geometric projection is claimed**.

## Question fixed before intervention

[Prior native stage-transfer evidence](WINDOW48_SP80_STAGE_TRANSFER_2026-10-18.md) established that ACTION4 changes **34 native pixels at level 0 versus 33 at level 1** under the same 454545 word. The changed region moves from an upper band to a lower band after the verified level-0-to-level-1 progression. Does ONE spatial relationship, determined from the initial ACTION4 change only, predict the later change regions?

Any exact **bijective** pixel-grid transform from the complete level-0 change mask to the complete level-1 change mask is impossible because 34 != 33. A D4 symmetry combined with translation and boundary clipping is an exploratory registration, **not a full-grid conjugacy**.

## Native experiment and source record

- [Successful final native registration run #39100789840](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39100789840).
- [Original native frames, source JSON, trained hypotheses, per-pixel missed predictions](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39100789840/artifacts/12126825328) (GitHub artifact retention 14 days).
- [Reproducible native executable](../native_sp80_stage_geometry.py) and [focused CI](../../../.github/workflows/arc3-sp80-geometric-heldout.yml).

The test performed **three separate official native game resets**, each continuing the independently witnessed level-0 completion sequence 454545 and then repeating 454545 at level 1. This is **36 actual native actions**. The native roots for the new level 1 were identical on the three runs. After checking the real level counter at every action, source frames for both six-action words were preserved.

The measurement plan fixed **eight square-grid symmetries (D4: four rotations and four reflection cases including identity)**, then selected an integer pixel shift by maximizing sparse changed-mask overlap **on level-0 versus level-1 ACTION4 step 1 of reset 0 only**. The selected mapping was frozen before checking steps 2 through 6 and before the two other independent resets. A separate simpler hypothesis restricted symmetry to **identity plus translation** and was fitted from that SAME training pair. No subsequent spatial alignment was fitted to a held-out observation.

## Exact numerical results

| Measurement | D4+shift model | Translation-only model |
| --- | --- | --- |
| Selected native geometry | reflect_y then shift (+8,-8) | identity then shift (+8,+20) |
| Training ACTION4 pixels intersecting observed level-1 changed mask | 32/33 | 32/33 |
| Training source mask count / stage-1 target count | 34 / 33 | 34 / 33 |
| Training source pixels clipped off 64x64 frame | 2 | 2 |
| Training full-mask exact equality | No | No |
| Mean held-out ACTION4 F1 across steps 3 and 5, three resets (six comparisons) | **0.96992** | **0.96992** |
| Held-out exact ACTION4 mask matches | 0/6 | 0/6 |
| Mean changed-mask F1 on ACTION5 comparisons (negative controls) | 0 | 0 |
| No-shift identity baseline held-out ACTION4 mean F1 | 0 | 0 |

The first and third ACTION4 effects yield **identical predicted changed-pixel sets** under the two fitted models. On the fifth ACTION4 effect the two predictions differ in **four** individual pixel positions, but each still matches **32 observed target pixels**, with equal F1. No held-out frame gives a clear preference for reflection over translation.

Per held-out ACTION4 step on each independent reset:

| Level-local word step | Source changed pixels | Target changed pixels | Selected output overlap | F1 |
| --- | ---: | ---: | ---: | ---: |
| ACTION4 step 3 | 34 | 33 | 32 | 0.984615 |
| ACTION4 step 5 | 34 | 33 | 32 | 0.955224 |

These per-step results repeated on all three independent native resets.

The ACTION5 controls returned zero overlap with either model's projected changed-mask sets; some ACTION5 masks were clipped completely by the selected mapping, and the level-0 sixth ACTION5 triggers an entire level transition (a different class of effect). **Thus the zero is a geometric negative control only, not proof that ACTION4 and ACTION5 are different original F3 generators or that the mapping generalizes to all controls.**

## What is witnessed versus not established

**Witnessed:** a strong, repeatable **partial pixel-level registration** of native ACTION4 changed regions across public SP80 game levels, selected only from the first change and validated without refitting on later effects. Both reflection+shift and translation-only obtain 32 matched target pixels; neither yields exact equality. At least 2/34 source pixels are clipped on the earliest comparison and a native target change remains unexplained. The fifth step further distinguishes their predictions but does not establish a winning explanation.

**Not witnessed:** a unique reflection or translation; any bijective whole-board relation; correct native pixel-color transition labels under the mapping; closure on a factor under both mathematical generators; identity of hidden native states; a map between ARC and one of the 48 original mathematical laws; rooted/nonrooted WindowCombined conjugacy; advancement to game level 2; or a complete game win.

A better continuation would identify a representation from actual native data that explains the **unmatched pixels and level-dependent color/geometry changes**, then make a **new prediction** from that representation on a different observed action context. Do not silently retrofit a full F3 state isomorphism to the measured 32-pixel overlap. The original 48-law equations and canonical agent remain unchanged.
