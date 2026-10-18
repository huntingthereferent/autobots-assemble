# Original depositor's directly linked AACT download-date statement

**Evidence class: source-owner attestation, not independent historical capture.**

## The correction

The [two whole-source AACT studies files](NIH_P2_STATUS_DIFFERENCE_SEARCH.md) have verified byte identities and **1,345 differences among 432,597 shared study IDs**. The Zenodo item containing Lalagkas's studies file was **published October 31, 2023**, but that publication date is not the date of AACT extraction.

The original depositor's public source code now establishes a much stronger *author-attributed source link*:

- [Panagiotis N. Lalagkas's original `drugs_investigated_indicated_diseases.R`, commit `96ccb82`](https://github.com/lalagkaspn/mendelian_comorbidity_therapeutics/blob/96ccb828b5118e54c658fc1cd386173de67a4b4/drugs_investigated_indicated_diseases.R), recorded October 31, 2023, explicitly states `## data of download: November 4, 2022`, and reads the **local** `raw_data/AACT_studies.txt`.
- [The same author's script at commit `675b7a4`](https://github.com/lalagkaspn/mendelian_comorbidity_therapeutics/blob/675b7a4992d7e2469d368924f4c1f87d7ca162da/drugs_investigated_indicated_diseases.R), also recorded October 31, 2023, retains **the identical date statement** and changes the following source call to **`ct = fread("https://zenodo.org/records/10058991/files/AACT_studies.txt?download=1")`**.
- The Zenodo file at that **exact URL** was previously independently verified as original archive bytes, whole-file SHA-256 `bed698312a04292fc31f7ea71130731acc9b57723399ab1b45c0f6d70a304d49` and published MD5 `d043fb7704bcff8cfb5be95d4f5ced85`.
- Independently, Axfors/Nilsonne [stated November 9, 2022 for their AACT source](https://zenodo.org/records/10091147), with a separate authenticated whole archive SHA-256 `d1d4fb04a121e03f2ac08bacef708a896f7240d5ff025104ed7512b60408d755`.

These are **the original source owners' stated underlying collection dates**: November 4 and November 9, **both in 2022**. The original code's URL makes the linkage specific to the same deposited Lalagkas file, not just a coincidence of 432,597 studies or proximity of Git and Zenodo dates.

## Independent evidence admission

[`nih_p2_aact_owner_date_link.py`](nih_p2_aact_owner_date_link.py) fetches **both original Git files at pre-pinned commit SHAs**, verifies their full raw contents using the **real Git blob SHA-1**, checks that the date assertion occurs directly beside the AACT source reference and either the original local path or **exact deposited Zenodo URL**, then writes a small JSON source-owner receipt. The dedicated GitHub CI independently downloads both source files and tests falsifications of wrong dates, wrong URL, changed blob identity and detached source claims.

Original third-party scripts themselves are **not copied into this repo**; they are inspected read-only and referred to by immutable original-source URLs.

### Preserve these distinctions

| Observation | Status |
| --- | --- |
| Original author declares **Nov 4, 2022** as AACT download date for the Zenodo-linked file | **Source-owner attested, directly linked** |
| The second depositor declares **Nov 9, 2022** as its AACT collection date | **Source-owner attested, separately verified archive** |
| Source owners' *stated* collection dates order the two archives Nov 4 → Nov 9 | **Supported as attributed claims** |
| The actual Nov 4 download transaction witnessed contemporaneously by an independent observer | **Not established** |
| Original author script contains a cryptographic SHA-256 linking the Nov 4 date to the exact archive bytes | **Not established** |
| The date on which any individual original clinical registry version first became public | **Not established** |
| The date of any clinical event or patient outcome | **Not established** |

The 1,345 differences now have a plausible **owner-attested earlier → later collection direction**, but the precise external underlying source timestamps remain **not independently authenticated**. For scientific reporting, do not transform owner attribution into an independent registry snapshot capture, or label differing values as authenticated clinical events. Even independently dated endpoint snapshots cannot exclude unseen intervening revisions.

The remaining [historical-version issue #106](https://github.com/huntingthereferent/autobots-assemble/issues/106) concerns **original per-study version payloads plus source-authenticated first-publication times**, separate from these two snapshot owner statements. Nothing here modifies the original twelve-job W13 workstation, its native journal, its game, its A/B license, or the unsubmitted NIH Phase 1 draft.

## Reproduce

```sh
python -m unittest -v network.tests.test_nih_p2_aact_owner_date_link
python -m systems.workspace.nih_p2_aact_owner_date_link --output-dir /tmp/nih-p2-owner-date
```

The live test requires network access to the original public Git repository; no private GitHub access, third-party library copies, or 500 MB clinical downloads are required to verify the **additional** author-provenance link.
