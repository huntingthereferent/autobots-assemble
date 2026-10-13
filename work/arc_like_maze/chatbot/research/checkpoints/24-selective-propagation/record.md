# A/B finite chatbot: selective propagation across independent certificates

**October 13, 2026.** This is an additive orchestration layer on the **same existing** finite A/B chatbot. It does not create autonomy, infer an environment, or replace the mathematical engines. The caller invokes `advance()` when the surrounding sources move. A/B as relational language is not equated with the finite operators A/B in this test.

## Why it was added

The prior `SourceChangePropagation` fully revisits *both* transport routes in a comparison. When several independent comparison records exist, re-auditing all records is unnecessary whenever only one source changes. New `SelectivePropagationPortfolio` uses each record's existing registry-checked owner pins, source/snapshot versions, owner-head metadata, recorded edge-content digests and route-declaration identity to **select the affected comparisons**. It then calls the **unchanged full `SourceChangePropagation.advance()`** only for those records.

**Safety distinction:** A skipped comparison is tagged `CACHED_NOT_REPLAYED` and `proof_fresh=False`; it is **not** certified as current fresh proof, even when its cached historical outcome was `BASELINE_WITNESSED`. When someone needs its evidence for a new task, `verify_for_use(name)` performs the full owner-backed replay first. Hashes and metadata are change-detectors, not source authentication. A source could behave differently without changing these stamps; therefore metadata-based skipping is never proof of its mathematical behavior.

The source scopes and exact declaration references are preserved; a mutable route map/fingerprint or route-object substitution invalidates the stable-cache path and triggers an audit. A stamp change triggers a conservative audit even for a cached edge irrelevant to a particular proof. No new transition is observed merely by monitoring stamps.

## Tested demonstration

Two distinct, already established `TwoRouteComparison` records, each having an independently pinned donor, two intermediate scopes and final scope, are registered as `portfolio_0` and `portfolio_1`.

| Event | Full replays | Skipped as historical cache | Conclusion |
|---|---|---|---|
| No source change | none | `portfolio_0`, `portfolio_1` | Neither is freshly proven by this call |
| Revoke only `portfolio_0` right-middle source pin | `portfolio_0` | `portfolio_1` | First comparison withdrawn; second not falsely reclassified |
| Explicitly request `portfolio_1` for use | `portfolio_1` | N/A | Full audit returns `COMPARISON_PRESERVED` |

All three calls performed **zero new source-transition observations**. The prior evidence belongs to its original pinned source scope; nothing is copied between comparisons. The changed source's prior result remains in the historical propagation ledger.

Extra finite controls include a dependency shared by two comparison records: changing that shared source selects both and leaves an independent record untouched. That is a **pure dependency-graph test**, not remote-source authentication.

## Limits

- This reduces full **comparison-level** replay. It does *not yet* skip just the unaffected left route within one dirty comparison; the legacy comparator deliberately replays both routes when selected. This boundary is explicit.
- No automatic background monitoring or notification. The surrounding system must call `advance()`.
- Stamp checks still inspect every registered scope locally, including its pin validity and edge-cache digest. A skipped proof is historical until full replay.
- A task must call `verify_for_use()` before using a cached witness as fresh mathematical evidence.
- Matching labels or hashes do not authenticate a remote system. Existing in-process owner binding is the only admitted source-bound evidence in this finite harness.
- No unrestricted conjugacy, physical theorem, off-path edge transfer, or universal agent claim.

## Contents and verification

The new archive contains **233 files**: the preceding 225 are byte-for-byte unchanged, with these eight additions: `ab_chatbot_selective_propagation.py`, `test_ab_chatbot_selective_propagation.py`, `finite_selective_dependency.py`, `test_finite_selective_dependency.py`, `run_selective_propagation_demo.py`, this README, `SELECTIVE_PROPAGATION_RESULTS.json`, `SELECTIVE_PROPAGATION_REGRESSION.json`.

Completed local suites:

| Test module | Passing tests |
|---|---:|
| New integrated selective propagation | 9 |
| New independent dependency model | 6 |
| Existing source change propagation + route comparison | 25 |
| Existing two-hop transport | 14 |
| Existing source replacement recovery | 13 |
| Existing cross-scope transport | 22 (includes imported fixture tests) |
| Existing owner pin contract | 10 |
| **Total completed executions** | **99** |

A combined legacy invocation exceeded its execution window; the separately completed two-hop and replacement modules were rerun and counted instead. The entire historical suite was not run, and GitHub CI is not claimed. The cross-scope module includes fixture imports and is counted as *executions*, not unique cases.

Reproduce locally from the unpacked folder:

```bash
python -m unittest -q test_ab_chatbot_selective_propagation.SelectivePortfolioTests
python -m unittest -q test_finite_selective_dependency.DependencyPlanningTests
python run_selective_propagation_demo.py
```

**Next:** Selective replay *inside* a dirty two-route comparison, preserving the clean route's exact certified result as cache-only until requested for use. Prove that changes of common donor/final sources still invalidate both routes. Preserve the unrelated Continuity repo pointer.
