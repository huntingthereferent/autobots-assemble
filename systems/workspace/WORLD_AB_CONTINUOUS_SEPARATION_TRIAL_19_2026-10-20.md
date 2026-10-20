# WORLD Trial 19 — whole-interval clearance, no new world

**October 20, 2026 · A/B original WORLD continuing from Trial 18.**

## What the source movement supports

Trial 18 tested the **same original rigid-square contact law** conditionally at Trial 17's first renewed finite-face contact. Six virtual cases generated candidate second impulses that passed conservation and no-penetration checks at sampled frames. That did not establish movement **between** those frames.

Trial 19 uses only the mathematics of the SAME two-dimensional translating and rotating rigid square in the SAME 24×6 virtual WORLD. There is no new physics engine, scene tree, predefined object catalog, NIH/motor-specific system, or added category of laws.

At the Trial 18 candidate instant, let `r_i` be any one of the square's four half-side-0.25 vertices relative to its center. If the candidate's outgoing translational velocity and spin remain constant in the bounded observation window, its signed distance to the **original** source supporting line is:

`g_i(t) = n·(c0 - a + v t + Rot(ωt) r_i)`

The exact real-arithmetic curvature bound for this declared constant-motion model is:

`|g_i''(t)| ≤ ω² sqrt(2) * 0.25 = K`.

By Taylor's inequality,

`g_i(t) ≥ g_i(0) + g_i'(0) t - (K/2)t²`.

For the initially touching corner, `g_i(0)=0` (within source rounding tolerance), and a strictly positive conservative lower bound on its outgoing derivative means it **moves away from the line throughout the entire open interval**. For the other three corners, the quadratic lower polynomial is concave, so checking its two interval endpoints is sufficient to prove a positive gap throughout the interval.

If every one of the square's vertices stays on the same strictly positive side of the source line, the convex square cannot intersect that **infinite** supporting line; therefore it also cannot intersect the **finite** original face or endpoints. This deliberately stronger separating condition avoids constructing any additional collision response.

The window is *exactly* 0.016 original WORLD virtual time units after the Trial18 candidate impulse. It cannot be silently extended. The eight original source angle controls remain 0°, 2.5°, 5°, 7.5°, 10°, 12.25°, 15°, 20°. The two original no-recontact controls retain **no second impulse or clearance claim**. Six candidates must pass the conservative bound before reporting conditional mathematical separation.

## Independent falsification

`systems/workspace/world_ab_continuous_separation.py` implements a short, explicit four-corner Taylor bound.

`network/tests/test_world_ab_continuous_separation.py` independently verifies original Trial18 source/impulses and **does not call this bound computation** to decide continuous clearance. Instead, for each vertex, it separately derives `g_i(t)=c+v_n t+A cos(ωt)+B sin(ωt)`, locates the analytically characterized stationary times of this trigonometric distance function in the bounded interval, and checks every extremum. It also independently checks all claimed numerical Taylor margins. Deliberately corrupted corners, margins, spin, source impulses, conditional flags, time windows and fabricated physical results must fail.

Dedicated workflow `.github/workflows/world-ab-continuous-separation.yml` replays earlier Trial04/17/18 tests and the new independent witness, preserving model, numerical bounds, verification receipts and SHA-256 content digest. Report completed verification only after inspecting actual CI results.

## Strict limits

This is **conditional, continuous-time geometric separation under nominal real-number constant translation and spin after one selected model impulse**. The contact law is still a hypothesis, not selected by physical measurements. The computation uses ordinary binary floating-point values, not formally outward-rounded interval arithmetic; consequently this is not a machine-checked numerical theorem for arbitrary real input or an empirical Earth-material claim. Input rounding is disclosed, particularly the initially touching vertex's near-zero source gap.

No arbitrary joint contacts, forces, deformable materials, further motion beyond this window, fabricated next receiver, motor prototype or NIH blueprint result is established. The world continues only as far as these existing relationships support.
