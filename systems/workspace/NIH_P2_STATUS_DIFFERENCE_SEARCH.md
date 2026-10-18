# NIH Phase 2 — status changes between two original AACT archives

**Boundary:** Original archived source fields, not first publication dates of individual versions, clinical outcomes, or a new workstation job.

## The observed problem

[PR #140](https://github.com/huntingthereferent/autobots-assemble/pull/140) independently re-downloaded and verified two complete AACT historical datasets. Both preselected study identifiers, `NCT03280849` and `NCT04153409`, had recorded `overall_status=Completed` in both exports. That **negative result** prevents using those two cases as evidence of a changed *recorded status value*.

For a meaningful real-source test, this research instead asks: **Which public NCT IDs in both authenticated snapshots actually have a different recorded `overall_status` value?** This is an independently testable question without inventing a version-level timestamp.

## Fixed before seeing live results

The algorithm in [`nih_p2_historical_status_difference_search.py`](nih_p2_historical_status_difference_search.py):

1. Re-downloads **both complete third-party original deposits** and checks their depositors' whole-file MD5 and independently witnessed whole-file SHA-256 before use.
2. Verifies the 2022 ZIP member inventory and directly opens the actual `AACT-2022-11-09/studies.txt`, without unpacking/re-distributing other tables.
3. Scans all 2022 and 2023 pipe-delimited `studies.txt` records with bounded row counts. Joins records **only on exact NCT identity**; duplicate/malformed IDs or tables fail the run.
4. Compares statuses using only outer whitespace/case normalization so `COMPLETED` and `Completed` aren't mistaken for different status meanings. Records spelling-only differences separately from substantive source-field changes.
5. Records shared/missing NCT counts, same-status counts, different-status counts, status field-pair frequencies and **at most eight changed source-status anchors**, selected by **lexicographically smallest NCT IDs** independent of the row scan order. The selected anchors keep **exact original status spelling and the source-recorded last-update-posted values from both snapshots**.
6. Preserves both archive identifiers, source owners, hashes, depositor publication dates, and explicit **false** values for clinical-event time, individual revision posting time, and any claim of excluding intervening changes.

The source labels must remain distinct:

- **2022-dated snapshot:** Cathrine Axfors and Gustav Nilsonne's AACT deposit [Zenodo 10.5281/zenodo.10091147](https://zenodo.org/records/10091147). Depositors state 2022-11-09 as dataset date, 2022-11-27 as retrieval date, while Zenodo publication was 2023-11-09.
- **2023-dated snapshot:** [Zenodo record 10058991](https://zenodo.org/records/10058991), published 2023-10-31. It is a different complete source and not a per-study history endpoint.

## What this test can and cannot show

When a case has different statuses in the two archives, the **recorded exported values differ**. It supports a time-bounded observation of changed source fields and a reproducible test case for the A/B evidence-selection rules. It does **not** establish that the study's clinical state actually changed, exactly when the first public record was updated, or whether other revisions occurred between the two exports.

The selected anchors remain independently dated *source snapshots* with status observations, not original authenticated per-study version sequences. The [unresolved historical-version evidence issue #106](https://github.com/huntingthereferent/autobots-assemble/issues/106) remains open.

This experiment uses no new W13 native jobs and does not modify the original twelve-job runtime, native journals, CI lineage, Phase 1 draft, or A/B license. It does not submit to NIH. Source ownership and redistribution restrictions remain attributable to the depositors; only minimal public status observations and hashes enter the small receipt.

## Reproduce

```sh
python -m unittest -v network.tests.test_nih_p2_historical_status_difference_search
python -m systems.workspace.nih_p2_historical_status_difference_search \
  --output-dir /tmp/nih-p2-original-source-status-differences
```

The actual scan requires approximately 526 MB in temporary source downloads. Unit fixtures establish **only negative controls**. The dedicated full-source CI must succeed before any observed count or anchor is admitted as real historical source evidence.
