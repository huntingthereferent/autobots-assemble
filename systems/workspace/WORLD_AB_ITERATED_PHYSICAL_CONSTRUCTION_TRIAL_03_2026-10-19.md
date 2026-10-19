# WORLD / A-B physics — Trial 03: bounded iteration and clearance saturation

**2026-10-19 · existing WORLD branch** `world/w13-two-world-advance-contract-20261016`

## Executed native + Chromium result

[Successful original WORLD Actions run #39249863110](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39249863110) · [retained screenshot/playable HTML/native generated source and independent browser witness artifact #12185141643](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39249863110/artifacts/12185141643) · ZIP SHA-256 `4eaa3f04795c8f5c6c9504d24f1afaa6470c8dc636186897039412a612cfdbcb`.

**19/19 focused tests passed**. Native initial trajectory and new browser event history independently agreed; actual Chrome browser loaded original 144-cell W13 physical WORLD, the original wall-contact A/B experiment and Trial 02 source-composition module **unchanged**, then executed Trial 03 dynamic composition. The comparison verified the full recorded event trace, sources, event times, physical face positions and source-only activation boundaries.

- Simulation world **24 × 6 virtual units**; the original source face x=12, y=[1,2] remains unchanged.
- Square half-width 0.25; original start (3.0, 1.35), velocity (+3.0,+0.12), restitution 1.
- Five virtual seconds; **13 actual contact events**.
- **Three new physical contact faces constructed from earlier rebound events**, not preplaced and not named after desired outcomes:

| Construction | Physically derived x coordinate | Explanation |
| --- | --- | --- |
| `generated-face-1` | **9.5000** | First outbound rebound projected for 0.75 virtual seconds |
| `generated-face-2` | **10.8750** | Second observed rebound projected halfway to next existing source face |
| `generated-face-3` | **10.0625** | Third observed rebound projected into remaining opposite-side clearance |
| Later proposals | **rejected** | 10 attempted added faces would leave insufficient space for a block of diameter 0.50 |

This is an **explicit source-relationship-conditioned digital assembly rule**: only after a real observed impact may the simulator propose a receiver, at most 0.75 virtual seconds along the measured outgoing velocity and no farther than half the free distance to the nearest existing collision face in that direction. The face has the inherited span and x-normal from the simple translational-source model. New surfaces are installed at their observed causal contact times; no surface may collide with the block before creation. All surfaces are checked for block-diameter spacing. Input from the owner's original visual blueprint (desired guide/funnel/diverter/spiral) is **not** given to the physics generator.

The model is explicitly **not autonomous material self-assembly** and not full Earth physics. It uses a single frictionless rigid translating square without mass calibration, rotational physics, gravity, friction, deformation or curved/angled collision geometry. Source-workflow arguments such as genuine original NIH Phase 2 participation, clinical evidence, original historical registry posting instants and all-Earth physics equivalence remain unclaimed.

## Independent failure tests

- Altered contact time, time ordering, impulse, final x-coordinate, surface normal, surface construction decision, retroactive source activation, fake insufficient gap and source physical wall identity rejected.
- Source wall missed: **no new surface**.
- Zero restitution: one initial impact, no outgoing x velocity, **no new surface**.
- Change to 0.5 restitution: the browser and Python generate a different physical face placement, and the native independent causal witness checks the new history.
- Browser `Next look` and `Previous observation` expose the successive time-indexed source states; the screenshot and JSON receipt record the true observed path, including unsuccessful proposed surfaces.

## Reasoning boundary — why the simpler physics stopped

The result is a **structural invariant**, not merely a failed visualization: every admitted source collision has a purely horizontal normal `[-1,0]` or `[+1,0]`. The collision law only reverses/scales horizontal velocity. Each derived surface inherits another horizontal normal and becomes another **vertical straight face**. There is no orientation update, angular impulse, curved surface, rotational body, or other dimension that can create divergent wall orientations. As gaps decrease below the block diameter, the only permitted geometry construction is rejected, while the object continues contacting already-built parallel walls.

Consequently: repeated LOOK → LANGUAGE → A/B → NEXT LOOK **does recover multiple source-generated collision surfaces and a specific saturation regime**, but the original guide, funnel, diverter and spiral blueprint is **still not generated**. Preplaced existing WORLD obstacles are not counted as generated and no target labels were injected into the source world.

## Source code

- Native independently traceable generator: `systems/workspace/world_ab_iterated_surfaces.py`
- Falsification and independent causal trace oracle: `network/tests/test_world_ab_iterated_surfaces.py`
- Fully playable original WORLD extension: `docs/world_ab_iterated_surfaces.html`
- Actual browser/independent native verifier: `scripts/verify_world_ab_iterated_browser.py`
- GitHub Actions: `.github/workflows/world-ab-iterated-construction.yml`

**Next scientifically meaningful movement:** test **an additional real dynamic degree of freedom** under independently stated physical rules, such as oblique rigid-body contact normals and material rotation, without giving the generator desired geometry labels. Contrast with the present fixed-normal baseline; only if the resulting geometry actually differs topologically should that be treated as progress toward the source blueprint. Keep both failed and successful observations.
