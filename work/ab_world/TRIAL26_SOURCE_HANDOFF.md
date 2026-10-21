# WORLD26 — preserve unknown between-frame intervals, not invented collisions

The original WORLD25 model checks two existing finite source segments against
the moving square on 2,049 finite grid poses per face, after a conditional
unselected third impulse. A negative grid result alone cannot rule out a
finite collision **between** those positions.

Original WORLD26, pinned to commit
`d9a735b1a5473c0f2646778996c89e70af0d28fd`, evaluates an
independently reconstructable sufficient nominal separation bound over
each of the 2,048 intervals per original finite face. It compares
separating-axis gaps at both sample endpoints against a conservative speed
envelope for every moving square vertex:

`|center velocity| + |spin| * sqrt(2) * half_extent`.

The native rule grants interval coverage only if positive sample margins
and their combined velocity-corrected surplus exceed the source guard.
When that bound does not succeed, the interval remains **unknown**, not
a diagnosed collision. A successful bound certifies only the stated
nominal mathematical assumptions; the source does not provide
outward-rounded floating interval proof, hardware measurements or a
general future collision solver. Even later virtual samples are conditional
on no earlier unmodeled contact.

The A/B handoff separately executes pinned original WORLD25 and WORLD26,
rechecks their source ancestry, original third-impulse refusal controls,
two finite face geometries, 2,049 endpoint margins and 2,048 interval
counts, fixed guard, per-face speed envelopes and original interval
classification. The original independent WORLD26 verifier recomputes
world-coordinate polygon SAT margins, corner-speed bounds, every source
uncovered-interval classification and intentionally challenges a
between-grid false-negative example.

Eight bounded A/B case records distinguish source-admitted third-impulse
controls, complete nominal two-face coverage, and remaining unknowns.
Every original uncovered source interval is retained in **separately
bounded batches of at most 128**, with each source face's identity,
original report digest and ordered receipt head tied in a manifest.
No arbitrary increase of the neutral A/B plan limit is needed. An A/B
comparison records when a no-unknown-interval hypothesis is contradicted;
it does not interpret the contradiction as a fourth impact.

No actual fourth impulse is selected, no new face constructed and no
physical material contact inferred. The source model, general A/B WORLD
construction, ARC, NIH, W13, World48, renderer and original licensing
remain unchanged.
