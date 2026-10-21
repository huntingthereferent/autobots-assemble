# WORLD Trial 18 — one conditional second impulse, same mathematical world

**October 20, 2026**. Parent: existing WORLD Trial 17, merged onto its original Trial 16 branch. This adds no new world, physics engine, artificial object taxonomy, renderer or motor/NIH-specific constraints.

## One mathematical movement

Trial 17 narrowed six original rotating-square controls to the first later vertex crossing of the *same finite source face* after the independently tested original Trial 04 impulse. Trial 18 asks a bounded question: **if the same frictionless elastic normal-contact law were applied to that renewed corner contact, what immediate outgoing velocity and angular velocity would it produce, and would the rotating square remain separated over a short observed window?**

The object's mass and inertia are unchanged from Trial 04 (unit mass, side length 0.5 virtual WORLD units, inertia 1/24). A corner at relative position `r` has incoming contact-point velocity `v_c = v + ω J r`, with `J(x,y)=(-y,x)`. For the existing face normal `n`, the proposed frictionless restitution-one normal impulse is:

`j = -2 (v_c · n) / (1/m + (r×n)²/I)`.

The same impulse updates translational velocity `v'=v+j n/m` and angular velocity `ω'=ω+j(r×n)/I`. Positive incoming normal impulse, reversed contact normal velocity and translational-plus-rotational kinetic-energy conservation are independently checked. No tangent impulse, material damping, surface compliance or real restitution measurement is assumed.

Each original source and Trial 17 candidate is preserved. For the six new-contact candidates, the code independently checks original face coordinates, corner identity and the contact normal before proposing an impulse. It then inspects all four rotated square vertices at finite-face tangent coordinates in 0.0005-unit increments through the next 0.016 virtual-time units. A detected overlap is an explicit **unresolved** case. A sample series without overlap is **not** evidence for continuous-time clearance or sustained contact consistency: between-sample passage, edge crossings and future collision response are not solved.

The two original 0° and 20° cases lack a renewed source contact within Trial 17's window and therefore have **no proposed second impulse**.

## Verification and negative cases

- Generator: `systems/workspace/world_ab_local_recontact_impulse.py`.
- Independent witness: `network/tests/test_world_ab_local_recontact_impulse.py`, reconstructing the original Trial04 impact and Trial17 first return using independent prior oracles, then recomputing lever arm, proposed normal impulse, post-spin and every local sample without calling Trial18's helper routines.
- Negative tests mutate contact time, source frame, impulse, energy, corner, sampled clearance and hardware claims. Any unsupported source must stop rather than constructing a receiver.
- Dedicated workflow `.github/workflows/world-ab-local-recontact-impulse.yml` runs earlier original first-impact/rotating-clearance/first-return regressions, plus Trial18 independent numerical tests, and retains a SHA-256-stamped JSON replay. CI results are evidence only after completing successfully.

**Evidence boundary:** this is a *conditional mathematical impulse hypothesis*, not a measured second material impact or a unique contact law. The candidate's short observed path is not a verified physical continuation. No new face gets constructed and no further impact is selected. The earlier WORLD, NIH and A/B-owned renderer sources are unchanged.

Next question, only if the math supports it: whether the full continuous rotating-polygon boundary, including finite segment endpoints and possible simultaneous vertices, admits that post-impact motion. No further construction is supported merely by these samples.
