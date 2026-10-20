# NIH Phase 2 — direct source revision and bounded RDF inference

This branch advances **the actual missing behaviors** from the Phase 2-style direct reproduction trials:

- [Direct W13 Phase 2 trial #269](https://github.com/huntingthereferent/autobots-assemble/pull/269): original unchanged emitted temporal Python answered **8/13**, original static baseline **6/13** fictional biomedical questions.
- [Time-respecting generic A/B source-chain trial #271](https://github.com/huntingthereferent/autobots-assemble/pull/271): **11/13** with separately verified 3/3 longitudinal sequence questions and 160 unseen source-path orderings.

The remaining two explicitly failed questions are source-claim **supersession** and **RDF relationship composition**. Both must be answered by executable operations and independent tests, never by editing the gold expected values.

## 1. A/B observed source revision

`ab_source_revision_relation.observe` accepts a **researcher-declared** support predicate and separate correction predicate. It only considers records with matching source `subject`, claim `object`, evidence-validity target and source-known cutoff.

- A *later-known* explicit revision changes a previously supported source claim to **SUPERSEDED**.
- A correction that was not known at query time, is about another claim/source, or is not valid at target time cannot silently rewrite the past.
- A same-day conflicting revision returns **AMBIGUOUS** rather than selecting a winner without source evidence.
- When no original support is visible, return **NOT_AVAILABLE**, not a falsified negative.
- Critically, the previously published statement **remains in history**, with its original ID and the exact correcting source ID. Supersession means a new explicitly sourced evaluation of *current support*, not destructive deletion, clinical truth or the date of a biological change.

## 2. Real but bounded RDF graph inference

`ab_bounded_rdf_source_composition.infer` takes a strictly three-stage **explicitly requested source relation**, reuses the proven A/B source-chain witness, then constructs a real rdflib Graph.

Original source events and source identifiers remain connected to the graph. For the separately witnessed `a → b → c` observed event movement, the graph asserts:

```text
a  ab:observedThen  b .
b  ab:observedThen  c .
```

An explicitly declared bounded relation-composition rule computes and inserts the **new actual RDF triple**:

```text
a  ab:observedBefore  c .
```

The test serializes and re-parses the graph, verifies the inferred triple exists and checks its source against a separately coded exhaustive direct-record oracle.

This is **not** OWL 2 propertyChainAxiom compliance, full RDF/OWL entailment, an OWL consistency checker, an unbounded inference engine or evidence that a therapy caused a later effect. The exact Phase 2-style *practice question* is answered by a narrower implemented relation-composition interpretation.

## Honest expected comparison

| Fixed 13-question fictional practice workload | Correct cases |
|---|---:|
| Unchanged original W13 emitted temporal Python | 8/13 |
| Original static snapshot | 6/13 |
| W13 + independent bounded source chain | 11/13 |
| Plus source supersession + bounded RDF composition | *verify in live CI before claiming* |

The evaluation also replays the existing original baseline and 160 source-chain unseen cases, then generates **160 independently verified new source-revision cases** and **160 independent original-source RDF inferencing cases** across the care and surveillance referents. Revision cases must include SUPPORTED, SUPERSEDED, AMBIGUOUS and NOT_AVAILABLE, while RDF cases must include substantial valid and invalid source paths.

Results are based on actual original source behavior and exact synthetic practice gold labels. Scoring 13/13 would **only mean this narrow fixed fictional practice workload is satisfied**. It does *not* prove the official NIH Phase 2 criteria, clinically realistic benchmark success, an external biomedical KG graph, unsatisfiable class/OWL inconsistency detection, scalable performance, superior static KG baselines or eligibility to compete.

## What is preserved

No new universal laws, no forced 48-law model, no original W13 temporal Python change, no rewrite of the existing twelve-job W13 journal, no revised original Phase 1 evidence, no third-party licensing intake or private clinical data. These are bounded **separate capabilities** supporting the existing world.

## Reproduction

```bash
python -m pip install 'rdflib>=7,<8'
python -m unittest -v \
  network.tests.test_nih_phase2_direct_reproduction \
  network.tests.test_nih_phase2_time_respecting_chain_trial \
  network.tests.test_nih_phase2_source_revision_rdf_trial

python -m systems.workspace.nih_phase2_source_revision_rdf_trial \
  --output-dir /tmp/nih-p2-revision-rdf
```

Preserve the actual CI receipt and hash before updating the performance numbers. Future work after the measured failures must test realistic biomedical KG relationships and truly independent external data, graph inconsistency/unsatisfiable-class metrics, a stronger static graph reasoning baseline, scale and robustness, not re-run Phase 1 source provenance.
