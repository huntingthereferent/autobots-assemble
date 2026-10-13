# A/B chatbot — exact route-bound task consumption (2026-10-13)

**Current research referent.** Continue the existing finite mathematical A/B chatbot while respecting the observation that useful movement can come from its surroundings, not from autonomous goals. This experiment adds **one explicitly declared task bound to one named, already observed two-hop route** within a historical two-route comparison. A/B as relational language is not defined by these finite mathematical generators.

## What has been independently witnessed

The previous two-route fixture uses the same pinned donor and final sources, but independently pinned left/right middle sources. Both original chains have **six state pairs and five admitted labeled transitions**. Their composed donor-to-final maps can disagree; this is a route-independent mapping conflict, not evidence that either individual chain is false.

The new `RouteBoundTask` requires a strict declaration:

```python
{
  'route': 'left',
  'route_fingerprint': '<64-hex fingerprint of previously witnessed left chain>',
  'required_edges': [
     {'state':[1,0,0], 'action':'B'},
     {'state':[1,1,2], 'action':'A'}
  ]
}
```

It also accepts bounded `goals`, `required_paths` with exact old/new endpoints, and `required_destinations`, reusing the existing strict `JointEvidenceTask` parser. It independently replays **only the named route** twice, with the same pinned owner/revision/transition checks already performed by `TwoHopTransport`. It verifies that the named route object, initial pinned scope objects, mapping declarations and exact route fingerprint remain unchanged. It checks every task obligation exclusively against that route's *admitted* states and edges. It does not invoke the other route, change either historical join, or create novel owner transitions. A hash identifies the route plus normalized task constraints, but is not source authentication.

| Experimental input | Bounded result |
|---|---|
| Right middle owner pin revoked; task uses two edges of unaffected left route | `TASK_COMPLETED_ON_SELECTED_ROUTE`, 2/2 edges admitted |
| Compare both routes after right pin revoked | `COMPARISON_WITHDRAWN`, correctly |
| Left task requests edge `(0,1,2) B`, available only on right route | `ROUTE_TASK_REQUIREMENTS_UNPROVED` |
| Task requires both routes' exclusive edges | Unproved on **each** route; no evidence merge |
| Only left route owner pin subsequently revoked | `OWNER_PIN_UNPROVED`, previous task success withheld |
| Selected route mapping replaced | `ROUTE_DECLARATION_CHANGED` |
| Selected source changes between replay passes | `SOURCE_MOVED_DURING_AUDIT` |

The local owner-edge observations remain exactly the same before and after task consumption: donor 3+3, selected middle 5+5, final 6+6. No task observations are added. The historical two-route result is preserved as a historical record, never promoted to a freshly verified comparison.

## Tests and reproducibility

**100 tests passed across completed suite runs**: 18 new in-process integration tests, 7 new independent finite-law tests; 14 previous route-refresh, 12 previous two-route comparison, 13 source-change propagation, 14 two-hop transport, 10 exact owner pin and 12 cross-scope transport regression tests. A separate earlier combined invocation stalled in the old joint-task suite; that incomplete execution is **excluded**. One initial misnamed test class ran no tests and was replaced with the correctly named completed run. Full historical regression suite and GitHub CI are **not** claimed.

Reproduce from the extracted ZIP directory:

```bash
python -m unittest -q test_ab_chatbot_route_bound_task.RouteBoundTaskTests
python -m unittest -q test_finite_single_route_task.FiniteSingleRouteTests
python run_route_bound_task_demo.py
```

The separate `finite_single_route_task.py` knows the complete declared finite laws and intentionally **does not authenticate an external owner or prove in-process source identity**. Only the integrated adapter uses existing in-process, owner-pinned observation replay.

## Boundaries

- The chatbot continues when **invoked**; it does not poll autonomously.
- A route-specific task can succeed even if the unrelated route is withdrawn, but it **does not establish agreement between routes**.
- No unobserved edge can satisfy a task. No task may assemble independently available obligations from different routes unless a new separate witness legitimately joins them.
- An exact source pin, version, mapping and cached observation used by the route remains subject to the old verifier's audits and failure walls.
- `ROUTE_TASK_REQUIREMENTS_UNPROVED` is a bounded evidentiary limit, not a theorem that the missing mathematical edge cannot exist.
- GitHub is **unchanged** for this local increment. `state/current.json` is untouched.

**Next movement:** Allow a portfolio of route-bound tasks to respond selectively to external changes, using route-level dependency indexing while requiring current proof before any task result is published. No autonomous objective is required.
