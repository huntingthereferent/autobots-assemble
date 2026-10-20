# NIH Phase 2 — original clinical-trial version status contrast

**Referent:** historical content availability for the original W13 temporal-evidence investigation. The existing World48 mathematics, WORLD Trial14, NIH source-owned 12-job journal, original temporal Python and separate synthetic test result are not modified.

## Prior source evidence

- [PR #151](https://github.com/huntingthereferent/autobots-assemble/pull/151) proved that official public record-history views V94 and V105 render in actual Chromium.
- [PR #257](https://github.com/huntingthereferent/autobots-assemble/pull/257) actually observed `Overall Status = Recruiting` for both V94 and V105, with original version-local last update posted dates. These unchanged endpoints are **not** a transition.
- The public official [NCT00001756 history table](https://clinicaltrials.gov/study/NCT00001756?tab=history) lists version 260 submitted 2022-11-04 with *Recruitment Status* among the changed sections. This is a source-selected **candidate**, not proof of a changed status value. A section-changed marker does not by itself mean `Overall Status` changed.
- The [ClinicalTrials.gov glossary](https://clinicaltrials.gov/expert-search) distinguishes record submission and posting. It calls Last Update Posted the day when the most recent update was made available; that field does not by itself independently prove each exact historical version's first publication time.

## Next source question and controls

Independently open **predeclared** original V105 (2019-11-22) and V260 (2022-11-04) in a fresh unauthenticated official Chromium session. Admit only an exact `https://clinicaltrials.gov/study/NCT00001756?a=VERSION&tab=history` route with HTTP 200, original study ID/title/index and unique `Viewing VVERSION (DATE)` banner.

Ignore the current study summary and all history-index rows. Inspect only `Study Status` after the banner and between the original `Study Identification` and `Sponsor/Collaborators` headings. Record only selected `Overall Status`, `Last Update Submitted that Met QC Criteria` and `Last Update Posted` with Actual/Estimated precision, URL, retrieved UTC, original source text SHA256 and section SHA256. Do **not** archive the HTML, historical record bodies, sponsor contacts or patient data.

The test must report **actual original statuses** as observed, not projected from the history table's section change label. Both equal and unequal cases are distinct tested outcomes; the live CI succeeds as a source-change witness only if two exact versions render and `Overall Status` really differs. If not, preserve `NO_OBSERVED_CHANGE` or `UNAVAILABLE` rather than inventing a changed status.

A source-labelled version-local `Last Update Posted` date is recorded verbatim, but **version-first-public `known_at` is not admitted** without separate verification of version-level publication identity and clock correspondence. No answer is computed by W13's temporal prototype from invented timestamps. The historical source gap stays [#106](https://github.com/huntingthereferent/autobots-assemble/issues/106).

## Test

```sh
python -m unittest -v network.tests.test_nih_p2_original_version_status_contrast
python -m systems.workspace.nih_p2_original_version_status_contrast --out-dir /tmp/nih-p2-actual-status-contrast
```

The official original-source browser and all falsification tests run on GitHub Actions, and the workflow retains only a minimal source receipt and its digest. A successful result is a **bounded original status-value contrast** in the publicly rendered historical record; it is not a general temporal KG benchmark, physical construction, any causal clinical claim, or NIH Phase 2 award/submission.
