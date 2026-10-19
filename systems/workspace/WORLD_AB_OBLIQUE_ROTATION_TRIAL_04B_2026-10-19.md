# WORLD / A-B Physical Trial 04B — oblique normals, angular response and derived receiver

**Date:** October 19, 2026  
**Existing WORLD branch:** `world/w13-two-world-advance-contract-20261016`  
**Status:** independently reproduced native/browser dynamics across four controlled cases; **complete original visual blueprint NOT GENERATED**.

## Scope and provenance

This is a continuation of the source-owned Trial 01 through Trial 03 physical construction work, within the existing **24 × 6 virtual WORLD**. Trial 03 generated three parallel vertical faces then hit a clearance limit; see `WORLD_AB_ITERATED_PHYSICAL_CONSTRUCTION_TRIAL_03_2026-10-19.md`. Trial 04B tests whether **angled normals** and **contact-induced angular velocity** change the relation-derived receiver topology under declared friction mechanics.

A separate, independently ongoing Trial 04 on this branch (`world_ab_oblique_impact.py`, verified [run #39266763862](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39266763862)) uses a **rigid square**, computing the first off-center impact and angular impulse but **not** asserting a verified follow-on receiver impact. **Trial 04B deliberately uses a rigid disc** with Coulomb friction and a separate two-impact replay. Do not treat the square and disc branches as identical controlled bodies or combine their evidentiary claims.

The native source wall remains (12,1)–(12,2) in the original WORLD. A new **isolated 0° / 20° experimental face** is anchored at its midpoint (12,1.5), explicitly not a replacement for the original physical wall. The original W13 rooms, native journals, Trial 03 script and original blueprint were not modified.

## Physical dynamics

- Disc radius = 0.25 virtual cells, normalized mass = 1, `I=0.5*m*r²=0.03125`.
- Incoming centre position (3,1.35), velocity (3,0.12); exact continuous source contact and receiver contact with a circular disc.
- Source-normal angle independently set at 0° or 20°. Surface friction independently set at 0 or 0.4. Normal restitution = 1; tangential impulse is bounded by Coulomb friction.
- Tangential surface velocity includes `v · tangent - spin * radius`. Contact impulse updates both translation and angular velocity. Independent analytical equations check both event times, x/y, velocity, spin, rigid-body energy and causality at all 34 frames per case.
- Declared digital **construction policy**: when the first source impact has been independently observed, derive the receiver's normal from the *opposite direction of the outgoing centre velocity*; place it 0.25 virtual seconds along that measured velocity with radius compensation, and independently verify a second contact. No original target shape names enter the dynamics generator.
- This is a **controlled contact-and-construction experiment**, not spontaneous matter self-assembly, real-world mass calibration, all-Earth physics, frictional deformation, curved geometry or an original physical blueprint reproduction.

## Actually executed native and browser evidence

[Successful GitHub Actions Trial 04B run #39267233029](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39267233029) · [retained actual playable HTML, screenshot, native branch records and independent Chromium receipts #12193267963](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39267233029/artifacts/12193267963), ZIP SHA-256 `091ff4369b846fe7ed1cbd3b5e20543b67111cb2279fb6dc75082ee9a4848fc2`.

**12/12 focused controls passed:** six separate oblique/rotation analytical, mutation and original target-failure checks, plus six prior original Trial 03 regression controls. Real Chromium generated the same four entire branch receipts; native Python and the separate analytical oracle agreed for all **34 frame samples per branch**, all impact impulses and the two actual contact events per branch.

| Case | Experimental source angle | Friction | Derived receiver normal orientation | Disc rotation from contact? | Source contact time | Receiver contact time |
|---|---:|---:|---:|---|---:|---:|
| A | 0° | 0 | −2.290610° | No | 2.916667 | 3.166667 |
| B | 0° | 0.4 | −1.527525° | Yes | 2.916667 | 3.166667 |
| C | 20° | 0 | 37.709390° | No | 2.887479 | 3.137479 |
| D | 20° | 0.4 | 32.017777° | Yes | 2.887479 | 3.137479 |

The 0° no-friction disc baseline already produces a slight angle because the original incoming motion includes +0.12 tangential velocity. Adding the 20° source angle gives materially different receiver orientation; adding friction generates nonzero angular motion and changes the resulting receiver angle. The *receiver orientation is the opposite outgoing translational vector* by construction: it is **not an unprogrammed emergence of arbitrary curved material**.

The live browser preserved the original 144-cell physical WORLD, existing trial03 callable controls and original script spans. Browser observation controls executed each case forward and backward to its final frame and then reset. No full Earth physical laws, actual original clinical history, or NIH competition result were asserted.

## What actually changed versus Trial 03

**SUPPORTED:** a second physical degree of freedom changes the outgoing physical state (normal-axis deflection, tangential impulse, rotation) and the independently derived orientation of an additional functional collision face. Existing Trial 03's strictly parallel-wall orientation **is not a mathematical necessity** in an angled-contact model. There is a real independently verified second contact with the new angled receiver.

**NOT SUPPORTED:** generating the original guide, funnel, diverter or spiral from unrestricted free dynamics. The current receiver is one straight segment with a normal selected by an explicit observation-based rule. Although more orientations are possible, a functional funnel, diverter, guide, vortex/spiral shape, robust path selection, material self-assembly, realistic Earth gravity, full variable material friction and damage mechanics are not reproduced. No clinical inference or NIH proposal submission was performed.

## Files and executable checkpoints

- `systems/workspace/world_ab_oblique_rotation.py` — native four-way rigid-disc source/contact/receiver generator; no original target diagram references.
- `network/tests/test_world_ab_oblique_rotation.py` — **independently rederived event-time and impulse oracle**, full-frame readback and mutants, structural non-equivalence negative case.
- `docs/world_ab_oblique_disc_factorial.html` — standalone playable actual WORLD extension with all four native-derived cases, disc orientation marker, frame navigation and exported source receipt.
- `scripts/verify_world_ab_oblique_disc_browser.py` — compares browser against native model and analytical oracle, retains screenshot/receipt, checks old W13 and Trial 03 scripts unchanged.
- `.github/workflows/world-ab-oblique-disc-contrast.yml` — independent replay and artifact gate.

**Next coherent boundary:** before expecting genuinely curved guide, funnel or spiral construction, test bounded connected surfaces with *different normals*, compare trajectories under declared collision/material rules and reject any predetermined target-shape sequence. A true functional topology result requires independent shape and route verification, not renaming a single constructed line.
