# WORLD Trial 15 — two object geometries, same movement relation

**October 20, 2026**. Continues the original WORLD Trial 14 branch. This experiment does not introduce another engine, renderer, world type, new corpus of physical laws, or a motor/NIH-specific modeling system.

## Mathematical question

Does the same finite construction-from-movement step persist when the translating object's **support geometry** changes?

Compare two bodies in the **same** original 24 × 6 virtual WORLD:

- A disc of radius 0.25, allowed only frictionless translation in this control.
- An axis-aligned square with half-side 0.25, explicitly **held at fixed orientation by a constraint**. That constraint is an essential idealization; these results are not the free rotation/torque of a real square.

Each moves from the *same* original position and velocity toward the same source segment at a selected finite orientation. Each obeys exactly the same ideal normal reflection:

`v_out = v_in - 2 (v_in · n) n`.

Only the support distance from its center to the supporting contact plane differs:

- Disc: `h(n) = r`.
- Fixed square: `h(n) = r (|n_x| + |n_y|)`.

The source first-contact time follows from `(p0 + t v - a)·n = h(n)`. If the support point lies within the finite segment interior, this gives a bounded modeled contact. The actual computed outgoing velocity determines the *next* face normal `n2 = -v_out/|v_out|`; the next face is positioned at a source-derived projected future contact center after the inherited Trial04B/14 0.25 virtual time. Test that the same body can reach its derived face, reflect, and remain in WORLD bounds.

This is *still just the mathematics* of a particular declared relation, not a claim that the shape has been manufactured. Nothing classifies an NIH document as a square or requires 48 universal laws.

## Why this is a real test

The face/source is not pre-arranged for each object. Different contact supports shift the first contact and consequently the derived surface's placement. Same source angle and same initial motion therefore can produce a **different constructed world state** for the disc and fixed square. The angle is not a prescribed shape name; it is an input to one geometric relation.

The square's representative support point may be outside the original finite face interior at a wider angle even when the disc's point remains admitted. In that case we return `NO_ADMITTED_INTERIOR_CONTACT` and **do not** fabricate a completed path. Crucially, it is **not a claim of no physical collision**: an endpoint may have been struck, and that model is deliberately unresolved.

Input grid: angles 0°, 7.5°, 12.25°, 20° × both constrained bodies = eight modeled two-contact trajectories, if independently verified. Control: disc results must match the unchanged Trial 14 frictionless source exactly. One 30° control probes the finite-face scope boundary.

## Evidence and restrictions

Source: `systems/workspace/world_ab_body_support.py`. Independent numerical witness and negative tests: `network/tests/test_world_ab_body_support.py`. Dedicated Actions workflow `.github/workflows/world-ab-body-support.yml` executes the original 04B, new 14, and 15 tests and retains hash-stamped native source and oracle outputs.

The witness separately recomputes both source face endpoints, body support, contact times and velocities, derived receiver orientation/position, every motion sample, boundary separation and activation causality. Mutated angle/receiver/source/contacts and fabricated physical-measurement flags must be refused.

The **full finite endpoint-contact problem, freely rotating square, simultaneous multiple contacts, all 3D motions, real Earth material behavior, and actual NIH blueprint** are not solved by this. If an interaction requires one of those relations, record its absence rather than silently importing a general physics engine or a hypothetical result.

No changes are made to the original WORLD contact sources, the W13/ARC/NIH projects, or the pending A/B-owned renderer lane. If the PR's CI fails, treat results as unverified until repaired.
