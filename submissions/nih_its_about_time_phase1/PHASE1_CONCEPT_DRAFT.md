# Temporal Evidence Availability in Biomedical Knowledge Graphs
## An As-Known-At and Valid-Time Framework for Reproducible Reasoning

**NIH “It's About Time” Challenge — Phase 1 Conceptual Design and Feasibility**  
**DRAFT FOR REVIEW · October 18, 2026 · NOT SUBMITTED**  
**Research:** James Muneoka, independent research / `huntingthereferent`  
**Companion ontology:** `phase1-temporal-ontology.ttl`

### Abstract

A biomedical fact can describe one interval while becoming available to a researcher, clinician, or public-health analyst only later. Static knowledge graphs (KGs) often retain the fact but lose this distinction, allowing evidence recorded later to appear in earlier decisions. We propose a source-preserving temporal KG design that separates *valid time* (when a source says a fact applies) from *knowledge availability time* (when evidence was available under a stated source policy). Each assertion carries an explicit source and, where independently established, a publication or observation witness. A query is evaluated with both a target time and a knowledge cutoff. The system withholds facts that were not yet knowable; it records unresolved source gaps rather than manufacturing missing historical versions.

A bounded source-owned implementation already constructs synthetic RDF with OWL-Time, PROV-O, and Biolink mappings, executes temporal queries, and checks exact results against an independently implemented observation-level oracle. The original twelve-job workstation also includes a browser-backed prototype/test chain and synthetic temporal-versus-static benchmark. Separate public-data experiments have verified official registry posting metadata, one 2023 AACT archived dataset, and a third-party derived historical corpus. They have **not** established authenticated public posting dates or raw historical content for individual study versions. This proposal distinguishes those observations from proposed extensions, including richer ontology constraints, uncertain source availability, and evaluation on independently authenticated historical releases. The biomedical motivation is retrospective interpretation of changes to public clinical-trial registry status and evidence, not clinical recommendation or patient-level prediction.

### 1. Problem, use case, and feasibility question

**Primary use case: longitudinal interpretation of public clinical-trial information.** A reviewer asks: “As of date K, what publicly available registry statements applied to trial T at date V, and which later-released statements must be excluded?” A conventional union of all historical and current graph statements can answer with a status that was published only after K. The resulting error is not necessarily a false clinical fact: it is a fact placed in the wrong information context. The same distinction could later be applied to evolving guidance, surveillance alerts, and sequential care pathways, provided that their own sources and governance permit it.

The feasibility question is narrow: **Can a temporal representation and executable eligibility rule reliably prevent future-evidence leakage while retaining source attribution, changes in validity, and explicitly unresolved conflicts?** Success on constructed examples is evidence for the implementation's limited semantics, not proof of clinical validity or general biomedical transfer.

The proposed workflow is suitable for public and de-identified research datasets and does not need protected health information (PHI). It does not infer treatment efficacy, regulatory compliance, or trial sponsor intent. It creates an auditable account of what a chosen source record allowed an observer to know at a particular time.

### 2. Temporal representation and design choices

The unit of evidence is a **source-qualified assertion**, not an unqualified timeless triple. An assertion A consists of:

`(subject, predicate, object, valid_from, valid_to, available_from, source_ref, provenance_state)`.

`valid_from` and `valid_to` define a half-open time interval `[valid_from, valid_to)`. `available_from` is an evidence-availability cutoff *under a declared source policy*. `source_ref` identifies a bounded source artifact, its version when available, or a recorded witness. `provenance_state` distinguishes an authenticated original historical version from a dated archive snapshot, a present-day registry record, a third-party reconstruction, or unavailable evidence. These categories are not interchangeable.

The framework also distinguishes five clocks:

1. **Valid/effective time:** the interval a source describes. The interval can be unknown, retrospective, or later corrected.
2. **Event time:** when an actual biomedical event occurred; it may differ from the interval stated in a document.
3. **Submission time:** when a registry submitter supplied information; this is not necessarily public disclosure.
4. **Public posting/availability time:** when the specified audience could access a version, established by source-specific publication evidence.
5. **Observation/retrieval time:** when this research system obtained its copy and recorded its digest.

When a record provides only a submission timestamp or a current “last updated” field, the system does **not** silently convert it into a historical public-availability timestamp. Where no authenticated publication time exists, retrospective public-knowledge answers remain *indeterminate* for that assertion; an alternative explicit question such as “what was in the archived snapshot by its deposit date?” may still be answerable.

#### 2.1 Formal query rule

For a query `Q(K,V)`, K is the knowledge cutoff and V is the valid-time target. Within a closed-world, fully witnessed bounded source set, assertion A is eligible only if:

`A.valid_from <= V < A.valid_to AND A.available_from <= K`.

The returned record is not just a set of `subject-predicate-object` values. It includes the assertion identifiers, their provenance witnesses, the exact cutoff pair, and a disposition: **eligible**, **withheld as later-known**, **outside validity**, **contradictory within declared constraints**, or **source availability unresolved**. If `available_from` is not authenticated, a query demanding verified historical public availability cannot return a positive historical assertion based on that field alone.

This is an explicit deterministic selection rule, not an OWL-wide closed-world entailment guarantee. OWL supplies an interoperable description of the entities, intervals, and provenance relations. A query planner applies date inequalities and source-admission policy outside standard monotonic OWL reasoning. Future work may incorporate time-aware embedding features, but a similarity score can **rank only temporally eligible evidence**; it must never override the time or provenance guard.

#### 2.2 Evolution and uncertainty

A correction produces a new assertion and a relation to the superseded one; it does not rewrite prior evidence or erase its source. Incompatible values are flagged as a conflict only if a **domain-specific predicate is explicitly declared functional for the comparison scope**. Multiple values of other predicates are retained without claiming contradiction. Unknown upper/lower validity bounds, publication times, or source identities stay explicitly unresolved, with the affected queries reported separately instead of forced into true/false conclusions.

A proposed extension adds ordered evidence events, source-confidence annotations tied to their method of measurement, and an **evidence frontier**: the subset of claims admitted from authenticated original versions at each knowledge cutoff. Temporal embeddings, if added, will encode intervals, order, provenance class, and missing-time masks; the proposed rule above remains the hard eligibility constraint.

### 3. Worked biomedical-facing example

The existing source-owned Phase 1 scope uses a **fictional clinical-sequence fixture**, not real patient records:

- `prior-note`: source note valid January 1–10, 2026, knowable January 1.
- `delayed-result`: fictional result valid January 3–10, 2026, but not knowable until January 5.

At `K = 2026-01-04, V = 2026-01-04`, the temporal answer includes `prior-note` and withholds `delayed-result`. A static union treating every valid fact as knowable includes both, thus leaking the later result into the earlier decision. At `K = 2026-01-06, V = 2026-01-04`, both are eligible. At `V = 2026-01-11`, both are outside their stated validity intervals. The case demonstrates the distinction between retrospective fact validity and the observer's knowledge.

A biomedical adaptation would replace these fictional sources with versioned public ClinicalTrials.gov study-status assertions, or an independently authenticated historical archive carrying date-specific facts. That replacement is **not yet implemented as an authenticated historical-version benchmark**. Registry submission, posting, clinical event, and our retrieval dates would be distinct fields, not inferred from one another.

### 4. Ontology and semantic interoperability

The companion `phase1-temporal-ontology.ttl` is a **reviewable draft ontology excerpt**, not a claim that full biomedical OWL reasoning has been implemented. It includes:

- `te:TemporalAssertion` mapped as an `rdfs:subClassOf` `biolink:InformationContentEntity`.
- `te:validDuring` linking assertions to `time:ProperInterval` with `time:hasBeginning` and `time:hasEnd`; `te:knownFrom` linking to `time:Instant`.
- `prov:wasDerivedFrom` and explicitly typed `prov:Entity` resources to preserve source identity.
- `te:RegistryStatusAssertion` and literal status data scoped to named, fictional study identifiers.
- Machine-readable OWL axioms **beyond subclassing**: qualified exact-cardinality restrictions on a known-from instant and a validity interval, functional source-field properties, property-domain/range constraints, and disjoint evidence-state classes.
- Explicit annotations explaining that an inferred OWL property does **not** perform arithmetic interval comparisons or establish when a version actually became public.

OWL-Time supplies interval/instant vocabulary, PROV-O supplies derivation relations, and Biolink supplies an information-content anchor. Additional mappings to OBO and biomedical entity identifiers are **proposed**, not claimed as demonstrated. The design minimizes unsupported equivalence claims: a registry status observation is metadata, not a clinical outcome. The ontology can be parsed and examined independently of the existing bounded prototype; its axioms and example assertions must be checked against a semantic reasoner before any inference-quality claim.

### 5. Algorithm and research feasibility

The proposed bounded reasoning pipeline has five auditable steps:

**Ingest.** Read a permitted, version-addressable source or released archive. Preserve source owner, exact URL or release identifier, retrieval UTC, schema, and raw response digest. Reject missing identity, malformed intervals, impossible timestamps, and changed source hashes.

**Normalize.** Emit source-qualified RDF temporal assertions while retaining original field paths and uncertainty about whether a date is a submission, posting, event, validity, or retrieval time. Avoid inventing an effective date for administrative status.

**Admit.** Apply a source policy. A publicly posted historical-version question requires authentic publication evidence. A frozen archive comparison may use the archive observation bound, but must not claim that bound equals an individual amendment's posting date.

**Query.** For a given `Q(K,V)`, select temporally eligible assertions, track excluded later-known assertions, detect declared functional conflicts, and preserve provenance links. Report unresolved historical evidence as unavailable or indeterminate rather than as a reconstructed record.

**Verify.** Independently recompute the expected observation-level answers from pinned source inputs; execute the original generated temporal program, check returned IDs and provenance; inject source mutations and executable semantic mutants to test whether the verifier detects wrong answers. Never treat tests written against the same fixture-generating rule as external clinical ground truth.

The present implementation already supports the *synthetic subset*: scope validation, RDF/Turtle mapping, RDF parsing, knowledge/valid-time selection, declared functional-predicate conflict detection, a source-owned design-packet builder, an executable temporal Python prototype, and a browser-backed test/benchmark handoff. What remains proposed is robust evidence admission for individual authentic historical versions, full ontology-level constraint evaluation, domain transfer, and uncertainty-aware public-knowledge queries.

### 6. Feasibility evidence already recorded

This section describes **repository experiments**, not NIH-reviewed benchmarks.

**Local Phase 1 research line:** native scope, ontology, reasoning, and design-packet jobs have independent host verifiers and preserve exact synthetic parent inputs. The packet source constructs a local draft from observed cases; the host recomputes its summary from the original scope and reasoning rather than trusting its prose.

**Original Phase 2 research line:** twelve source-owned native jobs were independently replayed with exact workstation ancestry. The synthetic benchmark compares the original emitted temporal Python program against a defined static-union baseline and an independently implemented observation-level oracle. The source-variation continuation recorded **729 actual executions** (nine constructed dataset conditions by 81 query cutoffs), all agreeing with the original source-observation oracle. A subsequent semantic mutation experiment detected **eight selected executable semantic faults out of eight**. These are meaningful bounded falsification checks, but neither measure general biomedical KG performance nor verify a real clinical decision.

**External source line:** an official ClinicalTrials.gov API v2 intake retrieved and hashed limited public posting metadata. A checksum-pinned 2023 third-party AACT dataset was independently downloaded and matched against separately fetched *current* registry records. A second source, Byungwoong Yoo's **TrialTrace** (derived data attributed under CC BY 4.0), was independently checked against its published SHA-256 corpus hashes. A cross-source study-ID join was verified. However, the original raw version-specific ClinicalTrials.gov history payloads are not present in the derived corpus; a separate undocumented site history endpoint returned **HTTP 403**. The source gap is genuine: neither a 2023 archived row nor a third-party derived transition verifies the *exact public posting date of that specific registry version*.

These experiments establish local implementability, provenance discipline, and robustness against selected synthetic errors. They do not establish clinical accuracy, patient benefit, general OWL entailment, or completion of the official challenge's Phase 2.

### 7. Phase 1 feasibility assessment and measurable criteria

**Criterion A — time-respecting correctness.** On a fixed, preregistered collection of synthetically generated observations and independent hand-labeled temporal query answers, report exact match rate; count future-evidence leakage cases and boundary failures; reject any nonzero leakage as a failed test of the stated guard.

**Criterion B — source and version integrity.** For every admitted real version, require a reproducible source locator, verified identity, original response digest, known retrieval time, and independently supported visibility/release timestamp appropriate to the query. Record `UNAVAILABLE` or `INDETERMINATE` when any required witness is missing.

**Criterion C — ontology rigor.** Parse and validate the provided TTL; check OWL restrictions, property domains/ranges, and declared disjoint classes with a separately chosen reasoner. Test deliberately invalid graph examples. Recognize that OWL's open-world semantics do not by themselves detect missing dates or execute interval arithmetic.

**Criterion D — static baseline comparison.** Use the *same* facts and query grid for static union and temporal selection. Report temporal consistency, withheld future facts, any conflicts, source-count/triple-count, and runtime or resource cost. Do not extrapolate beyond a bounded dataset or present an intentionally leaky static union as the best possible modern temporal baseline.

**Criterion E — real-world transition.** Obtain two or more independently authenticated original historical study versions or dated source snapshots with evidence of the observation/publication times. Evaluate at least one change whose source versions and visibility times are independently established; demonstrate that the answer is reproducible by a reviewer who did not generate the fixture.

Meeting A–D supports the *local design's* feasibility. E is necessary for defensible claims about authentic historical registry knowledge. All results should include negative controls, failure receipts, and exact tested source revisions.

### 8. Expected impact, limitations, and extensibility

For biomedical evidence reviews, pharmacovigilance, registry monitoring, and public-health surveillance, separating fact-validity from information availability could reduce temporal leakage and make retrospective interpretations auditable. This is a potential research benefit, not a measured patient outcome. The same abstraction can attach to other domain statements only when the domain supplies legitimate validity criteria and traceable availability evidence.

The main scientific risks are (i) missing historical versions; (ii) mistaken equivalence between submission, publication, observation and event times; (iii) retrospective corrections of past facts; (iv) open-world OWL reasoning versus closed-world eligibility checks; (v) conflicts under wrongly asserted functional predicates; and (vi) biased results from easy or internally generated examples. The design mitigates these through explicit source-state distinctions, fail-closed admission, negative controls, source-level comparison, and an independent real-history evaluation gate.

We do **not** claim a novel invention of bitemporal databases, standard interval algebra, OWL-Time, or PROV-O. The proposed contribution is their *source-qualified composition with explicit non-fabrication of missing historical knowledge and separately reproducible eligibility verification* for bounded biomedical KG evidence. Its novelty and advantage must be evaluated against relevant prior art and comparable time-aware KG approaches.

### 9. Deliverables, status, and conditions for submission

**Deliverable 1 — this concept/design draft:** a reviewable, not-yet-submitted Phase 1 narrative with an explicit model, a reproducible fictional example, feasibility evidence, source limits, and a real-world test plan.

**Deliverable 2 — `phase1-temporal-ontology.ttl`:** a machine-readable OWL/RDF example with selected logical axioms beyond a class hierarchy. It illustrates proposed semantic structure; it is not an official NIH-accepted ontology.

**Review required before submission:** Verify eligibility and registration; reconcile the exact official challenge documents, page and font requirements, and any later Q&A; validate the ontology in a separate reasoner and inspect its interpretation; independently review correctness and novelty claims; consider competing methods; and obtain informed owner approval concerning the challenge's intellectual-property provisions.

The official NIH announcement sets **January 15, 2027** as the Phase 1 submission deadline and specifies a **10-page maximum PDF, body text at least 11 pt, and a separate machine-readable ontology file no larger than 3 MB**. It also states that **only Phase 1 winners are eligible to submit to Phase 2**. Registration and submission occur on the competition portal, not through a repository merge. The published participation rules include nonexclusive, irrevocable, royalty-free government licenses while the participant retains other applicable intellectual-property rights; this should be reviewed independently before accepting the rules.

**Submission status: NOT REGISTERED OR SUBMITTED BY THIS DRAFT.** No NIH prize, award, scientific review, clinical benefit, or Phase 2 eligibility is claimed.

### Sources and reproducibility pointers

1. NIH, [It's About Time: Temporal Reasoning in Biomedical Knowledge Graphs Challenge](https://www.nih.gov/challenges/its-about-time-temporal-reasoning-biomedical-knowledge-graphs-challenge) — scope, Phase 1 scoring, format, deadlines, competition rules (accessed October 18, 2026).
2. [Synthetic scope fixture](../../network/tests/fixtures/nih_scope_example.json); [reasoning fixture](../../network/tests/fixtures/nih_reasoning_example.json); [ontology input](../../network/tests/fixtures/nih_ontology_example.json).
3. [Original packet builder](../../systems/workspace/nih_packet_worker_source/packet_worker.py); [independent packet verifier](../../systems/workspace/nih_packet_native.py).
4. [Original twelve-job Phase 2 benchmark](../../systems/workspace/nih_benchmark_temporal_join.py); [synthetic source-variation report](../../systems/workspace/NIH_P2_SOURCE_VARIATIONS.md).
5. [Verified third-party AACT archive boundary](../../systems/workspace/NIH_P2_REAL_ARCHIVE_BOUNDARY.md); [TrialTrace data and CC BY attribution](../../systems/workspace/NIH_P2_DERIVED_HISTORY_BOUNDARY.md); [cross-source limitations](../../systems/workspace/NIH_P2_CROSS_SOURCE_BOUNDARY.md).
6. [Historical-version evidence still unavailable](https://github.com/huntingthereferent/autobots-assemble/issues/106); [refused original-version retrieval](https://github.com/huntingthereferent/autobots-assemble/pull/107).

**All dates, statuses, and source references in the fictional demonstration are synthetic.** The real archive and current-record intake are separate, bounded research observations.
