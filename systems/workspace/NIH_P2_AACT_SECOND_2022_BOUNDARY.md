# NIH P2 — independently deposited second historical AACT snapshot (2022)

**Status: candidate original archival dataset, under byte-level verification. Not an admitted historical per-study version oracle.**

## Independently attributed source

Researchers **Cathrine Axfors and Gustav Nilsonne** deposited a copy of the Aggregate Analysis of ClinicalTrials.gov (AACT) data in [Zenodo DOI 10.5281/zenodo.10091147](https://zenodo.org/records/10091147), entitled *Nordic trial reporting project: Raw data from EU Clinical Trials Registry (EUCTR) and ClinicalTrials.gov*. The deposit describes an AACT dataset reflecting **November 9, 2022**, retrieved **November 27, 2022**, and publicly deposited on **November 9, 2023**. Its file `AACT-2022-11-09.zip` has depositor-published MD5 `1d4e6d141f40d300186fdd3d0a5980b1` and is **236,218,508 bytes**.

This source is **different from the independently verified October 31, 2023 Zenodo AACT archive** in [PR #109](https://github.com/huntingthereferent/autobots-assemble/pull/109). It is also different from **Byungwoong Yoo's TrialTrace derived corpus**. Depositor collection-date and publication-date claims are attributed to their owner, not treated as independently measured timestamps for each particular registry record.

## New experiment

The [bounded archive inspector](nih_aact_second_2022_archive.py) downloads **all 236 MB** from Zenodo in a dedicated GitHub Actions runner and verifies the complete depositor MD5. It independently records full-file SHA-256, exact byte size, names, sizes and CRCs of archive members. The archive is **never extracted** into the repository, and no third-party bulk data are redistributed in the evidence artifact. When the ZIP actually contains exactly one usable `studies.txt` table, the inspector may extract only bounded rows for the two selected public identifiers `NCT04153409` and `NCT03280849` after checking headers and duplicate IDs.

If the archive is a PostgreSQL dump or another format, the observed **member inventory and classification**, not a guessed studies table, becomes the first experiment's result. A subsequent source-owned extraction and comparison would then have to be implemented and independently run. Neither this inspector nor synthetic negative-control tests can claim that a two-snapshot status difference has been observed before the actual archive is read.

## Scientific boundaries

- **A dated historical snapshot differs from a real original per-study version.** AACT's snapshot contains registry state as of a source-reported collection/export date. It does not authenticate when any one status change first appeared publicly.
- The 2022 file was **deposited in 2023**. The depositor's 2022 source collection date is attributed, not silently interpreted as the Zenodo publication date.
- Even if 2022 and 2023 archived status values differ for a shared NCT, this only brackets a change in archived observed values; it does **not** identify a precise clinical event date, an amendment/publication date, or the exact original version content.
- The deposit's **license/rights should be independently reviewed** before broader copying or reuse. This experiment retains only minimal provenance and selected fields and does not substitute a third-party license for A/B's repository license.
- [Issue #106](https://github.com/huntingthereferent/autobots-assemble/issues/106) remains unresolved until direct archived study contents and dated observation claims are independently established. No clinical verdict, new native workstation job, NIH award, or official submission is claimed.

## Reproduce and audit

```sh
python -m unittest -v network.tests.test_nih_aact_second_2022_archive
python -m systems.workspace.nih_aact_second_2022_archive --output-dir /tmp/nih-aact-2022
```

The second command requires a network connection and temporary disk space for the complete 236 MB source. The CI artifact contains a small JSON inspection receipt with the real source SHA-256, file inventory and, **only if present**, selected study rows.
