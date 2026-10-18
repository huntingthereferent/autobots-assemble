# NIH P2 — independently released archived source (2023)

This is a separate public archival-intake experiment after
[PR #105](https://github.com/huntingthereferent/autobots-assemble/pull/105)
and the source-refusal boundary in
[PR #107](https://github.com/huntingthereferent/autobots-assemble/pull/107).
It does not extend the original twelve-job workstation or claim an official
NIH Phase 2 award/submission, clinical validity or patient-level data.

## Source and verification

An identifiable, immutable third-party [Zenodo deposit
10.5281/zenodo.10058991](https://zenodo.org/records/10058991)
was published on **2023-10-31**, describing files originally downloaded from
the Clinical Trials Transformation Initiative's AACT database.

The deposited file `AACT_studies.txt` is approximately 289.6 MB and has
depositor-published **MD5 d043fb7704bcff8cfb5be95d4f5ced85**.
The CI source worker downloads that exact published file, enforces a bounded
370 MB upper limit, verifies **the checksum of the complete file** before
using any rows, computes a new whole-file SHA-256, and independently extracts
only two identified public trial statuses and minimal date fields.

The worker also separately calls the documented **current**
[ClinicalTrials.gov API v2](https://clinicaltrials.gov/data-api)
for the same exact NCT identifiers, recording a SHA-256 of each live response,
the URL and UTC observation time, plus the two source values and whether they
differ. A different value in 2023 and now is **not** proof of the exact date
or reason it changed.

The archived **source file is never uploaded into repository artifacts**;
only small derived study-status receipts and whole-file source hashes are kept.

## Time and provenance limits

* The Zenodo deposit date is a **bound on when this deposited dataset became
  publicly accessible**; it does not establish when AACT extracted the data
  or when any individual study amendment was posted.
* The deposited file is attributed to a university depositor who describes
  retrieving it from AACT. It is *not* misrepresented as an original official
  ClinicalTrials.gov signed historical revision.
* No version number for an individual registry study is derived from an
  archived row. The data is a historical dataset snapshot, not a study's
  authenticated version-history API.
* The source's historical `overall_status` is registry metadata recorded in
  that snapshot. It is **not** a patient outcome or a clinical effectiveness
  assessment.
* The independently fetched current status is knowable at the UTC retrieval
  time. The experiment **does not backdate it** to 2023 or to a study's
  first-posted date.
* A verified mismatch is evidence that the two source observations differ,
  **not** evidence that the underlying clinical event changed at a known time.
* MD5 is checked for matching the depositor's published file digest, not used
  as a stand-alone collision-resistant signature. SHA-256 is recorded from
  the complete observed bytes for additional identification.

## Verification and rejection

All of the following must hold before this external dataset is admitted:

1. The original Zenodo file downloads within limits and matches the
   depositor-published whole-file digest exactly.
2. The historical source has the expected header and contains exactly one
   bounded well-formed row for each of the two preselected NCT IDs.
3. The independently obtained official current API results identify those
   same NCT IDs and return bounded registry statuses.
4. The minimal receipts state uncertainty about per-study posting time and
   do **not** declare any official NIH or clinical benchmark result.
5. The dedicated GitHub Actions run and full repository suite pass on the
   same current PR head. Otherwise preserve failure and no merge.

Local unit tests use tiny artificial CSVs only to exercise checksum,
identity, duplicate-row and evidence boundaries. Those fixtures never count
as live source evidence.

## Reproduce

```bash
python -m unittest -v network.tests.test_nih_aact_archival_source
python -m systems.workspace.nih_aact_archival_source \
  --output-dir /tmp/nih-aact-source
```

The live step downloads the actual approximately 289.6 MB dataset, and
requires Internet access. The download is temporary; retain only the
verified minimal evidence receipt.

See [issue #106](https://github.com/huntingthereferent/autobots-assemble/issues/106):
authenticated **specific study version** history and corresponding public
posting times remain unverified even after a dated historical snapshot passes.
