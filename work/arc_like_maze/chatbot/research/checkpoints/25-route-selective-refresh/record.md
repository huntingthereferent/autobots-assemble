# finite A/B correspondence process — selective replay inside a two-route comparison

**October 13, 2026. Additive opt-in implementation.** The language-level A/B research referent is not defined by these explicitly specified finite action generators.

## What changed

`ab_chatbot_route_selective_refresh.RouteSelectiveRefresh` wraps the existing `SourceChangePropagation` and `TwoRouteComparison`. The earlier source files, join rules, pinned-owner scheme, selected commuting-square certificates, and original route histories remain **unchanged**.

On a caller-invoked `advance()`, a source stamp change selects **only its dependent route** for fresh `TwoHopTransport.advance()` checks:

- Donor/final scope: both routes, because they share these source scopes.
- Left middle: left route only.
- Right middle: right route only.
- Declaration/scope-object change: conservatively reject the comparison and designate both routes affected.
- No changes: no route transitions replayed; both results are explicitly `CACHED_NOT_REPLAYED`.

The selected route is audited twice for a stable owner-backed result, including exact fingerprint and pin/source replay through the preexisting `TwoHopTransport`. Pin/source stamps are checked before and after. The unselected route retains its historical certificate **without being represented as freshly verified**.

**Critically:** `advance()` is *not* permitted to declare a usable combined mathematical comparison. Even if one route re-verifies, the comparison status is `COMPARISON_REQUIRES_FULL_AUDIT`, because the other side is cached. `verify_for_use()` invokes the original `TwoRouteComparison.advance()`, which replays **both** routes and verifies their common selected donor edge, composed endpoint maps, evidence versions, pins, and repeat-audit stability. Only then can `COMPARISON_FULLY_WITNESSED` be returned with a `current_comparison`.

This is *on-demand* propagation: the environment changes, the caller invokes the agent, and the agent checks the relationships affected. There is no autonomous polling, independent goal setting, or speculative addition of unobserved edges.

## Executed finite results

| Case | Routes re-audited | Report | Extra owner observations |
|---|---|---|---:|
| Stable comparison, no source movement | Neither | `COMPARISON_CACHED_NOT_REPLAYED` | 0 |
| Right middle-source pin revoked | Right only | `COMPARISON_WITHDRAWN`; left historical | 0 |
| Full-use request after right withdrawal | Both | `COMPARISON_WITHDRAWN` | 0 |
| Shared final owner pin revoked | Both | `COMPARISON_WITHDRAWN` | 0 |
| Middle owner publishes new head, pinned historical view stays intact | Right only | `COMPARISON_REQUIRES_FULL_AUDIT` | 0 |
| Full-use request for that historical view | Both | `COMPARISON_FULLY_WITNESSED` | 0 |

These statuses were exercised by the runnable local owner-pinned demo: `python run_route_selective_refresh_demo.py`. Raw records are in `ROUTE_SELECTIVE_REFRESH_RESULTS.json`.

A deliberately corrupted *used* edge withdraws its dependent route; an altered but *unconsumed* cached edge may trigger conservative selective replay without automatically falsifying the route. Mapping or object substitutions are not silently accepted as new provenance. Historical comparison results stay attributed to their original immutable pinned source objects.

## Verification

**106 passing test cases in completed runs:**

| Completed suite | Tests |
|---|---:|
| `test_ab_chatbot_route_selective_refresh.RouteSelectiveTests` (new) | 14 |
| `test_finite_route_refresh_dependency.SelectiveFiniteTests` (new) | 8 |
| Prior selective portfolio | 9 |
| Prior source-change propagation | 13 |
| Prior two-route comparison | 12 |
| Prior source-replacement recovery | 13 |
| Prior two-hop transport | 14 |
| Prior cross-scope transport | 12 |
| Prior joint evidence task | 11 |
| **Total** | **106** |

An attempted combined regression command timed out; it is **not** included. One outdated test-class invocation selected no valid suite, and is not included. Full historical suite and GitHub CI not claimed.

## Complete package and boundaries

The new archive `ab_chatbot_route_selective_refresh_2026-10-13.zip` retains every one of the prior 233 files of `ab_chatbot_selective_propagation_2026-10-13.zip` byte-for-byte. Eight new files: integrated selector, 14 tests, independent finite dependency reference, 8 tests, demo, README, result JSON and regression record.

The pure finite dependency reference **does not verify owner identity, rule evidence, or live source transport**; it only selects which paths should be re-audited. The integrated adapter must still use the existing live pinned-owner and transition replays. Its quick stamp checks are change hints, **not proof**. The source/record identities are in-process handles, not remote authentication.

No existing source files were modified. GitHub was **not updated** in this increment. No arbitrary physical systems, universal A/B claim, or full-law conjugacy follows.

**Next mathematical movement:** Introduce a read-only task consumer for the *route-selective status* so that a task can depend on a chosen individual route without unnecessarily requiring the other route, while every such task still replays the specific route's complete owner-backed evidence before acceptance. A task that needs the route-independent comparison must still require both.
