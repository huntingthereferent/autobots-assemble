# WORLD / NIH P2 — source-owner posting-day cross-witness (October 19, 2026)

**Source boundary advanced:** from two original version-specific recruitment status fields plus *submission* days, to **two source-owner-reported Last Update Posted days within the selected original version Study Details**. Independent first-public-access transaction instants remain **NOT AUTHENTICATED**.

## Actual witnessed native continuation

[WORLD replay and independent cross-witness run #39215551336](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39215551336) — SUCCESS  
[Source evidence artifact #12169297326](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39215551336/artifacts/12169297326) — ZIP SHA-256 `818c4f36a4af71b25bc103f49f3596f38abb215fca4c38c1bcf93829ecbf8639`.

The fresh runner replayed the **original 12/12 W13 NIH native jobs** from the pinned retained owner journal, ran the original four game actions, and reverified the synthetic source revisions separately. **Zero new native jobs, original runtime/coordinator journals unchanged**.

- 8 original NIH P2 controls passed
- 22 WORLD source/event/historical field/posting-day cross-check controls passed
- 5 original third-party source-depositor reference checks passed
- Total: **35 focused negative-control tests passing**

## Official source owner, exact original versions

Study: [NCT00001756](https://clinicaltrials.gov/study/NCT00001756?tab=history) — *Study of Mast Cell Precursors*.

| Historical version | Original selected version source | Source's Date Submitted | Version-specific Study Details: **Last Update Posted** | Historical Recruitment/Overall Status |
| --- | --- | --- | --- | --- |
| V94 | [Official original V94 viewer](https://clinicaltrials.gov/study/NCT00001756?a=94&tab=history) | `2019-08-01` | **`2019-08-02`** | `RECRUITING` |
| V105 | [Official original V105 viewer](https://clinicaltrials.gov/study/NCT00001756?a=105&tab=history) | `2019-11-22` | **`2019-11-25`** | `RECRUITING` |

The two original selected-history pages were loaded in real headless Chromium without credentials, requiring the exact source URL and `Viewing V94 (2019-08-01)` / `Viewing V105 (2019-11-22)` banners. The source's **current record header** occurs before the original version banner and was independently separated and excluded as a candidate per-version post date. Both owner-labelled `Last Update Posted` fields were located **after the actual selected version's Study Details**.

An independent join checked (a) source-probe date field position and value, (b) separate original version-specific recruitment-status text, and (c) the **same independently witnessed original browser page text digest** in *both* source observations:

- V94 page SHA-256: `4370ff462cd731f2f42cc866aadb438e4d037c7a05de2cd64fb5acb53500c3ba`
- V105 page SHA-256: `4daab6b95ea574a0aeaea3fba36a94fd9db8df8f0dafd41eee5b87bd9a6bd9db`

The exact page digests also match prior successful source-access observations [PR #151](https://github.com/huntingthereferent/autobots-assemble/pull/151), and the status receipts from [WORLD run #39213264527](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39213264527).

### Decision boundary

**Supported:** original authoritative ClinicalTrials.gov viewer **reports** selected historical V94/V105 Last Update Posted days, and two independent live reads of the source page agree byte-for-byte on browser-visible text; the selected old recruitment status was RECRUITING on both pages.

**Not supported:** an independently witnessed original public posting *transaction*, exact UTC time or timezone within either reported day, original per-version first availability instant as measured at publication, complete audit of unobserved intermediate revisions, or clinical outcome truth. Do not silently convert owner-reported calendar days into UTC midnight or assign an exact `known_at` instant. The source owner uses `Last Update Posted` for the date changes became available, distinct from `Last Update Submitted`; only the source-reported **day** has been observed, not a contemporaneous external capture of the 2019 event.

**Research next move:** build a **day-granularity time query** with an explicit source-owner-posted-day uncertainty interval and independent oracle, rather than pretending an exact publication instant exists. Keep the former unknown exact time marked unknown; do not infer absent intermediate records from equal statuses at V94 and V105. The existing 2026 fictional game correction/withdrawal examples remain intentionally unjoined to actual NCT version history.

**Preserved:** WORLD two-room `game-w13-multiworld-v1` contract unchanged; original twelve-job native source/journals immutable; original source depositor's November 4, 2022 AACT claim remains separate; NIH Phase 1 draft not submitted.

## Reproduce

```sh
python -m unittest -v network.tests.test_nih_p2_world_version_posting_probe network.tests.test_nih_p2_world_posted_day_cross_witness
python -m scripts.nih_p2_world_version_posting_probe --output-dir /path/to/observations
python -m scripts.nih_p2_world_posted_day_cross_witness --evidence-dir /path/to/observations
```

The second command requires both independent historical field and posting-label receipts; mock unit tests cannot substitute for live official Chromium source evidence.
