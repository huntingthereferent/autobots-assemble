# Lane C E16 — unrestricted original-node source-predicate boundary

**Status: IMPLEMENTED; no E16 original-source result claimed until dedicated CI passes.**

E15 successfully materialized the entire authenticated 34,181-triple Bgee+GenEx+RO graph with the general Python OWL RL implementation: 183,287 final RDF triples, 100,108 exact-four-rule scoped original gene/target statements, 0 missing/extra against Jena and RDFLib SPARQL within that predeclared mapped-pair universe.

## New question
Does the full OWL RL closure include **additional** `RO:0002206` (expressed in), `RO:0002292` (expresses), or `RO:0002330` (genomically related to) RDF triples **touching any authentic original Bgee gene or source target node**, when the other endpoint and pair direction are unrestricted?

This is a distinct inclusion check. E15's mapped-pair selection can prove exact agreement within its fixed universe; it cannot alone rule out differently paired source-predicate triples involving original referents. E16 scans every allowed relation whose subject **or** object occurs in the full authenticated original source-node universe.

## Design and falsification
- Authenticate all immutable original GenEx/Ontop mapping files, the full original Bgee ZIP and the two complete original RO ontology files using the already frozen Git blob and whole-file SHA-256 receipts.
- Independently build the 25,027 exact original source gene-expression triples from the SQL author join and an independent SQLite oracle. Reauthenticate the four original owner property rules and independently derive the full 100,108-triple baseline from original source RDFLib SPARQL.
- Materialize the entire unmodified original 34,181-triple graph under `owlrl.OWLRL_Semantics` with a 12-minute/6-GiB bounded GitHub run. A new copy is materialized for this experiment.
- Enumerate the **entire original-node RO predicate scope twice**, using independent native RDFLib predicate traversal and a separate RDFLib SPARQL declarative `VALUES` query. Both must agree by exact triple set; not just count.
- Every one of the 100,108 four-rule source consequences **must** remain present. Extra predicate triples are **not** silently discarded; preserve their counts, orientation categories, and SHA-256 receipts with no original raw gene IDs or triples.
- If extras appear, report `ADDITIONAL_ORIGINAL_NODE_SOURCE_PREDICATE_CANDIDATES_FOUND`, **not** biological validation. If none appear, report `ORIGINAL_NODE_PREDICATE_SET_EQUALS_FOUR_RULES`; either result is meaningful only on the original-node/predicate boundary. Missing prior verified facts, scan disagreement, unauthenticated sources, runtime timeout and memory failure must fail.

The independently implemented query scans are not independent complete OWL RL engines. Neither E15 nor E16 proves whole-ontology logical satisfiability or OWL DL consistency. Apparent source-derived extra facts are hypotheses requiring separately attested ontology/data witnesses; these are not extra empirical gene-expression measurements, NIH scoring, patient outcomes or performance improvement over equivalent static inference. Original W13/NIH other lanes/ARC/WORLD and the source owners remain untouched.
