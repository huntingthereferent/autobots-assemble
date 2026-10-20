# NIH Phase 2 — two original source clocks, independent archive status check

**Question:** Can W13's existing source-observation approach accommodate genuine historical registry source movements without silently converting posting metadata into real clinical validity times?

**This is one bounded read-only source adapter, not another world.** It does not invoke or rewrite the original synthetic-only W13 emitted temporal Python, W13's original twelve-job journal, World48 laws or the active mathematical WORLD.

## Exact retained original sources

Use the **actual retained GitHub Actions source evidence artifacts**, downloaded by pinned run ID and artifact name from the same original repository. Before admitting either JSON, reject byte changes using the independently recorded original content SHA-256:

| Actual original source receipt | Run | Artifact | JSON SHA-256 |
| --- | ---: | ---: | --- |
| ClinicalTrials.gov historical V259/V260 original Chromium | [#39421372666](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39421372666) | 12264180158 | `9adf3d0419b89a8c098b97b61bbfec874d5833b69bdf0fced213628188ad5540` |
| Independently verified two-full-source AACT archive crosscheck | [#39424382213](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39424382213) | 12265565989 | `549d7cc2343c49818f54eeba8ce5c4ee3a8b44f84cf796d6361702d2e6c81e2e` |

The original ZIP digests and whole-archive deposited MD5/SHA-256 remain recorded in each original artifact. The adapter reads **only the two minimal receipt JSONs**, not 525MB clinical datasets or historical public web page bodies.

GitHub artifact retention was 30 days. If these exact source artifacts have expired, CI must report **source UNAVAILABLE** and require renewed original-source authentication, never fabricate replacement bytes.

## Two observed source-clock families

**Original public registry record history (two adjacent versions):** `NCT00001756` V259 contains `Overall Status = Recruiting`, source-reported `Last Update Posted = 2022-10-27 [Actual]`. V260 contains `Completed`, source-reported `Last Update Posted = 2022-11-07 [Actual]`. Their real independent Chromium retrieval timestamps are in **2026**. The NLM describes Last Update Posted as the date updated study information was publicly available.

**Independent owner-deposited AACT observations:** one original source owner attests a **November 4, 2022 collection** yielding `Recruiting`; another original source owner attests **November 9, 2022 collection** yielding `Completed`. Each independently authenticated entire archive also records matching `last_update_posted_date` values. These are **source-owner claims about historical collection days**, not independently witnessed 2022 network captures. The later Zenodo deposit dates are distinct from owner-reported original extraction dates.

In either source family, **actual clinical valid-at** remains `UNAVAILABLE`. An original registry version's **independently witnessed first-public availability timestamp** remains `UNAVAILABLE`. Do not conflate source posting, claimed archive collection, present-day retrieval, actual effective clinical time and exact first publication.

## Reproducible bounded comparison

The adapter runs six **conditional** source-reported cutoff queries over the two original registry versions. An unavailable earlier version is unknown, not evidence that a trial did not exist.

The separate source-family oracle takes original statuses directly from the two whole-byte-verified AACT archive rows, *not* from the registry cutoff-projection function; the owner-attested Nov 4 and Nov 9 collection claims are comparison anchors. It checks whether the source-reported conditional registry status agrees with each separately deposited original row. A mismatch must be reported as a mismatch, not repaired or renamed. The static-union baseline always holds both record values, which would leak the newer `Completed` field before its *source-reported* posted date.

The adapter asserts that this **does not** prove a real temporal-KG benchmark, authenticated actual `known_at` for first public version release, a medical event, NIH award, or NIH Phase 2 completion.

## Test

```sh
# GitHub Actions downloads and SHA256-verifies both original retained artifacts:
python -m unittest -v network.tests.test_nih_p2_two_original_source_clocks

python -m systems.workspace.nih_p2_two_original_source_clocks \
  --registry-source /exact/original-status-contrast.json \
  --aact-source /exact/independent-aact-original-version-corroboration.json \
  --output /tmp/nih-p2-source-clocks.json
```

Source receipt hashes, actual version/status values and two external archive identities must all match. Eight focused negative controls cover altered source, wrong identity/time, original-source clock leakage, unknown validity and prohibited W13 promotion. CI writes a small derived source receipt with no redistributed third-party full archive.

## Next legitimate movement

Resolve the remaining [historical first-publication authentication issue #106](https://github.com/huntingthereferent/autobots-assemble/issues/106), or explicitly leave the timestamp unsupported. Then compare the original source-observation adapter's outputs to independently witnessed original version/publication events before attempting an actual real-source historical `known_at` query in an explicitly permissioned W13 extension. The existing W13 original synthetic program remains unchanged, as does the license.
