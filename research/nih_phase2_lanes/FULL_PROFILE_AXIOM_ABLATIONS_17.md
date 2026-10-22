# Lane C E17 — full-profile source-axiom premise removals

State on implementation: IMPLEMENTED / NOT YET SOURCE-VERIFIED.

Earlier E14 established four exact authenticated rule-deletion counterfactuals
under a *selected-rule* Jena reasoner: 0, 75,081, 50,054, 75,081 consequences.
E15's intact **whole-graph** OWL RL closure matched 100,108 corresponding
consequences. E16 is a separate audit of the larger source-node universe.

E17 now asks whether those four premise-dependency effects survive complete
OWL RL reasoning over the real 34,181-statement Bgee+GenEx+RO combined graph.
An alternative original owner-defined axiom might restore a deduction absent
under the deliberately limited four-rule engine. The earlier counts are frozen
comparators, not assumed results.

Reauthenticate every original input file. Make four separate copies of the
original graph. Remove exactly one owner axiom from each transient copy;
run full Python OWLRL_Semantics with RDFS closure. Against each result compare
the complete RDF triple set to an independently authored RDFLib SPARQL finite
four-source-rule counterfactual oracle. Retain every extra/missing count,
directional partition, source owner axiom, witness digests, timings and memory
statistics without raw source SQL/RDF rows or the inferred RDF body.

Resource boundary: 15 minutes total subprocess time, ~6 GiB virtual memory
and 1.8 million materialized triples per control, 22-minute outer workflow.
Differences between full-profile and selected-rule implications count as
scientific counterexamples to selected-rule sufficiency, not as a fake PASS
for equality. Missing source, runner failure, timeout or incomplete modes
must remain NOT VERIFIED.

This does not establish full OWL DL consistency, new biological measurements,
patient outcomes, NIH challenge scoring or A/B superiority. Keep PR #404
draft, all ancestral review gates intact, and W13/ARC/WORLD/other NIH lanes,
licenses and source owner files unchanged.
