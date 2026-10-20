# NIH Phase 2 — adjacent original historical version observation

**Question:** The original official V105→V260 study record changed `Overall Status` from Recruiting to Completed. Did the change occur at **adjacent historical versions V259→V260**, or earlier?

The original evidence in [PR #259](https://github.com/huntingthereferent/autobots-assemble/pull/259) proves only a difference between the distant V105 and V260 source versions. It does **not** locate the earliest changed version, public posting time, the date a clinical status became effective, or a medical conclusion.

This continuation freezes two adjacent candidates in the official study `NCT00001756` public Record History: V259 (source index submitted 2022-10-26) and V260 (submitted 2022-11-04). The source index suggests the V260 edit touched Recruitment Status. **An index change label does not prove `Overall Status` changed.**

## Actual narrow source test

1. Navigate directly to two original official version URLs with a clean Chromium profile and no credentials.
2. Verify the exact requested URL, historical `Viewing V259` / `Viewing V260` banner, study ID/title, source-index submitted day, public route, HTTP 200, and unique version-local `Study Status` section.
3. Read only the original version-local `Overall Status`, `Last Update Submitted that Met QC Criteria`, and `Last Update Posted` with Exact/Estimated qualifier. Do not reuse the current-study summary or a history-index label.
4. Compare actual values; **both changed and unchanged statuses are valid outcomes**. If either page fails admission, return `UNAVAILABLE`.
5. Retain only source URL, field values, UTC retrieval, SHA-256 of original visible source and local section, and non-promoting uncertainty flags. Never redistribute page bodies, personal/sponsor data or clinical records.

Observed original `Last Update Posted` values do not independently establish first-public availability time of the exact version. A `known_at` claim for W13 remains blocked until this evidence link is authenticated independently. No private native journal or original W13/World48 program is modified.

## After observation

- If V259 and V260 differ, the observed record-level status change is localized to adjacent **submitted versions**. It still does not establish clinical event date or exact original version-first-public timestamp.
- If V259 and V260 match, preserve that negative observation and test a preceding pair using the original history index, without inventing a difference.
- If original source is inaccessible or its version/date identity differs, preserve the explicit wall without retroactively changing expected data.

Run:

```bash
python -m unittest -v network.tests.test_nih_p2_official_adjacent_status
python -m systems.workspace.nih_p2_official_adjacent_status --out-dir /tmp/nih-p2-adjacent
```

Live browser evidence is independently retained by the dedicated GitHub workflow. The outcome is a bounded source observation, not an NIH Phase 2 benchmark, new physical law, medical inference or submitted competition result.
