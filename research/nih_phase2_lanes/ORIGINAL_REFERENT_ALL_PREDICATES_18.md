# Lane C E18 — every predicate touching an original Bgee referent

**Verified owner-authenticated E18:** [full all-predicate original Bgee referent census #39845798218](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39845798218) **SUCCESS, 8/8 focused tests**. Original full 34,181-triple source graph materialized to **183,287 RDF triples** with general Python OWL RL in **64.588 seconds**. Among original source referents (129 distinct source genes + 1,864 distinct original mapped targets), the full closure has **154,445** touching RDF statements; the original graph has **25,062** touching source-node statements, and the previously independently verified four-rule set has **100,108**. There are exactly **29,275 additional statements outside both sets**: **27,257 `rdf:type`**, **1,993 `owl:sameAs`**, and **25 other RDFS/OWL class/schema statements** (4 `rdfs:domain`, 10 `rdfs:range`, 9 `rdfs:subClassOf`, 2 `owl:equivalentClass`). The additional statements under the *same three RO gene-expression predicates* are **zero**, corroborating E16's boundary. Independently implemented native RDFLib graph traversal and declarative SPARQL scans agreed by exact RDF triple identity. The 1,993 identity statements are not yet individually checked for reflexivity; their count alone does not establish aliases.

Derived-only evidence `nih-p2-lane-c-e18-all-referent-predicate-inventory`, ID **12454333892**, ZIP SHA-256 `6157f94aeea92da8285f0ca7dd11390f761fd3cc7ead404de1876b50850f3952`; retained JSON has only aggregated predicate/orientation counts and SHA-256 receipts without raw original IDs or RDF triples. These are **ontology-derived logical metadata**, not 29,275 observed genes, gene-expression events, disease mechanisms, or clinical outcomes.

---

Historical preflight status: protocol was implemented before verification; superseded above.

## Separate question

E15 verified that whole-graph `owlrl.OWLRL_Semantics` contains precisely the 100,108 source-owned gene-expression rule consequences in the frozen gene/target relationship-pair universe. E16 widened **those three RO predicates** to every original referent pairing and found zero extras.

E18 independently inspects **every RDF predicate** on **any original Bgee gene or mapped target node** in the entire full-profile closure, including `rdf:type`, `owl:sameAs`, and metadata predicates that neither E15 nor E16 admitted. The aim is to establish *which additional RDF schema and metadata consequences touch the actual original instance identifiers*, if any. **No result count for E18 is assumed before source-connected CI.**

## Method / falsification

- Authenticate all exact whole Bgee, author GenEx/Ontop/R2RML and full original RO source files; separately reproduce 25,027 owner-mapped RDF inputs through original SQL and independent SQLite.
- Freeze the full original 34,181-triple RDF graph, original referent node universe (gene subjects and original target objects), and 100,108 four-rule named predicate consequences.
- Complete OWL RL materialization on an isolated original graph copy, under the existing 12-minute/6-GiB runner resource limit; no modification of source files or other lanes.
- **Unrestricted source-referent scope:** retain every RDF triple, regardless of predicate or other endpoint type, whenever its subject or object is a member of the original gene/target referent set. This includes identity, types and literals (only counts and derived hashes are retained). Compare native complete-graph traversal to a separate declarative SPARQL triple scan by exact set equality.
- Prove that all original source-referent assertions and all prior 100,108 verified four-rule statements remain present; missing evidence, nonidentical scans, changed original source baseline or engine failure is a **FAIL**.
- Partition the inferred scope into original triples, independently verified four-rule RDF consequences, and **remaining** inferred statements. The remaining are grouped by RDF predicate, node direction, `rdf:type`, `owl:sameAs`, and other metadata. Both a zero-extra and nonzero-extra outcome are admitted with explicit status; never drop discoveries to force agreement.
- Store only grouped counts and SHA-256 fingerprints, no raw original Bgee IDs/rows, raw RDF graphs, materialized triples or source names.

**Important limits:** Two scans of a single OWL RL closure do not constitute two independent complete OWL RL engines. Source-authored ontology class/type/identity semantics are not themselves newly observed medical or biological events. E18 does not assert OWL DL consistency, validation of all original schema consequences, any patient treatment effect, official NIH Phase 2 scoring, first-public temporal provenance, or performance lift over equally capable static reasoning.

Independent files: `systems/workspace/nih_p2_bgee_original_referent_all_predicate_inventory.py`, `network/tests/test_nih_p2_bgee_original_referent_all_predicate_inventory.py`, `.github/workflows/nih-p2-bgee-all-referent-predicates-e18.yml`. This study remains within draft PR #404 and does not modify W13, ARC, WORLD, original source owners or the other NIH lanes.
