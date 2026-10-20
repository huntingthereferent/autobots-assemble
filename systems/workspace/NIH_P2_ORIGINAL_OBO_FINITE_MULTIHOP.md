# NIH Phase 2 — finite real-source URI movement beyond two hops

## Original wall and exact baseline

The previous external [OBO biomedical RDF source trial #280](https://github.com/huntingthereferent/autobots-assemble/pull/280) independently retrieved and authenticated the 2026-09-04 original `ro-base.owl` and `core.owl` (commit `091f4761ec84657cc336d623e02006d6c351722c`). Original evidence had **8,319 RDF triples** and **802** original source subclass/subproperty hierarchy relations.

The original 402-question experiment compared:
- A/B **exact two-hop** original URI composition (correct on its bounded question);
- an independent real RDFLib **SPARQL property path `+`** query, capable of any path length; and
- source-availability filtering using **explicitly synthetic** clock overlays, not original publication timestamps.

The independent static RDF reasoner could witness **87 queries** with real longer paths that the exact-two-hop A/B operation could not. The fixed **402-question original workload** and original pinned source files remain the benchmark. We will not make it easier, drop the longer questions, or rename a longer path as two hops.

## Construct the bounded relationship operation

`ab_finite_original_uri_multihop.traverse` accepts original source-URI edges (`s`, `p`, `o`, relation-domain, SHA256), a researcher-defined start/end/relationship URI, source-availability cutoffs and **an explicit maximum of 1–6 hops**. Dates here are test-owned overlays.

It uses deterministic finite breadth-first search with:
- original edge provenance on each step, including the *separately observed original SHA256*, original subject/predicate/object URIs and the test-clock gate;
- a complete URI-by-URI witness, preserving intermediate nodes rather than reporting a bare `true`;
- strict direction/predicate matching and no synthetic cross-subject edge construction;
- no cycles within a witness, finite 2,500-edge input maximum and 30,000 edge-extension budget;
- an explicit error if capacity is exceeded: **never call an incomplete search an observed negative**;
- a negative result that means **no path within the declared hop bound**, not no path in the entire graph or clinical world.

This does **not** infer treatment efficacy, biological causal relationships, a clinical event-validity date or unrestricted OWL entailment. The observation is a bounded source path in the requested original graph.

## Independent source verifier

The reproduction module reruns the previous OBO source-owner original 402-case SPARQL/static benchmark. For every new positive, the verifier independently reconstructs the original source edges from pinned original files and rejects any path that changes a relation SHA256, subject, predicate, object, synthetic knowledge/validity date or direction. Original source edges cannot be invented by the traversal.

The evaluator also compares **every A/B result** with the **unchanged RDFLib SPARQL `+` temporal oracle**; any mismatch remains visible in the report. It records how many previously unsupported **real longer source paths** the finite traversal recovers, and how many remain unsupported because the bound or another limitation is reached.

### Hard result distinctions

- `old_AB_exact_two_hop` — original narrower operation; do not change the previous score.
- `new_AB_finite_multihop` — new operation with source witness and declared six-hop bound.
- `independent_RDFLib_SPARQL_plus_temporal` — **more general** independent graph inference oracle on the same test-time-filtered original edges.
- `independent_static_SPARQL_plus` — original stronger static source graph reasoning without test clocks.
- `recovered_real_source_longer_temporal_paths` — only count a previously missed longer path **when it is actually available at the hypothetical time cutoff** and the new witness succeeds.

## What this can and cannot establish

A successful native test that recovers the 87 previously observed real source longer-path questions (or the portion of them available under synthetic cutoff) demonstrates **functional relationship traversal on original external biomedical ontology structure**, with independent evidence links. Unlike the earlier fictional 13-question score, this tests 402 original external graph reasoning questions.

The temporal stamps attached to these original ontology edges remain deterministic **synthetic test labels** because OBO source records do not furnish exact historical per-edge publication/clinical-validity times. Consequently success does **not** prove real-world historical biomedical `known_at`, clinical applicability, official NIH challenge benchmark success or full OWL consistency/unsatisfiable-class capability.

Existing original W13 emitted Python, 12-job native journal, World48 mathematics, NIH Phase 1 source history and A/B license remain unchanged. The parent OBO source trial uses the optional `owlrl` library only inside its focused consistency probe, so the broad repository test runner can import the module without an undeclared global dependency.

## Reproduction

```bash
python -m pip install 'rdflib>=7,<8' 'owlrl>=7,<8'
python -m unittest -v network.tests.test_nih_p2_external_obo_multihop_trial
python -m systems.workspace.nih_p2_external_obo_multihop_trial \
 --ro-base /verified/original/ro-base.owl \
 --core /verified/original/core.owl \
 --output /tmp/nih-p2-original-multihop.json
```

The dedicated GitHub Action retrieves the **exact immutable pinned original release**, independently verifies both complete-file SHA256s and retains only derived case-by-case path receipts and metrics, **not third-party original OWL file bodies**.

The actual success/failure counts must come from the retained CI run. Next decisions should follow the real remaining mismatches and source movements, not expand the world without observed need.
