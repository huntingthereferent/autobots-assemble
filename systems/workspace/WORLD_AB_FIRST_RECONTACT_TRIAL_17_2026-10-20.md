# WORLD Trial 17 — first *renewed* finite-source contact of the rotating square

**2026-10-20 · existing WORLD experiment lane**. Parent `experiment/world-trial16-rotating-square-clearance-20261020`. All original W13, WORLD03/04/15/16, NIH and renderer sources remain unchanged.

## Why this mathematical movement

Trial 16 retained the original experimentally controlled Trial04 square's *first* off-centre impulse, then showed that a freely rotating square could overlap the finite source under an unsupported straight-line/constant-spin continuation. Sampling revealed six overlaps but did **not** determine when renewed contact began. No response or next receiver was supported.

For each of the four original square corners, its signed normal distance from the original source line during candidate ballistic motion is a linear term plus `cos(omega·t)` and `sin(omega·t)`. Rather than guessing an event at the first sampled penetration, Trial17 enumerates stationary points of **each corner-distance function** within the admitted 0.06-virtual-time window. Each resulting monotonic interval is checked for a positive-to-negative root, which is bracketed by numerical bisection. The chronologically first candidate must have a vertex on the *actual finite segment interior*, not merely on an infinite line.

Input: the original, already independently checked, frictionless square first-impact record. No new source face, square dynamics engine, restitution assumption, arbitrary contact category or physical hardware result is added.

## Expected bounded observations

Controls: original source angles 0, 2.5, 5, 7.5, 10, 12.25, 15, 20 degrees. The six intermediate angles have predicted renewed point-face crossing times near 0.005296, 0.010904, 0.017048, 0.024108, 0.031851, and 0.045321 **after** the original first contact. The 0° and 20° controls do not show this same renewed line crossing inside 0.06 in the declared model. The numbers are candidates to independently test, not data from real-world instruments.

The independent oracle recomputes original-square impulse separately, then rotates the four vertices itself at 0.000025 virtual-time spacing and bisects the **first positive-to-negative** distance crossing. This verifier does not call the generator's stationary-point algebra. It checks corner identity, absolute/relative time, vertex coordinates, signed normal gap, tangent position along the finite face, source identity and the absence of invented later contact response or hardware testimony.

No return means **no new supporting-line crossing within the tested window**, not proof of physical clearance against finite endpoints or an unlimited-time absence of collision. A return is a geometrically located **candidate contact time** under the original ballistic continuation, not a completed sustained-contact or second-impulse solution. Root bracketing uses ordinary floating-point arithmetic: no formally certified interval/equality or exact physical time is claimed.

## Boundary gates

- Do not report the initial t=0 contact as a *new* contact. Immediate penetration or grazing must be marked unresolved.
- Reject a return outside the actual finite source face interior.
- Preserve the original source first impulse, its orientation, speed and angular velocity.
- Reconstruct source-root times with independent numeric geometry; reject tampered time, corner, face location, original impulse, source angle or invented receiver.
- At first renewed contact, stop: **no second impulse, post-contact trajectory or constructed receiver** is provided.

Source: `systems/workspace/world_ab_square_first_recontact.py`. Test: `network/tests/test_world_ab_square_first_recontact.py`. Workflow: `.github/workflows/world-ab-first-recontact.yml` runs earlier Trial04/16 regressions, the independent numeric witness, and retains SHA-256-stamped complete source model results.

This is not a general physical world, a motor, NIH blueprint, an exact-contact interval solver, a verified material model, or a renderer. It is the next bounded movement in the *same* WORLD, and leaves the unresolved relationship observable.
