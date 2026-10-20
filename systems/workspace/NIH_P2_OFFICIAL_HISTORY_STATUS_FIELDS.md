# NIH Phase 2 — first original version-local status content

**Question:** Can the original public ClinicalTrials.gov Record History viewer provide a historically selected status value independently of the current study summary?

Source continuity: [PR #151](https://github.com/huntingthereferent/autobots-assemble/pull/151) witnessed exact public versions 94 and 105 of `NCT00001756`, but intentionally did **not** inspect source-specific field content. [Historical-content issue #106](https://github.com/huntingthereferent/autobots-assemble/issues/106) remains open.

## Bounded native observation

A fresh headless Chromium process navigates the original official `https://clinicaltrials.gov/study/NCT00001756?a=94&tab=history` and `a=105` pages. The unchanged PR #151 validator first authenticates the expected official host, exact URL, selected version banner, target study title and identifier.

Only *after* `Viewing V94 (...)` or `Viewing V105 (...)`, the parser locates the version-specific `Study Details → Study Identification → Study Status` section and stops before `Sponsor/Collaborators`. That excludes the current-study header and the long record-history index.

For each source view, record **only**:

- Version number, exact source URL, source text hash, retrieval UTC.
- Exact observed `Overall Status`, without assuming a status change between versions.
- The version-local `Last Update Submitted that Met QC Criteria` and `Last Update Posted` values, including `Actual` versus `Estimated`.
- Version-banner submitted date; whether QC-submitted date matches that banner; SHA-256 of the selected original Study Status section.
- A hard-coded **false** claim flag for independent verification of that version's first-public posting date.

The original browser text and potentially sensitive page details are discarded. A live failed read emits `UNAVAILABLE`, never invented earlier study content. Negative controls reject a forged body hash, a mistaken current-page field, duplicate status, unsupported values, invalid dates, a fake banner, wrong source route, and promotion of reported posted dates to an independently proven *first-public* timestamp.

## Temporal boundary

A version-local `Last Update Posted` value is stronger provenance than the current study header's update date or the history table's `Date submitted`. However, recording this field is **not by itself** an independent verification of when that *exact historical version* first became public.

The report therefore sets `public_known_at_admitted_for_temporal_program=false` and `historical_first_publication_attribution=UNAVAILABLE`, regardless of whether exact historical status values were observed. No fabricated `known_at` enters W13, and synthetic temporal test results remain synthetic.

**Next source question:** independently establish the registry's meaning and version identity of the historical posted date, corroborate the exact version's public posting time, then test version-specific correct/incorrect historical temporal answers with an independent oracle. If the source lacks this link, preserve the wall.

No new universal world engine, World48 dependency, W13 13th job, original journal update, medical inference, competition submission or clinical result.

## Verification

```bash
python -m unittest -v network.tests.test_nih_p2_official_history_status_fields
python -m systems.workspace.nih_p2_official_history_status_fields --output-dir /tmp/nih-version-status
```

Only a successful live original Chromium run (not synthetic negative tests) can witness the selected historical version fields.
