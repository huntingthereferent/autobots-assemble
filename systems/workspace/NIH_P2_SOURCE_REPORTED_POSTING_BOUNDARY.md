# NIH Phase 2 — original version field ↔ official posting-date semantics

## Current referent

Continue the same source-original study `NCT00001756` and verified adjacent version-status difference. This is **not** a larger W13, a WORLD48 conversion, a replacement simulator, a new NIH Phase 2 native job, or an official NIH submission.

The original public ClinicalTrials.gov V259 and V260 pages were independently rendered in real Chromium and returned source-specific:

| Version | History submission day | Overall Status in original version | Version-local Last Update Posted |
| --- | --- | --- | --- |
| V259 | 2022-10-26 | Recruiting | 2022-10-27 [Actual] |
| V260 | 2022-11-04 | Completed | 2022-11-07 [Actual] |

Original successful [native public-browser run #39421372666](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39421372666); [minimal source receipt archive #12264180158](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39421372666/artifacts/12264180158). Archive SHA-256 `45c245cf94200d26b7263d0d03eb86549da8661598627434fadca83e4755e414`. JSON content SHA-256 `9adf3d0419b89a8c098b97b61bbfec874d5833b69bdf0fced213628188ad5540`.

The **byte-exact minimal JSON receipt**, but **no original page bodies**, is checked in at `systems/workspace/fixtures/nih_p2_original_adjacent_source_receipt_39421372666.json`. The separate original source's hashes are retained; hashes are content identifiers, not signatures or an independent timestamping service.

## Distinguish the four clocks

1. **Submission** — the version-history date when a source update was submitted, not when it became public.
2. **Last Update Posted** — the version-local source field reported by the original rendered record, qualified `Actual`.
3. **Observation** — this research's 2026 Chromium retrieval time, not evidence that an older record existed then.
4. **Clinical validity** — when the underlying real-world status applied. Not independently established by the record's publication date.

The [U.S. National Library of Medicine's 2017 Technical Bulletin](https://www.nlm.nih.gov/pubs/techbull/so17/so17_clinicaltrials.html) defines `Last Update Posted` as the date when changed information was made publicly available rather than submitted. The new runner fetches this **official second source** independently and records its exact response SHA-256 and retrieval timestamp.

**The precise wall is narrower, but not closed:** NLM explains the field's meaning, and the original versioned page identifies its own status and posted date. This is strong **source-reported** publication metadata. It does **not** independently prove exact first publication of V259 or V260 using a separately authenticated archived release or contemporaneous timestamp receipt. Neither source proves a clinical event effective date.

## The bounded, conditional A/B comparison

Without modifying or feeding real records to the synthetic-only original W13 executable, check what would follow **if** the source-reported Last Update Posted dates are used as the public-availability cutoffs:

| Cutoff | Source-reported status visible under this assumption |
| --- | --- |
| 2022-10-26 | UNAVAILABLE (no earlier version in this two-version scope) |
| 2022-10-27 | Recruiting (V259) |
| 2022-11-06 | Recruiting (V259) |
| 2022-11-07 | Completed (V260) |
| 2022-11-08 | Completed (V260) |

Those comparisons are **conditional, not a validated historical as-known-at knowledge graph result**. The original source receipt still says first-public `UNAVAILABLE` and `known_at_admitted_to_W13=false`. Even with an exact posted date, this experiment does not establish any `valid_at` for the clinical fact.

Both original source versions remain separately attributed; a later status does not overwrite the historical one. The static union over both versions would leak `Completed` into earlier hypothetical publication cutoffs. The test refuses duplicate, tampered or missing original source receipts, unsupported definitions and fake authoritative claims.

## Next admissible movement

Obtain a second independently authenticated version-level first-public history/release/timestamp relation or an authoritative version-to-published-date identity mapping. Then, and only then, admit a real version-specific `known_at` into a **separate bounded temporal evidence adapter**, compare to an independently computed oracle, and only subsequently test the effect on the W13 investigation. If that original evidence is unavailable, record `UNAVAILABLE` and preserve [issue #106](https://github.com/huntingthereferent/autobots-assemble/issues/106).

The original NIH twelve-job W13 lineage, independent verifier, 48-law ARC mathematics, WORLD Trial 14, and previous native artifacts stay unchanged. Source and solver claims must not be conflated.

## Replay

```sh
python -m unittest -v network.tests.test_nih_p2_source_reported_posting_gate
python -m systems.workspace.nih_p2_source_reported_posting_gate \
  --output /tmp/nih-p2-source-posting-conditional.json
```

The tests use an explicitly synthetic NLM-like snippet for falsification. Only the live GitHub CI fetch of the official NLM document may count as the real independent semantic witness.
