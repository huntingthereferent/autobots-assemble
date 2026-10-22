# NIH Phase 2 — OWL entailment and ontology inconsistency scope

**Trace:** existing [parent PR #285](https://github.com/huntingthereferent/autobots-assemble/pull/285) → [tracking issue #400](https://github.com/huntingthereferent/autobots-assemble/issues/400) → this independent branch.

## Current referent
[#285](https://github.com/huntingthereferent/autobots-assemble/pull/285) verified 402/402 finite 1–6-edge source-reachability questions against independent SPARQL property paths. This did not establish general OWL entailment or original ontology consistency. Historical edge-time cutoffs were synthetic.

## Independent movement
Pin original OBO Relations Ontology release, distinguish true source axioms from experiment-added fixtures, and predeclare a finite test battery for entailment, subclass/property inference, disjointness contradictions, and unsatisfiable-class detection under a named reasoner profile. Compare independent engines or implementations with the **same source axioms**.

## Measured source-owned outcomes — October 22, 2026

Three separately implemented source-connected experiments now run on the identical whole-file-SHA-256-pinned OBO Relations Ontology 2026-09-04, source-owner commit `091f4761ec84657cc336d623e02006d6c351722c` (8,319 RDF triples), with independent validators and retained run evidence.

1. [Direct asserted disjointness #39729055450](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39729055450): 7 explicit named `owl:disjointWith` pairs, 0 direct source asserted same-individual `rdf:type` conflicts; 1 contradiction in a **separate injected synthetic fixture**. 5/5 focused tests passed.
2. [Inherited named RDFS closure #39754651358](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39754651358): 15 source asserted named `rdfs:subClassOf` edges, 0 additional inferred named individual type assertions, 0 disjointness conflicts under this restricted inheritance, independent RDFLib closure agreement. A **separate fixture** exercises a positive inherited conflict. 6/6 focused tests passed.
3. [Original OWL RL source-schema entailment #39755850546](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39755850546): 787 source asserted *named* `rdfs:subPropertyOf` pairs. The finite transitive closure produces **1,656 additional nonasserted relation-schema pairs**, validated against independent RDFLib property traversal over the source relation hierarchy. An independently installed `owlrl` engine materialized all 24 deterministically selected original-source minimum-witness chains, with exact owner-source edge digests. 6/6 focused tests passed.

This last result is **true transitive RDFS/OWL RL schema entailment**, not merely uninterpreted two-hop reachability. However the source-backed OWL RL reasoner ran on selected **minimal asserted witness subgraphs**, **not** as a full materialization of the complete 8,319-triple ontology. It neither finds new biomedical patient/treatment truths nor proves the complete ontology consistent.

**Still `NOT_MEASURED`:** full OWL RL materialization/consistency on original entire graph, OWL DL class satisfiability, anonymous restrictions, original ontology temporal publication per edge, clinical validity and official NIH Phase 2 scoring. The result retains both zero findings and any errors; no unsupported assertion is upgraded to fact.

Before merging, require exact-final-head whole-repository protocol tests and parent draft review.

## Test gates
Independent source identity/hash verification, contradictory fixture isolation, unexpected inference and cyclic-path counterexamples, reasoner-profile mismatch detection and original source controls.

## Lane boundaries
- **Status (2026-10-22): OPEN / SOURCE-VERIFIED EXPERIMENTS EXECUTED; DRAFT UNMERGED.** The source-connected workflows above ran successfully. A GitHub branch/PR alone is not proof of a live private workstation lane. Full-ontology OWL consistency and official NIH evaluation remain unavailable.
- Source-owned work stays in its parent code area; this file specifies an independently auditable branch without changing other NIH source, W13 native 12-job journal/executable, WORLD, ARC or license.
- A failure, empty result or unavailable upstream source is retained as evidence, not repaired with fictional examples.
- Before any merge: implement finite source-owned tests, run dedicated authentic-source GitHub Actions, record artifact hashes and negatives, then review whole-repo protocol CI against the same exact branch head.
- This is independent research connected to NIH-style requirements, not institutional affiliation, clinical validation, patient-level inference, official challenge scoring or a grant application.
