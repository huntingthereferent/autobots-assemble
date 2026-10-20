# WORLD Trial 16 — free rotation tests the next movement before construction

**October 20, 2026 · original WORLD branch continuation.** Parent: Trial 15 fixed-orientation square vs disc. Trial 16 uses the *already established original* Trial 04 rotating-square first-impact mathematics. No engine, scene tree, new dimensions, motor-specific type, or universal physical law is introduced.

## What changed

Trial 15 constrained a square against rotating, so one reflected translation could lead it toward a newly derived surface. For a truly rotating square, that continuation is not automatically valid. The earlier original `world_ab_oblique_impact.py` independently calculated the square's **first frictionless impact**, including off-center impulse and the resulting angular velocity, but its post-impact position/orientation was explicitly *unconstrained ballistic projection* and its receiver was a proposal only.

This experiment keeps that source untouched. The four original square corners are rotated around the outgoing center with the existing angular speed. At every 0.001 *virtual* time units through 0.06, the test independently checks each projected vertex against the **original finite** face interior. If a vertex crosses onto the prohibited side at a point along the finite segment, it records the **first sampled overlap**, rejects unsupported continuation, and does not activate a derived receiver or invent a new impulse.

The source face's tangent interval matters; extending its line to infinity would fabricate collisions. This finite-interior vertex check is deliberately conservative and incomplete. It is not a continuous rotating polygon vs finite segment solver; between-frame collisions and edges crossing without a vertex sample remain undetermined. It cannot prove absence of contact when no sampled overlap is found.

Angle controls are `0°, 2.5°, 5°, 7.5°, 10°, 12.25°, 15°, 20°`. All original first-contact impulses and velocity/spin values remain from Trial 04. Any resulting overlap is a **mathematical counterexample to unconstrained linear continuation**, not independently measured material contact. The first overlap remains unresolved: do not replace it with a guessed normal, collision duration, deformation or outgoing trajectory.

## Witness and test boundaries

- Source: `systems/workspace/world_ab_rotating_square_clearance.py`.
- Independent oracle: `network/tests/test_world_ab_rotating_square_clearance.py` reconstructs the rotation matrix, source normal, original endpoints, every corner position, finite segment coordinate and signed separation without calling the new geometry routines. It runs the original first-contact `verify_impact`.
- Negative controls deliberately corrupt spin, first impulse, position, orientation, clearance, corner identity, status, source angle and any claimed physical measurement/receiver construction.
- Dedicated CI: `.github/workflows/world-ab-rotating-square-clearance.yml`, with Trial 04, 15 and Trial 16 native regressions, retained full sampled records and SHA-256 receipts.

**No source evidence promotes** an unverified second impact, a real-world free-rotating square observation, Earth-scale material equivalence, or a completed motor/NIH blueprint. The distinct Trial 06–13 simultaneous-contact ambiguities remain unresolved.

The next mathematically justified move after a detected overlap would be a **separate, independently validated first recontact time/contact-feature calculation** with finite edges and angular velocity. Not a new renderer or an assumed successful future collision.
