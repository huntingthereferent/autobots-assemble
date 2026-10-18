# NIH Phase 2 — status changes between two original AACT archives

**Boundary:** Original archived source fields, not first publication dates of individual versions, clinical outcomes, or a new workstation job.

## The observed problem

[PR #140](https://github.com/huntingthereferent/autobots-assemble/pull/140) independently re-downloaded and verified two complete AACT historical datasets. Both preselected study identifiers, `NCT03280849` and `NCT04153409`, had recorded `overall_status=Completed` in both exports. That **negative result** prevents using those two cases as evidence of a changed *recorded status value*.

For a meaningful real-source test, this research instead asks: **Which public NCT IDs in both authenticated snapshots have a different recorded `overall_status` value, without assuming an order for the underlying source snapshots?** This is an independently testable question without inventing a version-level timestamp.

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

## Unexpected source chronology: later Zenodo publication is not later AACT collection

The independent first scan found **432,983** NCT rows in the dataset whose owner dates its source to **November 9, 2022**, but **432,597** in the *other file*, which was **uploaded to Zenodo October 31, 2023**. Every one of the latter file's NCT IDs occurs in the 2022-dated dataset: **386 IDs in the 2022-dated file are absent from the October 2023 *deposit*, with zero IDs exclusively in the later deposit**. Some source-recorded `last_update_posted_date` values also run **backward** when read in Zenodo-deposit order. These are directly observed source anomalies, not evidence that official registry history moved backward.

A highly relevant same-author publication, **Panagiotis N. Lalagkas and Rachel D. Melamed, *Shared etiology of Mendelian and complex disease supports drug discovery* (BMC Medical Genomics 2024; DOI 10.1186/s12920-024-01988-3)**, explicitly says the researchers downloaded AACT on **November 4, 2022** and obtained **432,597 studies**—the *exact* number of study IDs in the October 2023 Zenodo deposit from Lalagkas. This strongly suggests its underlying material may actually precede the November 9, 2022 AACT data, but the author paper is **not** a cryptographic attestation that the exact Zenodo file is the referenced November 4 download. The deposit page itself does not specify the underlying file extraction date.

Thus a later **Zenodo deposit date must not be substituted for the underlying AACT snapshot date**. Both files are authenticated *as original immutable deposited artifacts*, but the **chronological order of their underlying source observations remains UNRESOLVED**. The 1,345 differing recorded statuses are reproducible cross-file discrepancies, **not proven transitions from November 2022 to October 2023**. A changed `last_update_posted_date` field is not proof of a unique original registry revision publication transaction. The output explicitly retains this ambiguity and counts backwards-moving source-recorded dates.

Original sources: [Lalagkas Zenodo record (published October 31, 2023)](https://zenodo.org/records/10058991), [Axfors/Nilsonne Zenodo record (AACT collection November 9, 2022)](https://zenodo.org/records/10091147), [Lalagkas/Melamed peer-reviewed article](https://pmc.ncbi.nlm.nih.gov/articles/PMC11385846/).

## What this test can and cannot show

When a case has different statuses in the two archives, the **recorded exported values differ**. It establishes a reproducible two-source discrepancy, but **not a justified direction of time between the original extracts** until provenance resolves the underlying extraction date of both files. It does **not** establish that the study's clinical state actually changed, exactly when the first public record was updated, or whether other revisions occurred between the two exports.

The selected anchors remain independently dated *source snapshots* with status observations, not original authenticated per-study version sequences. The [unresolved historical-version evidence issue #106](https://github.com/huntingthereferent/autobots-assemble/issues/106) remains open.

This experiment uses no new W13 native jobs and does not modify the original twelve-job runtime, native journals, CI lineage, Phase 1 draft, or A/B license. It does not submit to NIH. Source ownership and redistribution restrictions remain attributable to the depositors; only minimal public status observations and hashes enter the small receipt.

## Reproduce

```sh
python -m unittest -v network.tests.test_nih_p2_historical_status_difference_search
python -m systems.workspace.nih_p2_historical_status_difference_search \
  --output-dir /tmp/nih-p2-original-source-status-differences
```

The actual scan requires approximately 526 MB in temporary source downloads. Unit fixtures establish **only negative controls**. The dedicated full-source CI must succeed before any observed count or anchor is admitted as real historical source evidence.
