# NIH Phase 2 — independent archival corroboration of an original adjacent record change

**This investigates one source relationship, not another world or a new Phase 2 implementation.**

The official ClinicalTrials.gov public Record History for `NCT00001756` already produced a native independently witnessed source difference:

- Original version **V259**, submitted **2022-10-26**, recorded **Recruiting**, version-local **Last Update Posted 2022-10-27 [Actual]**.
- Original version **V260**, submitted **2022-11-04**, recorded **Completed**, version-local **Last Update Posted 2022-11-07 [Actual]**.

Source: [original Chromium run #39421372666](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39421372666), minimal [source artifact #12264180158](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39421372666/artifacts/12264180158) and [NIH PR #261](https://github.com/huntingthereferent/autobots-assemble/pull/261). This is a *record-version* change, not a proven time when a clinical phenomenon changed.

The separate [NIH PR #263](https://github.com/huntingthereferent/autobots-assemble/pull/263) proved that the National Library of Medicine defines `Last Update Posted` as when updated registry information is made public. It preserved the important distinction between *source-reported date* and independently authenticated exact-version first-publication event.

## One new independent outward source check

Two **independently deposited complete AACT datasets** already have verified original byte identities:

1. [Lalagkas original Zenodo 10058991 `AACT_studies.txt`](https://zenodo.org/records/10058991), published **2023-10-31**; original author's publicly pinned source script **attests the AACT download on 2022-11-04**, and links to the exact deposited file ([separately verified owner attribution](NIH_P2_AACT_OWNER_DATE_LINK.md)). SHA-256 `bed698312a04292fc31f7ea71130731acc9b57723399ab1b45c0f6d70a304d49`.
2. [Axfors/Nilsonne Zenodo 10091147 `AACT-2022-11-09.zip`](https://zenodo.org/records/10091147), originally reported as AACT data of **2022-11-09**, downloaded on **2022-11-27**, and only deposited **2023-11-09**. SHA-256 `d1d4fb04a121e03f2ac08bacef708a896f7240d5ff025104ed7512b60408d755`.

These owner-*attested* collection days fall on opposite sides of the registry's source-reported **November 7** posting. **This is a prospective candidate, not yet a verified coincidence.** Both entire original downloads (~526MB) must be re-authenticated against depositor MD5 plus previously recorded SHA-256, followed by extracting only exact `NCT00001756` rows.

The experiment records each independent archive's original `overall_status` and `last_update_posted_date`, compares each with its contemporaneous proposed official version, and records agreement/disagreement as **an observation**, with no hard-coded outcome.

A different archival status across owner-reported November 4 and November 9 and agreement with official V259 and V260 would **corroborate** (not independently date) the reported registry change. A same-status pair or mismatch is equally valid negative evidence.

## Non-overlapping timestamp contracts

- **Clinical valid time:** UNKNOWN. Neither published study records nor original archival snapshots establish when an underlying physical clinical state changed.
- **Version submission dates:** original registry record-history banner dates.
- **Version-local Last Update Posted dates:** public registry's *source-reported* posting metadata.
- **Source-owner archive extraction dates:** owner-attributed Nov 4 and Nov 9, *not* witnessed independent 2022 HTTP captures, and not the later Zenodo deposit dates.
- **Our observation:** fresh GitHub Actions download in October 2026.
- **Version-specific independent first-publication proof:** still UNSUPPORTED. An archive row is a snapshot, not an authenticated original numbered version, and a source owner statement isn't a timestamping authority.

No third-party archive is stored in GitHub or redistributed by the runner. Only a minimal source and comparison report and hashes are retained. A mismatch or unavailable whole-source download must stop original-source admission; no fabricated alternate source.

This uses the existing verified `nih_aact_archival_source`, `nih_aact_second_2022_archive`, and the unchanged official V259/V260 source receipt. The original twelve-job W13 world/journal, Phase 1 draft, Phase 2 draft, World48 laws, current WORLD trial and repo license stay untouched.

## Replay and next movement

```bash
python -m unittest -v network.tests.test_nih_p2_independent_aact_registry_corroboration
python -m systems.workspace.nih_p2_independent_aact_registry_corroboration \
  --output-dir /tmp/nih-aact-v259-v260-source
```

After original cross-source execution: if the independently deposited full sources corroborate the exact public record change, preserve the strongest supported source statement **without claiming first-public timestamp**. Then investigate genuinely independent historical version-level release evidence for [issue #106](https://github.com/huntingthereferent/autobots-assemble/issues/106) before admitting real `known_at` into original W13 temporal semantics. The original W13 emitted Python still only accepts synthetic datasets. Do not silently relabel it as a clinical/real-source reasoner.
