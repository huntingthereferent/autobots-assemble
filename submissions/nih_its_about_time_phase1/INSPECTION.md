# NIH Phase 1 — inspection notes

**Status: DRAFT FOR OWNER INSPECTION ONLY. No portal registration, terms accepted, submission, official review, or NIH award is claimed.**

## Exact challenge and due date

NIH Office of Data Science Strategy: [“It's About Time: Temporal Reasoning in Biomedical Knowledge Graphs Challenge”](https://www.nih.gov/challenges/its-about-time-temporal-reasoning-biomedical-knowledge-graphs-challenge). The official Phase 1 deadline is **January 15, 2027** (the NIH announcement specifies portal deadline timing in Pacific Time). Phase 1 is **Conceptual Design and Feasibility**, not a Small Business Innovation Research Phase I grant application.

NIH specifies **one PDF of at most 10 pages**, body text **at least 11 pt**, type density **no more than 15 characters per linear inch**, and line spacing **no more than six lines per vertical inch**. A separate machine-readable OWL/RDF/OBO ontology file **not exceeding 3 MB** is also required. The submission must go through the **official competition portal** after registration. The Markdown source and example TTL here are review materials, **not** a valid submission by themselves.

## Phase 1 review rubric (from NIH)

| NIH criterion | Weight | Proposed source in the draft | Important unresolved question |
| --- | ---: | --- | --- |
| Temporal modeling innovation | 25% | Sections 2–3 | Is the combination novel relative to time-aware KG and bitemporal prior art? |
| Reasoning correctness / temporal consistency | 25% | Sections 2.1, 5–7 | Independent real historical-record oracle not yet admitted |
| Ontology rigor / interoperability | 20% | Section 4 and companion Turtle | Separate OWL reasoner validation, axioms beyond hierarchy and external date predicates |
| Feasibility / integration | 15% | Sections 4–7 | Real domain integration, scale, and evaluation against a strong prior method |
| Clinical/public-health workflow relevance | 15% | Sections 1, 3, 8 | Demonstrable real-world workflow benefit without claiming clinical outcomes |

## Evidence ancestry

- Local synthetic Phase 1 research: [scope fixture](../../network/tests/fixtures/nih_scope_example.json), [ontology mapping](../../systems/workspace/nih_ontology_worker_source/ontology_worker.py), [reasoning worker](../../systems/workspace/nih_reasoning_worker_source/reasoning_worker.py), [packet builder](../../systems/workspace/nih_packet_worker_source/packet_worker.py), [independent packet verifier](../../systems/workspace/nih_packet_native.py).
- Later synthetic implementation: [12-job source-owned benchmark](../../systems/workspace/nih_benchmark_temporal_join.py), [source-variation results](../../systems/workspace/NIH_P2_SOURCE_VARIATIONS.md), semantic mutant test PR #103.
- Original W13 playable synthetic observations: PR #130 evidence frontier, #132 independent time axes, #135 constructed source profiles, #136 three-outcome bounded synthetic publication uncertainty. Do not label these original public biomedical evidence.
- External-source progression: PRs #138/#140 authenticate two whole AACT exports; #141 finds different recorded status values; #145 links a depositor's 2022-11-04 download-date statement to an otherwise 2023-deposited file. Deposit time is **not** extraction time or exact version publication time.
- Current original-history browser experiment: draft PR #151 rendered public V94/V105 viewing banners for NCT00001756, but **neither the status field nor per-version public posting date was authenticated**. Original source [issue #106](https://github.com/huntingthereferent/autobots-assemble/issues/106) remains open; separate blocked JSON PR #107 had HTTP 403.
- Owner readiness: PR #154 independently restored GAME-WORKER-READY in a separate run, with no new worker; original-owner NIH-P2-TEST remains unwitnessed. This is distinct from the earlier synthetic twelve-job benchmark lineage.

## Owner inspection priorities

1. Check that the proposal still describes the **intended research**, not just a polished account of tests.
2. Decide whether the registry-history example is the strongest single primary biomedical use case for Phase 1, or whether to choose another public-health domain with more clearly accessible historical source versions.
3. Inspect novelty, logical assumptions, temporal embeddings, ontology structure, treatment of uncertainty, and how source-owner claims are separated from independently observed evidence.
4. Review all linked proof artifacts and strip out any wording that suggests clinical benefit, real-world benchmark scores, or original source-version evidence that has not been demonstrated.
5. Review the official rule granting NIH specified **irrevocable royalty-free, nonexclusive license rights** while retaining other applicable IP rights. This is a substantive participation decision, especially with the repository's rights-reservation intent. Seek independent legal advice if needed before consenting.
6. Validate the final ontology file with an OWL reasoner and check its intended semantics; a Turtle parser and graph-shape tests alone do not prove reasoning correctness.
7. Reconfirm the current official challenge rules and Q&A immediately before any submission. No one has verified registration/eligibility or acceptance of terms.

## Submission gate

Before anything is uploaded to NIH:

- [ ] Research owner approves content, author/participant attribution, and IP implications.
- [ ] Phase 1 narrative is rendered into a PDF with **<=10 pages**, all body text **>=11pt** and the stated spacing/density limits independently checked.
- [ ] Ontology TTL is parsed, semantically reviewed, and **<3MB**, with non-hierarchy OWL axioms.
- [ ] Every quantitative statement and source reference has a reproducible pointer, and archive **collection, deposit, retrieval and public posting** dates are not equated.
- [ ] Original historical version status content and first-public times remain open unless independently authenticated (issue #106).
- [ ] Program specificity and real-world applicability are checked against NIH's latest portal instructions.
- [ ] Registration and eligibility are independently verified.
- [ ] No unsupported clinical/award/Phase 2 eligibility claim remains.
- [ ] Final owner explicitly authorizes any external registration or submission.

**Do not interpret a green GitHub CI status or a merged local packet as a completed NIH Phase 1 submission.**
