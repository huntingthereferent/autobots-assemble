# NIH P2 — original ClinicalTrials.gov public version viewer access

**Experiment type: original public source browser, not a claimed historical-content oracle.**

The original [historical source issue #106](https://github.com/huntingthereferent/autobots-assemble/issues/106) requires exact original per-study version content and independently grounded **posting/availability time**. The public ClinicalTrials.gov study page supports a **Record History** table and viewing individual versions. NLM's [2024 modernization report](https://www.nlm.nih.gov/od/bor/NLM_BOR_CTG_WG_Modernization_Update_Report_20241031_508.pdf) documents the original interface and its comparison tool. The table's **Date submitted** is not a public posted-at witness.

Earlier [draft PR #107](https://github.com/huntingthereferent/autobots-assemble/pull/107) attempted the site's **undocumented site-internal JSON history endpoint** and independently observed HTTP **403** from GitHub CI. This experiment **does not retry or bypass that route**.

## Bounded original browser source

The frozen target, `NCT00001756`, is selected through the independently authenticated historical status-field comparison in [merged PR #141](https://github.com/huntingthereferent/autobots-assemble/pull/141). Its 2022 source-dated file and other original file have different recorded recruitment statuses; those differences are not asserted to be version-level change-time witnesses.

The program independently navigates exactly two directly published public UI URLs:

- [Original official history page, version 94](https://clinicaltrials.gov/study/NCT00001756?a=94&tab=history)
- [Original official history page, version 105](https://clinicaltrials.gov/study/NCT00001756?a=105&tab=history)

The selected version numbers are observed in search-indexed original ClinicalTrials.gov Record History records; the native Chromium execution, **not a snippet**, determines whether those actual views are accessible from an unauthenticated GitHub runner. No cookie injection, access controls workaround, undocumented API or credentials are used.

The runner records actual HTTP status, retrieval UTC, original host, exact selected URL, limited page title, and a SHA-256 of the browser-visible text. A page counts as **explicitly rendered as requested historical version** only if the official site's public content contains the exact `Viewing V94` or `Viewing V105` banner **alongside the original exact study ID, title, real version index, and Study Details section**. A URL query parameter, current version summary, an index table's other version numbers, a search result snippet or a cross-host redirected page **cannot satisfy this gate**.

**CI admission boundary:** The independent browser workflow requires **both exact original viewer routes** and explicitly rendered V94/V105 banners. Wrong-path or duplicate query parameters and false prefix banners such as `Viewing V940` are rejected. A failed source request now fails the check (the minimal blocked-access receipt is still retained); a green check cannot mean `0/2` or `1/2` original versions were witnessed. This is strictly a page-presentation test, not authentication of historical status content or public posting dates.

## What is not claimed even if a browser page renders

- The raw source text/HTML is **not redistributed**, because historical study pages may include sponsor contacts or other irrelevant person details.
- Seeing a version banner verifies a **public version-view presentation**, not the correct underlying contents of `overallStatus`. The program does not yet extract or validate a structured status field from the version's exact original content and marks historical field contents **unverified**.
- The Record History table's **submission date** is not an independently verified first-public **posting date** of each version.
- `Last Update Posted` displayed at the top of the *current study summary* must not be silently copied to historical version metadata.
- Clinical outcomes, biological causality, user or patient-level records, a native W13 job, or an NIH submission are not demonstrated.

The next evidence layer, conditional on actual successful original viewer access, is to identify and independently verify a **specific historical version's own status content** from the version-specific rendered area, then independently obtain the corresponding **original-version public posting timestamp**, without inferring either from current records or another snapshot's label. If the public page is unavailable, the experiment produces the blocked access receipt and preserves the source issue as open.

## Reproduction

```sh
python -m pip install 'playwright>=1.54,<2'
python -m playwright install --with-deps chromium
python -m unittest -v network.tests.test_nih_p2_official_history_browser_access
python -m systems.workspace.nih_p2_official_history_browser_access \
  --output-dir /tmp/nih-p2-real-history-browser
```

The original twelve source-owned W13 jobs, its native Chromium game, Phase 1 draft and A/B intellectual property terms are unchanged.
