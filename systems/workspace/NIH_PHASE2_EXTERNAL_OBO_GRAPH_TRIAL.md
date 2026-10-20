# NIH Phase 2 — external original biomedical ontology vs real static RDF reasoner

This moves directly beyond the internally authored fixed practice set from [PR #276](https://github.com/huntingthereferent/autobots-assemble/pull/276). W13 + separately authored A/B operations passed **13/13** fictional practice cases with *limited* RDF composition, not the official NIH Phase 2 shared benchmark. The goal here is a more demanding external **actual RDF graph** with independently executed graph reasoning on both static and test-time-filtered sources.

## External data (not invented edges)

The source-owner [OBO Relations Ontology (RO)](https://github.com/oborel/obo-relations), **original September 4, 2026 release** (commit `091f4761ec84657cc336d623e02006d6c351722c`) provides exact real `ro-base.owl` and `core.owl`. These originals contain actual ontology `rdfs:subPropertyOf`, `rdfs:subClassOf`, `owl:disjointWith` and biomedical relationship vocabulary. The external source declares [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/); the CI reads these original files only and does **not** copy their full contents or change A/B's own All Rights Reserved license.

Each CI run independently downloads both **exact commit-pinned raw files**, verifies RDF/XML parsing, ontology version `2026-09-04`, source license and nontrivial original source relationships, and hashes the entire original source file. External files are ephemeral and excluded from the retained artifact.

## Evaluation target

Construct finite **two-hop** subproperty/subclass graph compositions `A --rdfs:subPropertyOf--> B --rdfs:subPropertyOf--> C` (and independent subclass analogues), using actual original source edges. A/B's bounded graph join returns intermediate original URI witness nodes and whether such a two-edge path exists.

Compare against **separately executed rdflib SPARQL property-path reasoning**:
- A finite, source-filtered original-graph query under two *hypothetical* known/valid clock labels;
- A real **full static RDF graph reasoner** with SPARQL property-path `+` over *all* original source triples. This baseline is stronger than the old `static_snapshot_ids` list because it can infer relationship reachability through arbitrary-length paths.

The source ontology **does not publish true edge-by-edge known/valid time**, so the deterministic timestamps attached to each original graph edge are explicitly labelled **synthetic stress overlay**, not the source's original publication events or clinical validity. These scores must never be called real biomedical as-known-at correctness or extrapolated to Phase 2 performance.

The A/B operation specifically tests **exactly two edges**; the SPARQL `+` oracle tests **arbitrary-length paths**. Cases where SPARQL proves reachable but A/B cannot are retained as real scope **failures**, not repaired by making the oracle match the A/B result.

The extended trial deliberately selects two distinct groups **from the original ontology's edges**: (1) witnessed two-hop pairs, where A/B and an independently constructed RDF two-edge oracle must match, and (2) witnessed three-hop paths with **no shorter direct or two-hop path**, where the capable static SPARQL `+` reasoner can succeed and the bounded A/B operation must truthfully return no exact two-hop witness. These genuine longer-path cases are required to reveal a measurable **structural limitation**, separate from the hypothetical clock/filtering comparison. An independent RDF two-edge product also checks the exact intermediate witnesses.

## Logical inconsistency measurement — explicitly limited

Use an actual original `owl:disjointWith` premise from the external ontology, **inject a labelled synthetic individual deliberately typed as both incompatible classes**, and ask the external `owlrl` OWL RL rule implementation to flag the contradiction. This tests a **restricted inconsistency signal**, not a full OWL DL reasoner, original ontology inconsistency verdict, or unsatisfiable-class count. A nonzero error count is valid only for the injected fixture, never evidence of a broken OBO ontology.

Record original triples, source relationship type counts, SPARQL-vs-A/B disagreements, future-leakage cases under the hypothetical clock overlay, provenance hashes, source-domain coverage and limits. No user/private biomedical data.

## What successful CI would and would not prove

A pass would establish that the bounded A/B operation constructs valid real external biomedical ontology source relationships and agrees with an independent RDF oracle on the exact two-hop question, that a real static RDF reasoner yields measurable differences when hypothetical source-availability clocks move, and that an OWL RL **deliberately inconsistent fixture** triggers a bounded signal.

A pass does **not** establish real historical biomedical temporal performance, source event release times, causal clinical reasoning, scalability to all NIH KGs, OWL DL unsatisfiable classes, the official shared benchmark or Phase 2 eligibility. The official NIH [challenge rules](https://www.nih.gov/challenges/its-about-time-temporal-reasoning-biomedical-knowledge-graphs-challenge) state **only Phase 1 winners are eligible to submit to Phase 2** (scheduled in 2027). The Phase 1 deadline is **January 15, 2027**.

This is an incremental external graph validation and an honest measurement of where the existing A/B semantics are too narrow; neither the old W13 source/journal nor World48 mathematics is changed.

## Run

```bash
python -m pip install 'rdflib>=7,<8' 'owlrl>=7,<8'
python -m unittest -v network.tests.test_nih_phase2_external_obo_graph_trial

# Use the two original immutable-source files downloaded by the CI workflow:
python -m systems.workspace.nih_phase2_external_obo_graph_trial \
 --ro-base /exact-source/ro-base.owl --core /exact-source/core.owl \
 --output /tmp/obo-original-temporal-vs-static.json
```

The dedicated Actions job retains only derived source/metrics, actual independent RDF answers and entire original source SHA-256s; it does not republish the original ontology files.
