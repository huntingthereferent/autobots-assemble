# Trial 16 — sampled free-square rotation as a retained counterexample

## Source and scope

Original WORLD Trial 16 is pinned at `6d22286b1fd129ae4011d1abb55dd4c320d58a5a` and replayed from its own untouched source checkout. Its independent witness recomputes the original Trial 04 rigid-square first impact, rotating polygon vertices, finite-face tangent coordinates, signed clearances and overlap flags.

This is *not* Trial 15's fixed-orientation square calculation. The original first impact produces an angular velocity; the following 0.06 virtual time units are sampled every 0.001 time units (61 samples per angle). No sample is a material sensor reading and no source beyond those sampled times is certified.

Source controls are 0°, 2.5°, 5°, 7.5°, 10°, 12.25°, 15° and 20°. Six source cases contain a sampled overlap with the original finite source face. The other two have no detected sample overlap, **not** established continuous clearance. In no case is the proposed receiver actually constructed, a later impulse calculated, or the original unresolved contact forced to a particular answer.

## Bounded A/B handoff

The A/B ledger records each original source case separately:

- Introduce the finite original source and the square after its source-owned *first* modeled impact, as a virtual object.
- Retain the original impact and any source-proposed receiver only as observations, never as an introduced object.
- Preserve time-ordered, explicitly unverified ballistic projection revisions only **before the first source-detected overlap**. Do not revise the square into or through the overlapping and later candidate frames.
- Preserve **all 61 source samples** for each case in an attributed source observation, including the quarantined projected tail when overlap is detected.
- Contrast the hypothetical no-overlap continuation with the source-reported overlap. The six counterexamples become `DIFFERENT`; two sampled no-overlap cases become `MATCH` *only within that sampled comparison*. Neither verdict upgrades to continuous physical clearance.
- Carry the final source status, precise first detected sample time, receiver-not-built, second-contact-not-solved and hardware-not-measured boundaries.

The original numerical witness is separate from the neutral A/B verifier. The latter reconstructs object revisions, observations, comparisons and hash ancestry without independently recalculating polygon physics. Tests reject fabricated physical evidence, altered source identity, reordered or missing samples, invalid overlap or source count, altered candidate status, continued states past the overlap boundary, and tampered ledger receipts.

The CI workflow pins the unchanged original source, runs its original native tests and independent oracle, then executes A/B fixture-negative tests, creates eight finite carrier receipts, independently verifies each receipt, and saves source artifacts and SHA-256 manifests. Both focused CI and the repository-wide protocol suite must pass before merge.

## What remains unknown

This does not solve continuous rotating-polygon contact, edge-only or between-sample intersections, post-overlap impulses, free-body friction, material deformation, or physical measurements. An early source overlap is a counterexample to the *unconstrained projected path*, not evidence for a specific new force or contact solver. Original WORLD source, neutral A/B limits, W13, ARC, NIH, World48, renderer and current A/B license are unchanged.

## Next evidence boundary

The next independent source study is Trial 17: bracket the first renewed contact with finite edges and angular velocity. Carry the interval and source-supported contact-feature uncertainty before admitting any new post-contact movement.
