# WORLD — A/B relation-derived physical construction, trial 02

**2026-10-19 · Existing WORLD branch** `world/w13-two-world-advance-contract-20261016`

**Result:** a newly instantiated virtual collision face was calculated **from the first observed rebound** and subsequently struck during a fresh continuation of the same moving block. Independent analytic and live Chromium witnesses passed. **Full physical blueprint equivalence remains disproven/not established by the observed evidence.**

## What actually changed in WORLD

The original 144-cell physical WORLD (`docs/world_phase1_phase2_physical.html`) and preceding one-wall A/B trial (`docs/world_ab_contact_trial.html`) were preserved. An additional executable layer was added:

- `systems/workspace/world_ab_relation_growth.py` — observation-driven geometric **assembly policy**, event-driven two-contact simulation and immutable source-wall relationship.
- `docs/world_ab_relation_growth.html` — playable LOOK / CONSTRUCT / REPLAY / NEXT LOOK sequence within the same original physical WORLD. A/B first motion is run independently; source contact is required before the construct action.
- `network/tests/test_world_ab_relation_growth.py` — independent **closed-form two-event analytical oracle**, negative contact/no-rebound controls, restitution changes, fabricated source mutants and original visual reference comparison.
- `scripts/verify_world_ab_relation_growth_browser.py` — real Chromium click/run with host-native simulator and separately implemented analytic verification, preserved earlier page scripts, screenshot and retained receipts.
- `.github/workflows/world-ab-relation-growth.yml` — new source-path-filtered execution and artifact retention.

The model is a bounded rigid translating square, virtual x/y grid, no gravity, friction, angular dynamics, material deformation, or calibrated real-world units. The **source geometry is unchanged**: west wall at x=12, y 1–2, square half-width 0.25.

## Relation-derived assembly, not preset blueprint construction

**Declared construction policy:** after independently observing original source-wall contact and its outgoing velocity, project the contact position forward for **0.75 virtual seconds** along the observed outgoing direction. Install a **finite, vertical receiver face** centered on this projected trajectory, with span inherited from the original wall. Do not use the original A/B diagram's desired structure names or shapes as generator input.

For initial square center (3.0, 1.35), velocity (+3.0, +0.12), restitution 1:

| Witnessed event | Bounded source measurement |
| --- | --- |
| Original source wall contact | t=**2.916666667**, x=11.75, y=1.70 |
| Actual outgoing velocity | (−3.0, +0.12) |
| Constructed new face x | **9.50** (11.75 + −3.0 × 0.75) |
| Constructed vertical y interval | **[1.29, 2.29]** |
| Second physical surface contact | t=**3.583333333** at x=9.75, y≈1.78 |
| Final position at t=4 | x=**11.0**, y=**1.83** |

**Independent analytical reference:** contact 1 at `(12−0.25−x0)/vx0`; contact 2 when the west-moving block's left extent meets the constructed receiver face. The oracle calculates all 17 state samples from two exact contact times and the restitution law, not from the generator's per-step event loop. It checks source face position/span, both impulses, and every position and velocity value.

## Actual successful evidence

[GitHub Actions run #39248172690](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39248172690) **SUCCESS**; [retained source, screenshot, actual 17-frame motion and independent evidence artifact #12183109682](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39248172690/artifacts/12183109682); ZIP SHA-256 `0972099b35ec45e58d9be7f572ea285da1d7b117423fc80e681c74718870d26f`.

- **18/18 focused tests passed** (7 original contact controls, 6 new composition controls, 5 physical fit controls).
- New original-WORLD Chromium page executed original A/B block–wall trajectory, constructed the receiver only after observed source contact, replayed the *same block* into a second collision, observed its second outgoing movement, and independently verified all 17 frames.
- New face position **changed** under restitution 0.5; a block missing the original wall generated **no surface**; completely inelastic contact (zero horizontal rebound) generated **no surface**; forged event times/impulses/frame values/surface geometry failed independent analytical tests.
- Original source wall, original prior scripts, existing 24×6 layout, source-room contract and historical evidence are unchanged.
- Generated physical relation is **one additional, actually usable virtual collision face**, instantiated by an explicit user-authored algorithm. This is not spontaneous material self-assembly, independent validation of Earth physics, or a full shape-generating physics engine.

## Original drawing comparison

The owner's `Visual Language A_B Exploration Blueprint.png` was referenced **only in the independent result comparator**. The trial recovered approach, first contact/deflection, new physical contact surface, reuse in a second collision, and continued movement. It did **not** generate the full original guide, funnel, diverter, or spiral structures. The face was intentionally **not relabeled** a guide in order to claim success. The original artifact comparison reports these four required structures missing.

**Actual next boundary:** test whether repeated observation-derived transformations produce structurally novel compositions *without injecting desired geometry or target labels*. To claim a larger complex world, verify the resulting shapes' topology/functional behavior independently, rather than renaming repeated vertical receivers. Keep physical units and material-law limitations explicit. No official NIH submission, clinical inference, or broader physics completeness is claimed.
