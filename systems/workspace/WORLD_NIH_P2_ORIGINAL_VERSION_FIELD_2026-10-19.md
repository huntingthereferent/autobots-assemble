# WORLD / NIH P2 — original historical version field witness

**Date:** October 19, 2026  
**Branch:** `world/w13-two-world-advance-contract-20261016`  
**Result:** Exact original-source version-specific recruitment-status field witnessed at two endpoints; original per-version first-public posting dates **still unsupported**.

## Source and independent replay

Successful [WORLD run #39213264527](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39213264527) · [observation artifact #12168965070](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39213264527/artifacts/12168965070) · artifact ZIP SHA-256 `2f504ca49c1d29388e49446f134068ca0d2b19ac8787f903cbfcf1674eee6408`.

The original public ClinicalTrials.gov Record History viewer served both pinned version pages in fresh headless Chromium:

| Original source version | Source URL | Field, in Study Details **after the selected version banner** | Exact browser-visible page-text SHA-256 |
|---|---|---|---|
| V94 | [Original V94](https://clinicaltrials.gov/study/NCT00001756?a=94&tab=history) | Recruitment status: `RECRUITING` | `4370ff462cd731f2f42cc866aadb438e4d037c7a05de2cd64fb5acb53500c3ba` |
| V105 | [Original V105](https://clinicaltrials.gov/study/NCT00001756?a=105&tab=history) | Recruitment status: `RECRUITING` | `4daab6b95ea574a0aeaea3fba36a94fd9db8df8f0dafd41eee5b87bd9a6bd9db` |

These independent live body-text hashes **match the prior exact-version public-browser access witness** in [historical issue #106](https://github.com/huntingthereferent/autobots-assemble/issues/106) and draft [PR #151](https://github.com/huntingthereferent/autobots-assemble/pull/151). A synthetic test fixture cannot claim this observation: the actual browser independently fetched the original public host at both version URLs, required the exact `Viewing V94`/`Viewing V105` banner, checked the original record ID/title and history listing, and isolated one status label/value *after* `Study Details` within that selected original version segment. Current record banners outside this region are not accepted.

**Observation:** Both exact historical version pages reported `RECRUITING`. This is a same-value two-endpoint observation, not evidence that no status change ever occurred between or outside those versions.

## Time separation

The two original page titles previously recorded submission dates V94 = August 1, 2019 and V105 = November 22, 2019, but these are **source-declared submission dates**, not authenticated original public-posting timestamps. The October 19, 2026 GitHub workflow time is the date of this *new browser observation*. There is **no independent per-version `posted_at`/first-public-access instant**, so do not derive a historically justified `known_at` from either `submitted_at` or our new `observed_at`.

The observed recruitment status is a registry record field, **not** a clinically adjudicated outcome or a verified real-world patient state. Version field `valid_at` remains independent of posting/observation clocks.

## Preserved native WORLD boundary

The same WORLD-triggered job also restored the original twelve-job NIH/W13 game from source-pinned retained journal; original twelve jobs reverified; **0 native jobs added, original runtime/coordinator journals unchanged**. Three fictional game revision events and five new synthetic browser event frames remain explicitly **separate** from the real historical ClinicalTrials.gov pages. Full focused checks: **8 original Phase 2 + 13 WORLD source/event/status + 5 original depositor checks = 26 passing tests**. The original `WORLD_W13_MOVEMENT_01.md` two-room contract remains unmodified and is **not** claimed BUILD/WITNESS-complete by these NIH game/source overlays.

## Next research boundary

Seek an original owner published **per-version posting date** for one pinned record, with source-specific evidence. Do not substitute the site's history table's *submitted date*, current record's global last-update-posted date, a later AACT capture date, or third-party Git commit time. If unavailable, mark `POSTED_AT_UNAVAILABLE` and retain current verified version-specific field contents without promoting a complete real-world temporal benchmark.

Source code: `scripts/nih_p2_world_history_field_probe.py` and `network/tests/test_nih_p2_world_history_field_probe.py`.
