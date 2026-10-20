# WORLD Trial 14 — one mathematical source face, movable without predefined shape categories

**Date:** October 20, 2026. Parent: original WORLD Trial 13 branch, `experiment/world-trial13-coupled-contact-modes-20261019`. This is a distinct experiment, not a merge of an unfinished contact solver or a replacement of W13, NIH, ARC or the previous WORLD models.

## The question

Can we preserve the *same* construction-through-movement relationship of Trial 04B while changing the source face continuously, rather than allowing only the previously predeclared 0° or 20° orientations?

One rigid, virtual radius-0.25 disc starts at the original WORLD position (3, 1.35), moving at (3, 0.12). A finite input face has a bounded operator-provided anchor and angle. The original single-contact friction law computes the outgoing velocity and spin. Only after that contact is modeled do we construct the second face: its unit normal opposes the actual outgoing translation, and its center contact is projected for the inherited 0.25 virtual time units along that movement. A second modeled impact must then be reached. An angled source produces an angled receiver *because of the resulting motion*, not because a target shape was supplied.

The input source anchor and angle are *experimental controls*, not inferred physical measurements. The second face is a **math-derived virtual object**, not self-assembled matter. We do not assume that arbitrary parameters are supported: finite source angle is restricted to [-40°, +40°], anchor is bounded within x=[7,16], y=[.75,5.25], friction within [0,.4], source and derived finite endpoints must lie in the original 24×6 WORLD, source impact must reach the original finite **segment interior**, and all recorded movements must preserve nonpenetration and world bounds. A miss constructs nothing.

The four original 04B cases (0°/20° × friction 0/.4) are replayed, and new 7.5° and 12.25° source angles are tried under the same virtual laws. Each case records both contact positions and times, velocities and spin, source and derived segment endpoints, activation after source contact, all bounded observation frames, and whether construction was possible. Two source angles can produce different receiver normals without introducing any additional object category or new law list.

## Evidence / scope

Implementation: `systems/workspace/world_ab_relation_morph.py`. Independent analytic witness: `network/tests/test_world_ab_relation_morph.py`. The independent witness recomputes face angles and finite endpoints, both contact impulses, energy and spin assumptions, actual virtual contact times, and every sampled motion position, without calling the generator's impact math. It also compares the shared 04B controls directly against the unchanged original source.

Negative cases: finite-segment miss, nonfinite/unbounded inputs, forged receiver angle or placement, forged impulse/contact/frame, false material measurement and receiver activation at the wrong time. No created face or completed motion is inferred for a miss. Previous Trials 03, 04B and 06–13 are not edited.

A source-pinned CI run must pass before making claims of completed verification. Workflow `.github/workflows/world-ab-relation-morph.yml` runs original Trial 03/04B regressions and this independent numerical trial, and retains a SHA-256-stamped JSON record of every attempted source and constructed movement.

## What this does **not** establish

No new 3-D scene tree, a motor-only world, a list of mandatory physical laws, automatic geometry creation in actual matter, complete surface contact/multicontact solver, NIH physical blueprint equivalence, or a proven Earth material property. The representation is one **bounded mathematics of objects whose relations change through contact**. The next constraint should come from a counterexample or requested construction, not an assumed universe of future objects.

The object renderer should consume this exact source record if selected; it must never become the source of motion or assign extra non-witnessed relationships.
