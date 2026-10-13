# Finite chatbot — continuation and provenance (October 13, 2026)

This is a trace of the finite mathematical chatbot's **stages 20–26**, following the [research index](README.md). The declared A/B-labeled finite generators are experiment-specific operators; they do not define the language referent. These records preserve what was observed and how to revisit it. The source systems and their environment do not need to initiate autonomous goals for relations to be checked on the next invocation.

## Witness sequence

| Stage | What changed and what survived | Locally recorded result | Integrated archive |
| --- | --- | --- | --- |
| **20 · Two-hop selected-edge transport** | Two independently witnessed selected squares connect three owner-pinned pairs. Original joins remain untouched. | 6 paired states; 5 admitted edges; 2/2 required task edges; 76 completed targeted test executions. [GitHub finite source](finite_two_hop_transport.py), [tests](test_finite_two_hop_transport.py), [scoped record](TWO_HOP_TRANSPORT_2026-10-13.md). | `ab_chatbot_two_hop_transport_2026-10-13.zip` · 201 files |
| **21 · Two-route comparison** | Two valid two-hop routes share donor/final owner scopes but use different pinned middle scopes. Four old/new endpoint assignments disagree; neither route certificate is erased. | `ROUTE_COMPOSED_MAP_CONFLICT`; agreement control also tested; **113** completed tests. | `ab_chatbot_two_route_comparison_2026-10-13.zip` · 209 files |
| **22 · Source-change propagation** | On-demand owner-pin and evidence re-audit distinguishes withdrawn routes from preserved historical witnesses. A new owner head does not erase an unchanged pinned old snapshot. | One right-middle change withdraws the right route, not the left; **101** completed tests. | `ab_chatbot_source_change_propagation_2026-10-13.zip` · 217 files |
| **23 · Source-replacement recovery** | A new independent owner/snapshot/pin establishes replacement evidence; the old comparison stays historical. A replacement may agree or conflict. | `RECOVERY_AGREEMENT_WITNESSED` and `RECOVERY_CONFLICT_WITNESSED` demonstrated; **92** completed tests. | `ab_chatbot_source_replacement_recovery_2026-10-13.zip` · 225 files |
| **24 · Selective propagation across comparisons** | Changes select dependent comparison records; unrelated records are explicitly cached, never silently promoted as freshly verified. | One affected record replayed, one unrelated record skipped; **99** completed test executions. | `ab_chatbot_selective_propagation_2026-10-13.zip` · 233 files |
| **25 · Selective refresh inside a comparison** | Replays only the affected route for a local update. A task needing the combined route-independent comparison still replays both. | One of two routes selectively refreshed; zero new transition observations; **106** completed tests. | `ab_chatbot_route_selective_refresh_2026-10-13.zip` · 241 files |
| **26 · Exact route-bound task** | A declared task is tied to one exact route fingerprint and current owner-backed evidence, without borrowing the other route's edges. | 2/2 required edges completed on an unaffected route after the neighboring pin was revoked; **100** completed tests. | `ab_chatbot_route_bound_task_2026-10-13.zip` · 249 files |

These test figures are **per-stage completed targeted runs**, generally including overlapping regression suites. Do not add them into one unique cumulative test count. The full historical suite was not completed for these six additions; no GitHub CI outcome is asserted for the integrated archives.

## Archive identity (SHA-256)

Each archive below was verified as readable. Each successive archive adds **eight files**, preserves all preceding entries byte-for-byte, and does not overwrite the prior mathematical witnesses.

| Stage | SHA-256 |
| --- | --- |
| 20 | `e14793cf3c3831489af42a4bd2c9662431edb029d26014ee2066427abfb94f5b` |
| 21 | `191ed3da68ab40f6ee41575de81200bd325597c1c8c071c9e007322b7b4745f6` |
| 22 | `5c390e9a17fae2d6541b52d2321987561ea4f080589271beb5a6772f6ae1e661` |
| 23 | `f6b9f1a58f37f4876859ca030515ecfb98ab05757459b9cbeff892df7f5c9c54` |
| 24 | `cfb7e0b2c85384796d92fba6de1ce5eeb62ed8c2c9c803d245a41572e3809305` |
| 25 | `2ef7351439cde7413a6ebc49d9122e322f72fbdd82d40625396d9a84621e7da9` |
| 26 | `cbcab83b747e644aa3759ce8a6feb9a8cbdb195ea16f2c016725dbbdb5e856fd` |

**Where the evidence is:** These integrated ZIPs were generated and supplied in the working conversation and are not GitHub repository files or GitHub Releases. Hashes are integrity identifiers, not download links. In a locally extracted Stage 26 ZIP, the individual dated READMEs, demos, `*_RESULTS.json`, `*_REGRESSION.json`, `finite_*.py`, `ab_chatbot_*.py`, and `test_*.py` supply the runnable implementation and stage-specific observations. The latest task's relevant reproduction commands are:

```sh
python -m unittest -q test_ab_chatbot_route_bound_task.RouteBoundTaskTests
python -m unittest -q test_finite_single_route_task.FiniteSingleRouteTests
python run_route_bound_task_demo.py
```

The independently executable finite reference models know their declared complete finite laws; they do not authenticate the integrated HTTP-backed owner's identity. The owner-pinned integrated adapters replay their own witnessed observations. When a route changes or its proof is revoked, a previous success is preserved **as history**, not current proof. Skipping an unchanged dependency is a cache decision, not an independently reverified theorem.

**Next possible test:** A shared dependency graph for several route-specific tasks responding to the same external changes. Not implemented by these records. This page records completed movement; it does not predeclare the next result.


## Stage 27 · Multi-task source dependency propagation (October 13, 2026)

[Bounded evidence and reproduction](MULTI_TASK_DEPENDENCY_2026-10-13.md) · [standalone pure finite dependency checker](finite_multi_task_dependency.py) · [eight finite tests](test_finite_multi_task_dependency.py).

The full owner-bound integrated chatbot adds a task-to-source incidence ledger: two tasks can depend on the left route while one depends on the right; a middle-source change selects only tasks using that middle; a shared source change selects all dependent tasks. Tasks that were not replayed remain historical/cached, and a task must freshly replay its own route before its obligations count as current evidence. A changed declaration or moving source blocks freshness rather than inheriting an earlier success.

**Local integrated handoff:** `ab_chatbot_multi_task_dependency_2026-10-13.zip` · 257 files · SHA-256 `03e3a0b89fb477b14c6b09e769e0d3515a004ebe9bf116f677cda86ea65c7a94`. All 249 predecessor entries unchanged. **127 completed targeted tests**: 27 new (19 live owner-bound + 8 independent finite) and 100 regressions. The full historical suite was not completed and no new GitHub CI result is asserted. The integrated owner-backed code and demo are in the local archive; the GitHub code here is the separately runnable finite reference.
