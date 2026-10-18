# NIH P2 — primary CTTI historical AACT snapshot catalog access

**Read-only original-source access experiment. No downloaded historical archive and no per-version posting-time proof.**

The CTTI AACT site's [historical snapshot catalogue](https://aact.ctti-clinicaltrials.org/downloads/snapshots?type=flatfiles) is the *source owner's* published route for archived bulk registry exports. Search-indexed historical page listings display archive years 2017–2026; for example its [2023 listing](https://aact.ctti-clinicaltrials.org/downloads/snapshots?type=flatfiles&year=2023) lists monthly archived filenames. The current [owner landing page](https://aact.ctti-clinicaltrials.org/landing) separately says account access is used for downloads.

A search index listing, however, is **not** evidence that a source archive is still accessible for an unauthenticated native script, that any proposed November 2022 file URL exists, or that a specific NCT original registry version was publicly posted at the archive's labeled date.

## Source-ownership experiment

[`nih_p2_ctti_owner_catalog_2022.py`](nih_p2_ctti_owner_catalog_2022.py) retrieves **only three CTTI-hosted public catalog pages**—the modern flatfiles/year=2022 URL, the legacy year-filtered snapshot URL, and the legacy unfiltered snapshot fallback—without credentials. It stores the exact HTTP status, basic page title, presence of sign-in language, and only genuinely observed 2022 archive links anchored by the returned original owner HTML. The scan rejects guessed date-formatted archive names, unsafe/cross-host links, signed URL/token-bearing parameters, invalid calendar dates and oversized HTML.

In the event CTTI redirects to sign-in or returns 401/403/404, **that is the research finding**, not proof there is no historical archive. The probe never guesses a direct source archive URL, never clicks through access restrictions, and never downloads a multi-gigabyte ZIP or bulk patient-related dataset. This is a discovery/access experiment; any actual published archive link still requires an independent next experiment for a HEAD metadata check, owner rights review, bounded download capacity and whole-file SHA-256 before individual source rows can be compared.

The existing two-Zenodo original archive research is retained in [merged PR #141](https://github.com/huntingthereferent/autobots-assemble/pull/141), and original-depositor file/date attestation is retained in [merged PR #145](https://github.com/huntingthereferent/autobots-assemble/pull/145). They establish **original deposited source file bytes and owner-attested collection dates**, not original ClinicalTrials.gov per-study version history.

## Claims not admitted

- No verified original CTTI 2022 flatfile ZIP or SHA-256 until the actual original archive is obtained.
- No assumption that *Zenodo publication time* equals *AACT collection time*, or that a CTTI date-stamped snapshot contains proof of each individual NCT's original-version posting instant.
- No original ClinicalTrials.gov per-study history payload, exact revision-publication timestamp, clinical performance result or NIH submission.
- No new worker in the original twelve-job W13 workstation, and no change to its journals, hosted work page, other third-party research sources, or owner-reserved A/B license.

The higher evidentiary requirement remains [historical-source issue #106](https://github.com/huntingthereferent/autobots-assemble/issues/106).

## Reproduce

```sh
python -m unittest -v network.tests.test_nih_p2_ctti_owner_catalog_2022
python -m systems.workspace.nih_p2_ctti_owner_catalog_2022 --output-dir /tmp/ctti-catalog-receipts
```

The native research execution must preserve a small JSON HTTP evidence receipt and explicitly mark *unverified source bytes and version timing* regardless of outcome.
