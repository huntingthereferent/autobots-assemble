# A/B chatbot — source-change propagation (2026-10-13)

## Current referent

This increment does **not** introduce a self-directed agent or another mathematical solver. It lets the existing pinned-owner A/B-labeled **finite** chatbot be invoked after its environment changes, follow the effects through its already-declared route dependencies, and separately report what can still be witnessed.

The four named scope pairs are **donor**, **left middle**, **right middle**, and **final**. Each is backed by its own locally owned finite original/changed snapshots. Both existing routes still use independent selected-edge commuting squares; the two-route comparison is valid only if **both** routes pass live owner-pin checks and retained-edge replays.

## New opt-in code

- `ab_chatbot_source_change_propagation.py`: `SourceChangePropagation(TwoRouteComparison)`; `advance()` performs on-demand audit, preserves immutable historical comparison reports, fingerprints the *currently cached* evidence for change detection (not as authentication), and reports which scopes changed and which routes depend on them. It never declares a new state map, owner pin, mathematical edge, or global equivalence.
- `test_ab_chatbot_source_change_propagation.py`: 13 integration tests with live in-process pinned HTTP source owners.
- `finite_source_change_propagation.py`: independent complete-law reference for comparing declared prior/current finite scopes, with **no** source authentication or monitoring claim.
- `test_finite_source_change_propagation.py`: six pure finite regression controls.
- `run_source_change_propagation_demo.py`: four reproducible live-owner-backed cases, exported in `SOURCE_CHANGE_PROPAGATION_RESULTS.json`.

No predecessor module was edited.

## Executed source movement

The starting fixture carries two separately witnessed transport routes whose **composed endpoint mappings disagree**. The incompatibility is a genuine route-independent mapping obstruction, not an invalidity of either route's finite observations.

| Subsequent event | Left route | Right route | Live comparison | Added edges at refresh |
|---|---|---|---|---:|
| No source change | preserved | preserved | `ROUTE_COMPOSED_MAP_CONFLICT` still witnessed | 0 |
| Right-middle new-source pin explicitly revoked | preserved | withdrawn | `ROUTE_EVIDENCE_UNPROVED` | 0 |
| Common final-source pin revoked | withdrawn | withdrawn | `ROUTE_EVIDENCE_UNPROVED` | 0 |
| Right-middle owner publishes a new current revision; old pinned views untouched | preserved | preserved | prior selected-edge conflict preserved by historical replay | 0 |

Additional focused controls: an altered **used** right-middle B transition is rejected without withdrawing the left route; a changed right-middle pinned revision or replaced snapshot is not silently re-pinned; a new legitimate but **unused** edge observation does not invalidate the already witnessed partial correspondence. A donor-source revocation withdraws both routes. A comparison scope swap is rejected.

**Critical temporal distinction:** An owner's **head revision** can advance while existing owner-held immutable historical snapshots remain verifiable. That event is reported as `SOURCE_HEAD_ADVANCED`, but it does not establish or remove a mathematical fact about the historical pinned revisions. If the active pinned snapshot/owner/edge evidence fails, affected chain certificates are withdrawn. A fresh version requires a new, separately witnessed comparison and cannot inherit the old result. The original comparison remains in the in-memory historical report and is never displayed as a currently valid conclusion after withdrawal.

The effect graph here is not discovered: donor and final affect both routes; either middle affects only its own route. `affected_routes` reports which route *depends on the changed scope*, not that the route became invalid. Validity comes exclusively from the replayed route certificate.

## Tests

**101 passing targeted tests in nine separately completed suites**, without counting an earlier interrupted group:

| Suite | Tests completed and passing |
|---|---:|
| New live source-change integration | 13 |
| New independent finite reference | 6 |
| Predecessor two-route comparison | 12 |
| Two-hop transport | 14 |
| Cross-scope transport | 12 |
| Cross-pin join | 10 |
| Exact owner pin contract | 10 |
| Joint evidence task | 11 |
| Earlier same-pin explicit transfer | 13 |

A first run of new tests exposed an incorrect `PinnedView` attribute (`version`, not `revision`), which was fixed. A second negative control incorrectly altered an **unwitnessed** edge and was corrected to alter the actual used transition. **Only subsequent successfully completed tests are counted.** Full historical regression and remote GitHub CI were not performed.

Reproduction, after unpacking into one directory:

```bash
python -m unittest -q test_ab_chatbot_source_change_propagation.ChangePropagationTests
python -m unittest -q test_finite_source_change_propagation.FiniteSourceChangeTests
python run_source_change_propagation_demo.py
```

## Identity, observation and mathematical boundaries

A `ScopeStamp` captures in-process snapshot identity, pinned source version, currently owned head version, exact registry pin validity, observed transition count, and a digest of currently cached transitions. **Those digests are change indicators, not source authentication credentials.** Pin validity continues to come from the original registry and loopback owner binding; mathematical completion still comes from the original audited two-hop route certificates and the four-scope comparison. A change notification or source label alone never grants validity.

`advance()` is an explicit on-demand method, **not a background watcher** or an autonomously generated task. Owner head inspection is same-process and does not request new HTTP transitions. Historical evidence remains alongside live audit results. There is no unobserved-edge promotion, no general intertwinement claim, no unrestricted cross-source equivalence, and no physical A/B theorem. The named A and B finite actions are only a bounded mathematical experiment; they do not define A/B as James's relational language.

## Handoff

Archive: `ab_chatbot_source_change_propagation_2026-10-13.zip` includes all **209** predecessor files byte-for-byte and **eight** additions. GitHub is unchanged in this increment; no repository-write authorization was supplied for a fresh addition in the current authorship context. The unrelated current Continuity project pointer `state/current.json` is untouched.

**Next possible movement:** support a *new, explicitly pinned* replacement middle source as a separate route object, and compare its newly witnessed certificate against the retained historical one. Do not relabel the old certificate as valid for the new pin.
