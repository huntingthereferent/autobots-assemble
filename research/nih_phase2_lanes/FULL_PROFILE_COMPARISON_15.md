# Lane C E15 — full OWL RL independent profile boundary

**On commit: IMPLEMENTED, NOT YET SCIENTIFICALLY VERIFIED.**

The existing Lane C source-authenticated fourth-rule comparison verified 25,027
original Bgee mapped expressions and 100,108 conditional RDF consequences
over all 34,181 original Bgee+GenEx+RO triples. A new Python OWL RL general
profile engine now receives the whole unchanged graph, unlike the selected
four-rule Jena implementation. The independently prepared four-rule RDFLib
SPARQL set is frozen as comparator.

The target is full-set equality within the original mapped gene/target node
universe for three RO predicates in four defined directions. Unexpected
source-mapped pairings must be recorded as discrepancies, not silently hidden
by filtering for only expected pairs. Store hashes, never original RDF rows.

Boundaries: 12-minute experiment timeout, 6-GiB virtual memory budget,
1,800,000 materialized-RDF-triple post-closure cap, and a 22-minute GitHub
Actions job limit. Timeout, memory exhaustion, source mismatch or disagreement
does not count as a scientific PASS. Preserve the negative result.

A successful result would prove only scoped equality of named property
consequences with this version of the OWL RL engine. This is NOT a second
independent full-OWL-RL-profile implementation, full OWL DL consistency
testing, independent biological truth, clinical finding, NIH scoring or A/B
advantage. Do not merge PR #404 without final-head CI and ancestor review.
W13, other NIH lanes, ARC, WORLD, licensing and original owner files untouched.
