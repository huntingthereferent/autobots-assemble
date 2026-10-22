# Lane C E20 — authenticated source RDFS witnesses for inferred type metadata

**State: IMPLEMENTED, source-connected result NOT yet verified.**

E19 established 1,993 original Bgee referent nodes (129 genes, 1,864 source targets), two original source-authored rdf:type assertions, and 27,257 additional inferred rdf:type assertions in the complete authenticated OWL RL closure. These are ontology-derived metadata, not newly measured biological events.

## Research question

How many of E19's 27,257 inferred types can be justified by an independently implemented, *source-owner-only RDFS witness subset*, without invoking OWL RL as the explanation mechanism?

E20 first reauthenticates the exact original Bgee source SQL archive, three original author GenEx/Ontop/R2RML mapping files, and two complete original Relations Ontology files under existing Git blob and SHA-256 receipts. It independently builds all 25,027 source-authored expression relations through original join and SQLite, plus all 100,108 previously verified four-rule logical relations using RDFLib SPARQL.

## Finite provenance procedure

The separate explicit_rdfs_type_oracle reads ONLY original source-owner domain, range, subPropertyOf, and subClassOf axioms, matching their full sets with a declarative SPARQL input scan. Plain Python computes bounded property/class ancestry and original domain/range consequences from original observations plus the four prevalidated rule output sets. Original rdf:type assertions and their source class ancestry remain distinguishable.

A fresh source-original 34,181-triple graph is materialized with owlrl.OWLRL_Semantics. The whole original-node rdf:type result set is enumerated twice, by native predicate traversal and declarative SPARQL. Every independently supported RDFS consequence MUST be present in that OWL RL set; any absence fails. Report *independently explained inferred types* and the *remaining residual types* without assuming either value. A residual is a limited-oracle explanation gap, not an empirical inconsistency or independent molecular discovery.

Eight synthetic test cases check property/class ancestry, original named schema premise removal, direct four-rule inputs, original/non-native scope, finite cycles, missing Oracle deductions, original-type claims and transparent residual accounting.

## Constraints

The dedicated E20 source-connected workflow uses a 12-minute full-profile timeout and 6-GiB process-memory bound; no source rows or inferred RDF bodies are uploaded. Evidence contains only source receipts, grouped type counts and digests, with missing witnesses triggering CI failure. The experiment does not establish independent full OWL RL completeness, OWL DL satisfiability, biological validity, clinical efficacy, official NIH result, original valid/publication dates or A/B advantage over an equally capable static engine. Lane C PR #404 stays draft; no W13, ARC, WORLD or other NIH lanes are modified.
