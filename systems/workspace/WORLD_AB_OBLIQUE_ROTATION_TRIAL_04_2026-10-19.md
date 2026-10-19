# WORLD / A-B physical trial 04 — angled normal and rigid-square rotation

**October 19, 2026** · Original WORLD branch `world/w13-two-world-advance-contract-20261016`.

## Executed native and Chromium evidence

[Successful GitHub Actions run #39266763862](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39266763862) · [playable source and evidence artifact #12193582102](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39266763862/artifacts/12193582102). Archive SHA-256 `c6af7fe7b46e7298d8c86174757cc265dd25590a362fe980a656c4dde14f6b6d`.

**12/12 focused native tests passed** (six new angled-contact cases; six retained repeated-contact source/history controls). Fresh Chromium browser performed the actual first-contact calculation, changed the angle back to vertical, changed restitution, rejected invalid inputs, and reset. The real browser output matched the separate native physics and a separately computed polygon-support/contact/impulse oracle.

Existing original W13 WORLD (24 × 6 virtual cells) and previous original x-normal repeating-face Trial 03 remained unchanged. Trial 04 is a **counterfactual source boundary orientation** branch, not a replacement for the original source wall history.

The same initial rigid square is used in each branch: center (3.0,1.35), velocity (+3.0,+0.12), side length 0.5 virtual cell, unit mass, zero incoming angular velocity. The finite wall is centered on (12,1.5), length 1 virtual cell, and angle is 0° for A and 20° for B. A rectangular moment of inertia `m (side)^2 / 6` and a frictionless normal impulse with restitution are applied at the earliest polygon support contact.

### Observed comparison (browser, restitution 0.7)

| Measurement | A: 0° original vertical | B: 20° angled |
| --- | ---: | ---: |
| Source wall normal | (−1,0) | (−cos20°,−sin20°) |
| Post-contact velocity x | −2.100000000 | +0.025053799 |
| Post-contact velocity y | +0.120000000 | −0.962791866 |
| Angular velocity after first contact | **0** rad/s | **+11.352926011** rad/s |
| Off-center contact support | original right edge average | original upper-right corner |
| Follow-on surface | velocity-projected **candidate only** | differently oriented candidate **only** |

Under the initial original-W13 perfectly elastic restitution 1 baseline, the native model separately recorded vertical outgoing `[-3.0,+0.12]` versus angled `[-0.499936707,-1.153872783]` and angled spin `+13.356383543` rad/s. These are parameter-dependent, not a different source trial.

### Physical and evidence limits

The observed first collision and resulting *instantaneous* angular impulse/linear velocities are analytically verified for a frictionless rigid square at zero initial spin, against one stationary straight finite face. Only this **first event** is independently checked. The orientation 0.025 virtual seconds after impact is an **unconstrained ballistic projection**, not a numerically resolved continuous body/wall collision simulation: later interpenetration, contact persistence or a second impact has **not** been checked.

The experiment uses a **deliberate external angle input**. The wall angle was not spontaneously constructed from the prior Trial 03's saturated parallel-wall geometry. No physical fabrication scale, gravitational field, friction, material elasticity beyond idealized restitution, torque from real contact-patch deformation, or Earth-physics fidelity is established.

From the measured outgoing motion, the program derived a **proposed** differently oriented next line segment. It explicitly records `surface_built=false` and `second_contact_witnessed=false`. A proposed surface is not a functioning guide; no guide/funnel/diverter/spiral was generated, and the original full physical blueprint was not reproduced.

### Actual files and future boundary

- Source-only rigid contact model: `systems/workspace/world_ab_oblique_impact.py`
- Independent rigid-polygon support/impulse oracle and forged-event controls: `network/tests/test_world_ab_oblique_impact.py`
- Interactive extension preserving original WORLD and all previous trial scripts: `docs/world_ab_oblique_rotation.html`
- Actual native/Chromium evidence verifier: `scripts/verify_world_ab_oblique_browser.py`
- Workflow and retained screenshot/JSON: `.github/workflows/world-ab-oblique-rotation.yml`

**Next test:** physically instantiate the outbound-velocity-derived angled candidate and independently verify a new rigid-body contact with its actual orientation, body spin, and finite-wall collision response. Do not assume the projected next-look has no interpenetration before that is tested. Only after a genuinely constructed new shape works may it be counted as a new physical structure.

This is a bounded virtual research investigation, not an official NIH Phase 2 submission, a human clinical claim or a universal Earth-physics model.
