# WORLD25 — retain full finite shape intersections, not fourth contacts

The original WORLD21 source provides a conditional third impulse and two
source-derived finite faces in a bounded 24×6 world. Trial22 checked first
square-vertex/supporting-line crossings. Trial23 retained all inward
crossings and their finite-face versus line-extension classifications.
Trial24 separately checked source face **endpoints** against rotating
square **edge interiors**. These are different, source-owned geometric
relations, and none independently proves complete finite contact.

Original WORLD25, at pinned source commit
`c4190eff7d0147b53620322c1900fdb7dfc6b9c3`, checks the **entire finite
source segment against the entire rotating square** within the original
conditional third-impulse motion. For each of two pre-existing finite faces,
it checks 2,049 time-grid positions within [0.008, 0.25] after the hypothetical
third impact. The original source clips each finite segment in the moving
square's local frame; an independent source verifier implements the
separating-axis theorem on the world-coordinate square and line segment.

A detected finite intersection is **model evidence**, not an exact first
contact, continuous collision detection, measured hardware behavior or
selection of a fourth impulse. The source retains all sampled overlap
windows, first-grid indices, bounded numerical transition brackets and
source23 same-face vertex comparison. If no sampled overlap is found,
the observation is limited to that grid; omitted intervals are not proved
clear. A source case lacking the conditional third impulse must retain zero
post-third geometry.

The neutral A/B adapter separately executes and consumes source23, source24
and source25 reports from the **same pinned original commit**. It checks
their original third-impulse and derived-receiver ancestry, preserve names
and both existing finite endpoints, counts source windows, and keeps all
source25 candidate brackets in original source observations. This creates
eight independently bounded A/B records. It contrasts the hypothesis of
no sampled finite intersection with the actually reported source result
and retains the original Trial23/24 feature alternatives for independent
inspection.

No new receiver is created by the carrier. No geometrical crossing selects
a contact force. Neither the carrier nor receipt hashes independently
establish the source mathematical SAT/clip equivalence—that remains the
responsibility of the pinned original numerical oracle, run in dedicated CI.

The original WORLD model branches, ARC, NIH, W13, World48, renderer,
general A/B bounded construction rules and All Rights Reserved ownership
terms are unchanged. The next source investigation may refine a detected
first finite intersection, but must not substitute a time grid or a
supporting-line candidate for a certified actual contact.
