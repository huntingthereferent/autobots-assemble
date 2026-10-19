# WORLD / A-B Physical Blueprint — original block–wall continuation, trial 01

**Research date:** 2026-10-19  
**Owner WORLD branch:** `world/w13-two-world-advance-contract-20261016`  
**Result:** independently replayed **partial physical relation recovery**, **full original blueprint NOT REPRODUCED**.

## Exact comparison referent

The owner-provided Library artwork `Visual Language A_B Exploration Blueprint.png` is a proposed physical-language cycle: LOOK → LANGUAGE → A/B → NEXT LOOK, beginning with a moving block and boundary, a contact/deflection relation, then possible accumulation into guide, funnel, diverter and spiral structures. The artwork is a *relational drawing*, not a measured fabrication blueprint.

The original 24 × 6 virtual physical WORLD remains intact. Its source wall is `boundary-wall` at cell (12,1), taken from `systems/workspace/world_physical_construction.py`. Existing original two-room W13 rules, journals, physical source geometry, source-specific historical clinical timing, and prior WORLD evidence **were not rewritten**.

## Bounded source-independent generation

Native physics generator: `systems/workspace/world_ab_contact_trial.py`.  
Playable extension inside the same physical WORLD: `docs/world_ab_contact_trial.html`.  
Independent original reference checklist (NOT input to generator): `network/tests/fixtures/world_ab_original_visual_reference_v1.json`.  
Falsification + analytic oracle: `network/tests/test_world_ab_contact_trial.py`.  
Actual Chromium browser, independent native and analytic witness: `scripts/verify_world_ab_contact_browser.py`.

A/B begins with **exactly the same** virtual rigid square, position and velocity. Branch A has no contact wall; branch B includes the source boundary. The only source physics for this bounded trial are translation on an x/y plane and one event-detected elastic or inelastic contact against the wall's west face. Mass is unit-normalized; there is no gravity, force-field, angular momentum, friction, torque, surface deformation, or real-world calibration. Inputs are bounded, numerical, and checked.

The generator does **not** receive the desired `guide`, `funnel`, `diverter`, or `spiral` categories. It emits only observed trajectory states and contact-derived relational descriptions. Those original diagram categories enter **after** source generation in a separate witness comparator. Existing static objects in the WORLD are explicitly **not credited** as generated shapes.

## Actually executed run

[GitHub Actions #39227432269](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39227432269) — **SUCCESS**.  
[Retained evidence artifact #12173844295](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39227432269/artifacts/12173844295) — SHA-256 `f66d2932d6b674f393a8a6379723f27f316fa028b37f7c1d08a01551bfa6f558`; includes self-contained playable physical-world HTML, actual Chromium screenshot, generated 17-frame-per-branch physical source report, independent comparison receipt, and original visual-reference fixture.

- **12/12 focused tests passed**: seven contact/analytic/mutation/blueprint-comparison checks and five pre-existing physical-world topology tests.
- 17 real browser-generated motion states each for `A_without_wall` and `B_with_wall` (time 0.00–4.00, 0.25-step); independent **closed-form continuous event-time collision oracle** agreed on *all* x/y positions and velocities.
- Initial position (3.0,1.35), velocity (+3.0,+0.12), square half-extent 0.25 virtual cell, restitution 1.0, source wall west face x=12 and y-span [1,2].
- A final: x=**15.0**, y=**1.83**, vx=**+3.0**, vy=**+0.12**; no collision.
- B contact at t=**2.916666667**, contact x=**11.75**, contact y=**1.70**, horizontal speed +3.0 → −3.0; B final x=**8.5**, y=**1.83**, vx=**−3.0**, vy=**+0.12**.
- Negative controls: start the block outside the collision path → **no collision**; restitution 0.5 → **normal kinetic energy decreases**; invalid motion values → browser refuses run; reset reproduces exact original case.
- Existing world source JS scripts and the 144-cell physical geometry remained **byte unchanged** within the new playable extension.

## Original visual blueprint relation recovery

| Target relationship in sketch | Newly emerged from physical simulation? |
| --- | --- |
| Approach toward boundary | **Yes** (initial positive vx and bounded separating distance) |
| Solid boundary contact | **Yes** (discrete contact event at independently verified continuous intersection time) |
| Deflection / redirected motion | **Yes** (x velocity sign change, derived from contact) |
| Next physical state | **Yes** (subsequent measured frame with new direction) |
| Self-generated guide structure | **NO** |
| Self-generated funnel structure | **NO** |
| Self-generated diverter structure | **NO** |
| Self-generated spiral structure | **NO** |

**Conclusion:** the simple world is sufficient to generate the *first block–boundary redirection* under its declared mechanics, and the independent numerical oracle verifies that narrowly. It **has not generated the full original physical A/B blueprint**. The static WORLD already contains pre-placed structures; these are **not** generated by the collision model and must not be counted as successful reproduction. There is no evidence that Earth physics is fully represented.

### Next genuine test boundary

Build **rule-derived physical composition**, not a predefined sequence of desired shapes: accumulate the contact trace, instantiate a next obstacle/collision surface only from a recovered relation, expose further motion and measure whether guide/funnel/diverter/spiral geometries can genuinely emerge. Keep the target blueprint isolated in the separate verifier; reject or report deviations rather than repairing the output toward the desired picture.

This is a bounded original-WORLD simulator/research return point, not independent certification of every mechanical phenomenon, NIH competition outcome, or user-submitted physical engineering measurement.
