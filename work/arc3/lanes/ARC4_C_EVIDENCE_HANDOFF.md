# ARC4 lane C — evidence, provenance, and handoff

**Evidence cutoff: 2026-10-22.** This document indexes what the original SP80 SDK has actually established. It is not a solver, new native test, or a claim about hidden game logic.

## Official checkpoint: 4/6

Original `arc_agi.Arcade(OperationMode.NORMAL)` stage3→4 advancement was first observed in genuine run [#39616395169](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39616395169), with independent original entrance histories A and B agreeing on the frozen native intervention (`catch_left3_up5`). [Merged PR #367](https://github.com/huntingthereferent/autobots-assemble/pull/367) pinned the native stage4 entry, selected-object inventory, genuine level/state, and raw frames. The exact replay word is preserved as `STAGE3_WINNER` in [source](../native_sp80_stage4_entry_inventory.py); do not copy it inaccurately into a summary.

## Level-4 frontier

[Merged PR #372](https://github.com/huntingthereferent/autobots-assemble/pull/372) verified a selectable L-shaped native 27-pixel piece previously omitted from level-4 movement tests.

[Merged PR #379](https://github.com/huntingthereferent/autobots-assemble/pull/379) established a source-observed tradeoff between left-lateral and top-left visual cup coverage. Later source interventions produced original-frame cases where all four measured 45-pixel cup windows became palette13 while the **measured left boundary** did not visibly change. These cases did **not** advance the SDK.

The latest [draft PR #398](https://github.com/huntingthereferent/autobots-assemble/pull/398), [original run #39726675675](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39726675675), executed 20 genuine original SDK games (five upper-bar settings, two independently held lower arrangements, two entrance witnesses). All 20 remained `levels_completed=4, NOT_FINISHED`. Six original game resets (three condition pairs) had all four measured cup regions full simultaneously **without measured left-border change**. Both witnesses agreed case by case. The native, ARC-direct-continuity and repository protocol workflows passed on the draft PR's exact head. The PR was **not merged** at the evidence cutoff.

**These are pixel events, not an official WIN rule.** Top, right, and bottom early source transitions still require an event-order audit. Reversible post-pour tests in [draft #392](https://github.com/huntingthereferent/autobots-assemble/pull/392) returned 24/24 official level4 results and did not establish a movement-history cause.

## Independent lanes, no silent data promotion

- **A — original-frame event order:** [PR #407: contract and original-native audit](https://github.com/huntingthereferent/autobots-assemble/pull/407) (separate experimental branch). Freeze three source-positive conditions and matched controls. Independently measure first original source-frame events at all four boundaries and outside cup windows. Preserve complete JSON/NPZ.
- **B — source-pinned intervention:** [PR #408: intervention contract and gate](https://github.com/huntingthereferent/autobots-assemble/pull/408) (separate experimental branch). Gate a single new original SDK movement on the exact observed event coordinate and original selected-object receipts; no automated candidate selection from guessed physics. A green test gate alone does not mean a native experiment has occurred.
- **C — this evidence index:** update canonical status, provenance and artifact retention without changing game behavior, numeric results, the ARC-like F3 mathematics, NIH, or WORLD.

All three branches begin from the same main baseline and target main independently; never treat an unmerged lane as part of the canonical code. Results of A may be imported as an explicit, source-pinned handoff into B, not as uncontrolled cross-branch rewriting.

## Present walls

- No authentic original SDK level5 or WIN yet.
- No proven mapping from the finite-field 48-law mathematical family to native ARC action IDs or SP80's objective rule.
- The observed four-cup pixels do not capture every off-cup/boundary event.
- GitHub Actions artifacts have per-run retention; a URL alone is **not** a durable archival guarantee. Keep an evidence index with checksum, commit, run ID and actual copied raw bytes before expiry.

## Resume

Read [evidence index](../runs/ARC4_EVIDENCE_INDEX_2026-10-22.md), the actual [stage4 entry implementation](../native_sp80_stage4_entry_inventory.py), and PR #398 original raw frames. Prefer lane A's first-event source evidence before constructing the lane B intervention. Count only source SDK `levels_completed >= 5` or `WIN` as the next game milestone.
