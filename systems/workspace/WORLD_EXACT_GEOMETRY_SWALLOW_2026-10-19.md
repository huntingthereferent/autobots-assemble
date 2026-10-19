# Computational geometry source swallow — exact classification, no collision rewrite

**External source inspected:** [kika, commit `36920f741cbe6a53cd0f80727b03362ebe0a7a83`](https://github.com/kent-tokyo/kika/tree/36920f741cbe6a53cd0f80727b03362ebe0a7a83)
(Apache-2.0), specifically `src/intersections/segment2.rs`,
`src/predicates/orient2d.rs`, `tests/adversarial/segment_intersection.rs`,
and `docs/adr/ADR-004-exact-construction-strategy.md`.

## Actual new relationship

The upstream separates a **predicate** — whether two finite segments
intersect, and *how* — from a separate **construction** — the actual
intersection coordinates. Its robust orientation predicate first tries a
floating-point filter, then escalates to exact expansion arithmetic if the
filter is inconclusive. These are observable source mechanisms, not a reason
to install its Rust runtime or replace A/B physics.

The previously merged A/B Box2D topology audit classified finite crossings
with floating-point determinants and a tolerance. It conservatively returned
`parallel-or-unresolved` for near-parallel cases. That is a defensible
approximate result, but not a definitive classification of the **recorded**
binary coordinates. We located one concrete input whose naïve determinant
rounds to zero while its exact binary determinant is **negative**.

## Smallest addition

`world_ab_exact_topology_audit.py` uses Python's standard-library
`fractions.Fraction` to compute **exact signs of the supplied finite binary
inputs**. The predicates classify the WORLD source's independently measured
finite crossing, shared endpoint, endpoint against a segment interior,
collinear touch/overlap, and disjoint cases.

The result is a **read-only cross-check against the existing approximate
audit**. If the classifications disagree, the API reports the disagreement.
It does not mutate the input geometry, silently overwrite a witness,
construct an intersection position, suppress a physical contact, or change
the Trial 06/07/08 solver and its collision mechanics.

Input coordinates are confined to a finite `[-10000, 10000]` range
(rejecting zero-length segments and nonfinite values). This bounds the
research scale, but *exact binary arithmetic does not recover precision
already lost when the original source was rounded*. It neither guarantees
a physical-world result nor constitutes external proof of the original
unrounded geometry.

## Reproduce

```bash
python -m unittest -v network.tests.test_world_ab_exact_topology_audit network.tests.test_world_ab_segment_topology
```

Test the exact 04B-derived WORLD source, symmetry, segment reversal,
collinear/end/interior controls, adversarial floating-point cancellation,
nonfinite cases, and near-but-disjoint geometry.

All code in this change is original A/B implementation and uses the Python
standard library; no upstream Rust code, expansion arithmetic, external
dependency, license or claimed numerical benchmark is imported.

This continuation is deliberately based on the **WORLD Trial 08 experimental
branch**, not on `main`. A separate physics experiment and independent
Chromium replay would be needed before any collision-model change.
