# WORLD / A-B physical construction Trial 05 — source-connected first-contact routing

**Checkpoint:** 2026-10-19, original WORLD branch `world/w13-two-world-advance-contract-20261016`.

## Source and experimental boundary

Trial 05 is a controlled **cross-run assembly** using the exact two *separately generated receiver segments* from Trial 04B, with experimental source angles 0° and 20° and friction 0.4. The surfaces were not reoriented, moved to a desired shape, copied from the original A/B drawing, or simultaneously co-generated. These two line segments form **one finite intersection** within the original 24×6 grid. The original native W13 world and earlier physical source experiments remain unchanged.

The first four GitHub runs for this lane failed before browser verification because stored ten-decimal observation normals were passed to the original strict unit-normal impulse solver, which requires a Euclidean normal length within 1e-10. The native model was corrected to verify the source-normal deviation is below 5e-9 and reconstruct a unit vector **only at the impulse interface**. The recorded original face position, orientation, provenance, and geometry remain unchanged. This fixes a numerical storage/interface precision mismatch, not a wrong physical result or looser source admission.

## Independently witnessed outcome

[GitHub Actions run #39296335675](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39296335675) **SUCCESS**; [artifact #12209405850](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39296335675/artifacts/12209405850) (source HTML, native complete receipt, real browser-generated receipt and screenshot, independent browser witness), SHA-256 `db4996b3f5a753274ceac914c4879956f722e2f23759a7655a97534a522a60f6`.

- **17/17 focused native tests passed**, including independent intersection calculations, finite-disc contact checks, reference source stability, geometry and trajectory mutations, prior rotating-disc mechanics and Trial 03 iteration regressions.
- Real Chromium generated the source-connected geometry and seven probe outcomes; its entire receipt matched independently recomputed Python source geometry and the separate kinematic/impulse checker.
- Physical intersection: **(10.739308093, 1.322386209)** native (browser independently reconstructs approximately **(10.739308092, 1.322386211)**); rounding discrepancy is within verification tolerances.
- Source geometry has **two straight line segments**, **one finite intersection**, **one connected component**, and **zero curves**.
- Test probes originate at virtual x=12 with horizontal speed 2, on source-defined heights y=[0.9,1.05,1.2,1.6,1.8,2.0,2.25]. Under the single original near-vertical receiver, the first three miss. Under the connected geometry, they contact the **20°-source receiver** first.
- Probes at y=1.6, 1.8, 2.0 hit the **0°-source receiver** in both cases. The y=2.25 probe misses both.
- **Three of seven** probe heights change their first-contact result, without target guide/funnel/diverter/spiral labels in the generator. Both source receiver IDs are witnessed as distinct **first-contact** outcomes, with independently recomputed impulse and immediate outgoing motion.

## Code

- `systems/workspace/world_ab_connected_routing.py`: source-grounded finite segment intersection, first-admissible disc impact, baseline and assembled outcomes, strict normal reconstruction on impulse.
- `network/tests/test_world_ab_connected_routing.py`: separate geometric/rigid-body oracle, source/timing negative controls.
- `docs/world_ab_connected_routing.html`: **standalone** interactive companion linked to the original 144-cell playable WORLD, not a replacement world engine.
- `scripts/verify_world_ab_connected_browser.py`: actual Chromium and native/witness comparison, retained screenshot and JSON.
- `.github/workflows/world-ab-connected-routing.yml`: native, browser and retention.

## Claim boundary

**SUPPORTED:** two separately observed relation-derived straight surfaces can be assembled at their recorded coordinates and produce a connected geometry with distinct first-contact routes for fresh incoming probes. Native and browser agree, independently, within the explicitly bounded virtual model.

**NOT SUPPORTED:** simultaneous self-assembly, full finite-thickness multi-contact resolution at the junction, verified passage through a physical guide/funnel, material loads, curvature/spiral formation, all Earth physics, or reproduction of the full original physical A/B blueprint. This is a first-contact **path-selection** witness, not a demonstrated complete guide.

**Next falsifiable boundary:** run continuous trajectories near the crossing with two-sided collision and multi-contact manifold handling, test for penetration and double-contact ambiguity, and compare multi-step exit distributions with the current first-contact-only control. Do not label this junction as the original guide/funnel without that independent functional behavior witness.
