# Stage 27 — Selective propagation across route-bound tasks

**Date:** 2026-10-13. **Status:** Locally executed bounded chatbot experiment.

The previous route-bound-task stage showed that a task can use one exact witnessed transport route without inheriting a neighboring route's failure. Stage 27 registers **several separately declared tasks** against one or more already-witnessed two-route scopes. It builds an exact *in-process* incidence graph from each task's pinned donor, middle, and final scope pairs.

When the caller invokes `MultiRouteTaskDependencies.advance()`, changed owner pins, revisions, selected owner heads, or cached observations are detected via local source fingerprints. Only tasks depending on those changed scope pairs are re-audited. An explicit notification (`changed_sources=(...)`) can force an audit even if the local fingerprint is unchanged; `force_tasks=(...)` targets one named task.

**The graph does not create proof.** It selects which existing `RouteBoundTask.advance()` functions must run. Each selected task replays its own selected route twice and checks its separately declared obligations. A skipped task is **CACHED_NOT_REPLAYED**, not fresh proof. `verify_for_use(name)` always replays the named task. Different tasks never pool edges, paths, destinations, or images into a single proof.

## Live, reproduced example

Three tasks use four source-pair objects: `left_a` and `left_b` share the **left** route, while `right_a` uses the independent **right** route. They share donor and final scopes but have different pinned middle scopes.

| Event | Re-audited tasks | Not replayed | Result |
| --- | --- | --- | --- |
| No change | — | left_a, left_b, right_a | Historical cache only |
| Right middle source pin revoked | right_a | left_a, left_b | Right task withdrawn; left tasks historically preserved |
| Explicit `verify_for_use('left_a')` | left_a | left_b, right_a | Independent left task completes using current owner-backed evidence |
| Shared final scope revision changed | left_a, left_b, right_a | — | All dependent route tasks require re-audit; invalid pinned revision does not retain success |

Every affected task was bound to an already-witnessed route. No newly observed transition was created by the selective orchestration. The demo records per-source observation counts before and after each step.

The tests also cover two independent comparison graphs, multiple source events, a previously witnessed but unproved obligation, declared task mutation to a *different valid requirement*, route-object substitution, old owner revisions surviving a changed live head, altered cached evidence, and a source moving midway through a multi-task audit. A mid-audit source change invalidates freshness for **every task that depends on that source**, including earlier successes from the same batch; those tasks remain dirty for the next invocation.

## Reproduce

From an extracted full ZIP, with Python 3 and no network required:

```sh
python run_multi_task_dependency_demo.py
python -m unittest -q test_ab_chatbot_multi_task_dependency.MultiRouteTaskDependencyTests
python -m unittest -q test_finite_multi_task_dependency.FiniteMultiTaskDependencyTests
```

Existing targeted suites were also rerun independently:

```sh
python -m unittest -q test_ab_chatbot_route_bound_task.RouteBoundTaskTests
python -m unittest -q test_ab_chatbot_route_selective_refresh.RouteSelectiveTests
python -m unittest -q test_ab_chatbot_two_route_comparison.TwoRouteTests
python -m unittest -q test_ab_chatbot_source_change_propagation.ChangePropagationTests
python -m unittest -q test_ab_chatbot_two_hop_transport.TwoHopTransportTests
python -m unittest -q test_ab_chatbot_cross_scope_transport.CrossScopeTransportTests
python -m unittest -q test_ab_chatbot_owner_pin_contract.ExactOwnerTests
python -m unittest -q test_finite_single_route_task.FiniteSingleRouteTests
```

**Completed targeted tests:** 127/127, consisting of 19 new integration tests, 8 new independent finite graph tests, and 100 preceding regression tests. The full historic chatbot suite was not rerun to completion. No new GitHub CI result is asserted.

## Files added to the preceding 249-file ZIP

- `ab_chatbot_multi_task_dependency.py` — owner-bound dependency ledger and proof-for-use boundaries.
- `test_ab_chatbot_multi_task_dependency.py` — 19 live-owner integration tests.
- `finite_multi_task_dependency.py` — independent pure source/task incidence reference (not source authentication).
- `test_finite_multi_task_dependency.py` — 8 independent finite tests.
- `run_multi_task_dependency_demo.py` — executable scenario.
- `MULTI_TASK_DEPENDENCY_RESULTS.json` — exact example output.
- `MULTI_TASK_DEPENDENCY_REGRESSION.json` — completed test suite tally.
- `MULTI_TASK_DEPENDENCY_README.md` — this record.

All original 249 entry contents are preserved byte-for-byte. The new ZIP contains 257 source/data/documentation files. The integrated owner-bound chatbot remains a local ZIP; committing a standalone finite checker does **not** mean the complete archive has been committed to GitHub.

### Scope and next possible movement

This is on-demand source-change propagation, **not** continuous observation, general proof of finite-system equivalence, a new objective-generating agent, or a global result about language. It does not automatically infer which obligations a new task should declare. A possible next step is to share one fresh route audit across multiple tasks attached to that exact route, without allowing one task's obligations or source pins to pass as another's. That optimization is **not** claimed here.
