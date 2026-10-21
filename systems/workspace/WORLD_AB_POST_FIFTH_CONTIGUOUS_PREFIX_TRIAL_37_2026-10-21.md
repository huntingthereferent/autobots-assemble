# WORLD Trial 37 — first contiguous modeled clearance prefix beyond hypothetical fifth response

WORLD35 independently qualified a **conditional, unselected** fifth-response mathematical impulse (5.7970314569) in only the original 10° source case. WORLD36 independently checked all 24 original square-corner/surface inequalities, providing nominal separation for the **first 0.008 virtual-time units** after that hypothetical fifth response. Neither source observed a material fifth impact, proved exact contact timing, or selected another real-world trajectory.

## New question and source constraints

What portion of the **next at most 0.05 virtual-time units**, through t=0.058 after the hypothetical fifth response, is still supported by the same original six planes and four rotating square vertices? The further declared horizon is capped at t=0.25; no new receiver or impact law is introduced.

Take original WORLD35 fifth candidate position/orientation and its exact original response velocities and spin. Evaluate source square geometry at both ends of each of **32 finite base intervals** from t=0.008 to t=0.058. For each of the original 24 plane/corner constraints, a fixed-axis velocity Lipschitz upper bound is `abs(v · n) + abs(omega) × square_half_diagonal`. Two endpoint gap neighborhoods support an entire interval only when each endpoint exceeds the positive guard and their summed surplus exceeds the bound times the interval duration plus the guard. This handles rotation between samples. A source face's supporting line is deliberately stricter than finite-segment intersection: failure means UNKNOWN, not a finite contact.

If the sufficient inequality fails, recursively subdivide *only that chronological slab* to a fixed depth of 8; stop at the first unsupported leaf. Record all and only verified contiguous subintervals and that first unknown, without projecting farther. Other seven source cases must have no hypothetical fifth response, no subsequent interval, and no manufactured sixth collision.

## Independent test and limitations

A separate witness reconstructs the original source vertex indices using a CCW corner ordering, original source geometry and all six original planes. It replays **every** accepted interval in chronological order and the first unsupported leaf, checks every recorded normal gap, speed bound, surplus and classification, and rejects extra or skipped intervals. A rotating synthetic counterexample deliberately has positive endpoint gaps but an intervening negative gap and must **not** be certified by the endpoint-only witness. Tampering with original ancestry, omitted measurements or asserted sixth material impacts is rejected.

Only nominal floating-point source mathematics is involved; no outward-rounded certificate, hardware validation, exact continuous first-contact proof, sixth impulse, post-unknown movement or receiver may be reported. Independent source verification and full inherited tests must pass before merge.

## Gates

Require original WORLD04/18/20/21/22/23/24/25/26/28/29/30/31/32/33/34/35/36 plus WORLD37 native unit regressions, retained source+independent witness JSON and SHA-256, workstation continuity, and full repository protocol on **the same PR head SHA**. If any fail, do not merge. Neutral A/B main, ARC, NIH, W13, World48, renderer, DAW and All Rights Reserved license are unchanged.
