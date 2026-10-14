# Stage 28 — Shared fresh route certificate, independent task obligations (October 13, 2026)

**Question.** Can two differently declared route-bound tasks reuse one freshly verified, owner-pinned route certificate, instead of separately repeating its audit, without either task lending its own requirements or evidence to another?

**Executed local result.** Yes, in this bounded owner-backed in-process fixture. A single selected route is checked twice (as in the existing two-pass route proof), and the resulting exact certificate is read-only input to each task's separate obligations. Two different left-route tasks return `TASK_COMPLETED_ON_SELECTED_ROUTE`; together they used **2 underlying left-route replay calls** instead of the **4** incurred by CP-27's independent two-pass per-task audits. Their route certificate is the same freshly obtained object, but their `task_fingerprint` values and obligations differ.

A portfolio containing the two successful left tasks, one successful right task, and one intentionally unproved left task auditted the left route **once** and the right route **once**: 2+2 source-audit replay calls. The task seeking a right-only edge while pinned to the left route stayed `ROUTE_TASK_REQUIREMENTS_UNPROVED`. No route edges, state pairs, or owner observations were added.

## Admissibility and failure boundary

- Reuse is **only within one explicitly invoked portfolio advance**. A new call starts a new audit. No previous invocation's certificate is silently promoted into present proof.
- Tasks share only when they point to the identical in-process route object with the identical declared route fingerprint. Per-task admission, pinned-route structure, comparison binding and task declaration are rechecked; changing an obligation fails closed. Another route's exclusive edge cannot pass the task.
- The selected route is replayed **twice**, checks owner pins and exact source identities through existing integrated adapters, and must produce identical stable certificates with the declared fingerprint; route changes or revoked pins withhold both tasks' success.
- If any source moves across the portfolio invocation, freshness is removed from every dependent task. Unselected tasks remain `CACHED_NOT_REPLAYED`; `verify_for_use(name)` still performs a fresh selected audit rather than borrowing a historical result.
- This is in-process owner-pinned evidence under the existing synthetic owner registry, not externally authenticated identity or an autonomous agent. A SHA-256 archive checksum verifies byte integrity only; it does not authenticate remote owners or prove the entire language referent.

## Reproduction and exact evidence

From the extracted **complete** Stage 28 ZIP package, with Python 3 and stdlib only:

```sh
python run_shared_route_certificate_demo.py
python -m unittest -q test_ab_chatbot_shared_route_certificates.SharedRouteTaskTests
python -m unittest -q test_finite_shared_route_certificate.SharedFiniteTests
python -m unittest -q test_finite_multi_task_dependency.FiniteMultiTaskDependencyTests
```

The combined new-and-finite regression run completed **35/35 targeted tests** (13 new owner-bound integration, 14 new pure finite, 8 CP-27 pure finite regression). The large historical regression invocation stalled; one CP-27 owner-bound suite also timed out, so neither is reported as passing. No full-suite pass is claimed.

`SHARED_ROUTE_CERTIFICATE_RESULTS.json` contains the recorded demo output. `SHARED_ROUTE_CERTIFICATE_REGRESSION.json` gives the exact completed test accounting.

## Package continuity

This ZIP appends eight CP-28 files to the exact verified Stage 27 257-file archive. All 257 pre-existing entry contents remain byte-for-byte unchanged. The complete package contains **265 files**. The standalone reference can also be run from the smaller GitHub checkout without owner-backed Stage 20 integration dependencies, but that independent finite law is not a replacement for the integrated result.

**Next question:** Can an exact freshly revalidated route certificate be safely handed between independent consumer invocations, without importing the previous caller's identity, task obligations, or a stale source status? This would require a separately specified transfer contract; nothing here claims cross-invocation reuse.
