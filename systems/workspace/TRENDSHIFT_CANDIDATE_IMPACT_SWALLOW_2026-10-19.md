# Trendshift source swallow — candidate impact without a second executor

Date: 2026-10-19. Discovery: [Trendshift daily live board](https://trendshift.io/). Inspection is bounded to the source files below; **not** all of any repository, and not an assertion that every outside technique is needed.

## Live intake and rejected imports

* **[google-research/harness2](https://github.com/google-research/harness2)** — already selectively swallowed through the existing PR #217 into `harness_client.py` and `contrastive_harness.py`. No duplicate client or planner.
* **[morluto/rea](https://github.com/morluto/rea)** — earlier separate A/B swallow lane already exists. Do not import its product, name or license.
* **[cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill)** (MIT), source `skills/security-audit/validate-coverage-ledger.cjs`: canonical IDs, independent machine-validated coverage, and explicit statuses. Existing A/B native evidence gates cover the general boundary; no second security scanner or fabricated "covered" results.
* **[KnifeLemon/Filee](https://github.com/KnifeLemon/Filee)** (MIT) — broad offline conversion is not a missing native research relation, so no format converter or new file dependencies.
* **[xerj-org/xerj](https://github.com/xerj-org/xerj)** (Apache-2.0) — indexing is potentially useful at data scale, but the existing finite B9 graph can be inspected without introducing a search engine or a second state store.
* **[deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness)** (MIT) — another external AI runtime would be a client of the shared workstation, not the authority to replace its owned worker/execution path.

## Three non-AI sources inspected

1. **[SolidCraft](https://github.com/tangency-labs/solidcraft/tree/65e6d9dafd3680d6566844bac24ac24fa2019972)** (Apache-2.0), `crates/doc/src/project_order.rs` and `crates/kernel/src/provenance.rs`: distinguish exact topological provenance from mere geometric proximity; a result feature may have multiple input origins. This argues **not** to merge two possible B9 paths just because they reach the same proposed result.
2. **[OpenHeart](https://github.com/AhmadHassan-BTed/OpenHeart/tree/9699c1a0a86b465a2bdbebe4b1f96127a012b36e)** (MIT), `src/tra/delta/invalidation.rs`: report potentially stale derived records when their source graph hash differs. B9 already retains historical claims and can freshly recheck each receipt; it lacked a narrow view of which proposed downstream candidates warrant another inspection when a candidate source is explicitly reported changed.
3. **[Jantt](https://github.com/AhmadHassan-BTed/Jantt/tree/2fd3830d89090f1cd95683a18f4d715a1c704f44)** (MIT), `packages/core/src/pipeline/stages/cycle-guard-stage.ts` and `cascade-resolve-stage.ts`: fan-out through dependency graphs, distinguish unresolved cycles, and honor constraints rather than silently rewriting a task. B9 already rejects cycles *at admission*. A new **read-only** traversal can reject even a corrupted historical cycle before projecting any affected set.

## The smallest new A/B movement

`systems/workspace/construction_impact.py` asks the real original B9 RuntimeJournal:

> Given one or more *explicitly named* candidates that changed, which downstream **proposed** candidate nodes are reachable, including those reached through multiple alternative branches?

It does **not** decide whether a source changed, whether a source is correct, whether the relation is real, or whether work should execute. It reports:

* Every reachable downstream candidate that may need renewed inspection, with **one deterministic shortest illustrative route** per candidate — not a claim that it was the only possible route.
* The proposed downstream candidates shared by more than one changed upstream path.
* The candidates not reached by these **proposed** edges, retaining independent branches without claiming those branches are safe.
* A deterministic digest of the read-only report. Original journal, source-owner rights, worker execution, source editions, pinned preferences, and recorded native evidence remain untouched.
* Explicit `POSSIBLE_REVIEW_ONLY`, `current_native_evidence_reverified=False` and `worker_execution_authorized=False`.

The mechanism fails closed for unknown/cross-goal nodes, duplicate changes, malformed or cyclic persisted edges, and bounded capacity (256 nodes, 2,048 links, at most 32 changed candidate IDs). It does not send change notifications, add a scheduler, or automatically feed native B2/W13 workers. It keeps the scope that observation determines what is supported.

Tests in `network/tests/test_construction_impact.py` use real B9 goal/candidate/link journal records, shared links and alternative branches, exact fan-out paths, corruption/cycle controls, cross-goal rejections, deterministic repeat, and **byte-identical journal before/after observation**. Their source changes are explicit test inputs, not detected real-world events.

Reproduce: `python -m unittest -v network.tests.test_construction_impact`.

All new implementation is original A/B Python; none of the upstream CAD, UML or schedule source is copied. External licenses remain with upstream authors. Passing these tests verifies **only** the bounded graph projection; it is not scientific verification of an actual WORLD motion, a native worker outcome or an external source's research results.
