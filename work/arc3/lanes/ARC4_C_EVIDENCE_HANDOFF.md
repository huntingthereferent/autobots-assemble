# ARC4 lane C — evidence, provenance, and handoff

**Evidence cutoff: 2026-10-22.** This document indexes what the original SP80 SDK has actually established. It is not a solver, new native test, or a claim about hidden game logic.

## Official checkpoint: 4/6

Original `arc_agi.Arcade(OperationMode.NORMAL)` stage3→4 advancement was first observed in genuine run [#39616395169](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39616395169), with independent original entrance histories A and B agreeing on the frozen native intervention (`catch_left3_up5`). [Merged PR #367](https://github.com/huntingthereferent/autobots-assemble/pull/367) pinned the native stage4 entry, selected-object inventory, genuine level/state, and raw frames. The exact replay word is preserved as `STAGE3_WINNER` in [source](../native_sp80_stage4_entry_inventory.py); do not copy it inaccurately into a summary.

## Level-4 frontier

[Merged PR #372](https://github.com/huntingthereferent/autobots-assemble/pull/372) verified a selectable L-shaped native 27-pixel piece previously omitted from level-4 movement tests.

[Merged PR #379](https://github.com/huntingthereferent/autobots-assemble/pull/379) established a source-observed tradeoff between left-lateral and top-left visual cup coverage. Later source interventions produced original-frame cases where all four measured 45-pixel cup windows became palette13 while the **measured left boundary** did not visibly change. These cases did **not** advance the SDK.

The latest [draft PR #398](https://github.com/huntingthereferent/autobots-assemble/pull/398), [original run #39726675675](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39726675675), executed 20 genuine original SDK games (five upper-bar settings, two independently held lower arrangements, two entrance witnesses). All 20 remained `levels_completed=4, NOT_FINISHED`. Six original game resets (three condition pairs) had all four measured cup regions full simultaneously **without measured left-border change**. Both witnesses agreed case by case. The native, ARC-direct-continuity and repository protocol workflows passed on the draft PR's exact head. The PR was **not merged** at the evidence cutoff.

**These are pixel events, not an official WIN rule.** The subsequent original-SDK lane A event-order audit is complete for its specified source windows; the unmeasured or broader boundary regions and private game objective remain unproven. Reversible post-pour tests in [draft #392](https://github.com/huntingthereferent/autobots-assemble/pull/392) returned 24/24 official level4 results and did not establish a movement-history cause.

## New independently replayed source-event finding

The separate [lane A native run #39729756294](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39729756294) passed its 10 original SDK resets. In all three visual-positive source conditions, the **first measured top and right boundary changes occurred at frame21** despite no observed left/bottom boundary changes. This reinforces that "clean lateral" meant a *specific left-side observation*, not that all boundaries were quiet. The frozen lane A events are indexed [here](../runs/ARC4_EVIDENCE_INDEX_2026-10-22.md). The run has zero official level5/WIN.

## First Lane B original SDK intervention result

Lane B's [source-pinned native run #39731621139](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39731621139) compared the exact same level4 source arrangement with and without one additional upper-bar DOWN1 action, preserving its existing selection. The native original selected-bar position and returned full-frame hashes changed, while four-cup timing, first measured top/right boundary timing, off-cup first arrivals, and all four official `levels_completed=4, NOT_FINISHED` outcomes remained unchanged. Source [artifact #12405441391](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39731621139/artifacts/12405441391). This is a **negative, bounded one-factor result**, not an objective inference.

## Distinguishing actual original success from level4 visual nonprogress

**Current controlled SDK comparison (2026-10-22):** [original run #39762841397](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39762841397) verified four independent original-SDK resets: two predeclared level4 pour conditions, each with A/B independent entrances. Every session authentically advanced **stage3→4** on SDK ACTION5, then stayed **stage4→4** on a later native ACTION5. The successful stage3 returned source palette13 `180→0` over its last two frames while advancing; the four-cup level4 nonadvance also returned `180→0` without advancing. The three-cup control returned `135→0` without advancing. Genuine stage3 winning terminal root hash `fa8fd32d3bfd2c8b3ff7765aec373512` is the independently reproduced stage4 entry. Full original JSON+NPZ [artifact #12418353014](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39762841397/artifacts/12418353014), ZIP SHA-256 `67bd82eb42be10f4b53a16a5cd37ed47c453cab2cf8cd1c0065c2dd0d4f03c40`.

**Do not resume by inferring the stage4 success rule from cup fill, terminal clearing, or row63.** All have native counterexamples. The remaining wall is to identify a reproducible original-source contrast specific to a *genuinely advancing* action, or state explicitly that level4 advancement remains unobserved. Continue from the exact source evidence index and preserve A/B source/action receipts and artifact retention.

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

## Resume — current verified source checkpoint (October 22, 2026)

**Official original SDK: level 4/6, no level5 or WIN**, including all new genuine Stage4 native experiments; the older PR #398 material above is historical, not the latest evidence boundary.

The latest independently native-verified frozen test is [same-game repeated pours #39768996710](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39768996710) with raw [SDK frames/receipts #12422021789](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39768996710/artifacts/12422021789), ZIP SHA256 `0ea3addf36bf716e8e9d006df32ec0b165d3b65aa61b97e9e4a9cf32a1c7ab2f`. Twelve genuine original native resets, two right-bar positions crossed with 1/2/3 ACTION5s in the same game, source A/B entrances. **All official level4 NOT_FINISHED**. Extra pours reproduce all frame pixels in y0..62 across the same 34-frame animation; all differences are bottom row y63 only, where a single palette14→0 pixel may change or none. Original first pour also returns a genuine selected-object transfer: 36 pixels upper 9→8 and 45 pixels right 8→9. This boundary does **not** prove underlying internal state equivalence or establish the SDK objective.

Previously verified: [upper/right interaction #39766706911](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39766706911) (12 SDK resets, no level5), [stage-specific source cups #39764626858](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39764626858), [actual successful level3 versus stage4 nonadvancing pours #39762841397](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39762841397), and [independent terminal-screen audit #39765735502](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39765735502). The original level3 success redraws the measured left wall only on the final screen; the failed level4 four-cup pour does not. The redraw is an observed **consequence** of official progress, not a decoded triggering rule. Four simultaneously full cup regions during animation are insufficient.

**Active handoff:** read [full source and SHA index](../runs/ARC4_EVIDENCE_INDEX_2026-10-22.md), actual [native original stage4 entry implementation](../native_sp80_stage4_entry_inventory.py) and [Lane B intervention records](ARC4_B_INTERVENTION.md). Do not repeat source-disproved directions (row63 as a goal rule, four-cup filling alone, vertical upper ±1 in the held configurations, one/two/three no-movement repeated pours). Any next candidate must name exact source-native frames/receipts, a differentiating observed event, two independent SDK entrance witnesses and a separately testable outcome. **Only original SDK `levels_completed >= 5` or `WIN` advances the checkpoint.** Keep independent A/B/C draft PRs separate and unmerged.
