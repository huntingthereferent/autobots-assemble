# Lane C E19 — authentic Bgee referent type and identity claims

**Status: E19 original-source experiment completed; first CI report gate failed and is being independently rerun. No final-head success yet.**

[First original-source E19 run #39846804280](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39846804280) completed its complete original-file-authenticated OWL RL computation, eight synthetic positive/negative tests, and independent native/SPARQL comparison. Its measured report recorded **1,993 original source referent nodes, 1,993 reflexive self-identity triples, zero nonreflexive sameAs triples, and 27,259 total rdf:type triples** touching native nodes. The GitHub workflow still **FAILED** because it wrongly asserted **27,257 as the total type count**.

**Count reconciliation:** E18 independently reported **27,257 additional inferred** rdf:type statements *beyond* the original input. E19 counts **27,259 total** rdf:type statements on original referents: **two authenticated original-source rdf:type assertions + 27,257 newly inferred**. This is a total-versus-delta mismatch, not an independently demonstrated source change or cross-engine disagreement. The CI report gate now independently asserts both the source-authored and additional inferred counts and verifies their sum; a ninth fixture test explicitly enforces this distinction. Source bytes, inferred triples and the original graph are unchanged.

The first run's derived-only artifact is `nih-p2-lane-c-e19-original-referent-identity-type`, ID `12456151378`, ZIP SHA-256 `b04f1c7375cb5f70132ccef48b4df30c5bbd95c1aea47416909d5f0d447c8973`. **This is a scientific computation receipt from a failed workflow, not a successful CI receipt.** Re-run [E19 with reconciled gate](https://github.com/huntingthereferent/autobots-assemble/actions/workflows/nih-p2-bgee-original-identity-type-e19.yml) before final acceptance.

---

E18 confirmed the general OWL RL closure has 183,287 RDF triples overall; 154,445 statements touch the original Bgee referent-node universe, with 29,275 additional statements beyond original data and previously corroborated four source-owned inference rules. The 29,275 consist of 27,257 `rdf:type`, 1,993 `owl:sameAs`, and 25 other original referent schema statements. Those counts do **not** mean 27,257 biological phenotypes or 1,993 true new gene aliases.

## New falsifiable questions

1. Are all 1,993 `owl:sameAs` statements **reflexive** (`node owl:sameAs node`) or are any **non-reflexive, cross-resource** alias hypotheses present?
2. Does every one of the authenticated original 129 source gene nodes and 1,864 source target nodes receive reflexive self-identity within the full graph?
3. How many `rdf:type` statements touching original nodes were already owner-authored original RDF data, and how many arise **only after** the full OWL RL materialization? What are the original gene/target versus other-endpoint distributions and distinct type classes?

## Method / validation

Reauthenticate exact immutable Bgee database Git blob, three author ontology/R2RML/SQL mapping files, two whole raw RO files; apply complete OWL RL to the unmodified original 34,181-triple graph under the existing 12-minute/6-GiB finite limits.

Examine **every** `owl:sameAs` and `rdf:type` RDF triple with an original Bgee gene or mapped target URI as **either endpoint**. Independently enumerate native RDFLib graph traversal and declarative RDFLib SPARQL `VALUES` results; require exact set equality and fail if any original type/identity assertion disappears. Count original source-authored type statements separately from derived type statements. Retain identity self/nonself partitions, missing self-reflexivity (do not force success), type endpoint partitions, hashed class type aggregates, and hashed candidate nonself aliases. Do **not** save raw original gene IDs or RDF statements.

An actual non-reflexive identity result is only an **ontology-derived logical alias hypothesis** needing additional original-owner semantic witnesses; neither source-derived type nor identity is a new biological observation. The experiment does not demonstrate new patients, a clinical mechanism, OWL DL consistency, a second independent complete OWL RL engine, model superiority, or an official NIH result.

Files: `systems/workspace/nih_p2_bgee_original_identity_type_audit.py`, `network/tests/test_nih_p2_bgee_original_identity_type_audit.py`, `.github/workflows/nih-p2-bgee-original-identity-type-e19.yml`. Draft PR #404 only; W13/ARC/WORLD and other NIH lanes unchanged.
