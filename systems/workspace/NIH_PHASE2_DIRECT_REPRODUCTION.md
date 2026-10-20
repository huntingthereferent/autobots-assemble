# NIH Phase 2 — direct reproduction test of existing W13, not another Phase 1 intake

## What exactly are we trying to reproduce?

The [official NIH "It's About Time" Challenge](https://www.nih.gov/challenges/its-about-time-temporal-reasoning-biomedical-knowledge-graphs-challenge) says Phase 2 is about a **working temporal biomedical KG prototype**, time-respecting inference and longitudinal reasoning, a measured static-KG comparison, and reusable artifacts:

| NIH Phase 2 criterion | Official weight |
| --- | ---: |
| Demonstrated temporal reasoning on realistic biomedical data | 30% |
| Correctness of temporal inference | 30% |
| Evaluation rigor vs static KG | 20% |
| Extensibility beyond the primary use case | 20% |

The official evaluation-rigor criterion specifically names logical inconsistencies/unsatisfiable classes, amount of data/triples, relationship richness, attribute richness, class/property instantiation ratio, and interlinking completeness. The **official NIH shared task/test data may be provided later at NIH's discretion**; this experiment is our self-supplied **practice reproduction suite**, not the official shared benchmark or an NIH submission.

## Actual source under test

The **unchanged original** `systems/workspace/nih_prototype_worker_source/prototype_worker.py:ENGINE` that powers W13/NIH's existing emitted `temporal_query.py` runs as a distinct **real Python subprocess** for every case. The same program is used for the care/guideline/evidence and surveillance scenarios. Its answers are checked against an independently implemented factual-selection oracle. A real `game_construction` movement is also replayed separately; this must **not** be mistaken for a biomedical reasoning inference.

No builder is rewritten, no false inferences are patched into its JSON, and no previous W13 journal is touched.

## Direct Phase 2-style questions

The dataset comprises **fictional population-level** biomedical trajectories and revised scientific statements, not patient data or real-world claims:

- A care sequence: therapy alpha, observed inadequate response, then therapy beta. Can the system **infer a longitudinal switch** rather than just retrieve the snapshot fact of beta?
- A guideline change: can it retrieve the correct recommendation at each validity interval and avoid revealing future revisions too soon?
- A published claim later retracted: can it distinguish **a visible earlier claim** from **a currently supported claim** after a correction?
- Time-respecting paths: can it reject an inference before evidence exists, or incorrectly backdated to before the later intervention?
- A second domain (surveillance): does its original executable correctly apply the same temporal filter to another biomedical topic?
- RDF graph/ontology: can the **native temporal executable** emit or entail graph relationships and evaluate all required structural and logical metrics?

Thirteen independently declared true/false practice answers are checked from actual emitted Python output. A missing inference field is scored **FAIL**, never converted to a successful absence-of-path. This is important for negative tasks: a solver that cannot infer any path cannot claim to correctly reject an invalid one either.

## Static control and graph metrics

The comparator is explicitly the **same original executable's** `static_snapshot_ids`, which ignores `known_at` but uses the same `valid_at`. This does not stand in for the strongest possible static KG.

The separate **evaluation harness** constructs RDF source-statement triples and measures five explicitly defined structural proxies:
`number_of_triples`; object-predicate share of non-type predicates; literal attributes per statement; `rdf:type` assertions / non-type triples; fraction of source statement subjects with URI object links. These are declared operational proxy formulas, **not NIH-certified metric implementations**. Graph serialization and structural profiling belong to the harness, **not to the original emitted W13 temporal Python**.

**Unsatisfiable OWL classes / logical inconsistency are `NOT_MEASURED_NO_OWL_REASONER`.** Do not print zero when the system contains no reasoner.

## An honest PASS means the test ran, not that W13 passed every requirement

The executable's known-time + validity-time **fact selection** should pass some temporal tasks and prevent future evidence leakage. The same unchanged executable is not expected to satisfy full Phase 2 because it currently has no:
- longitudinal path inference over a series of events;
- correction/retraction semantics for evidence supersession;
- OWL/RDF property-chain entailment integrated into temporal query execution;
- inferred uncertainty intervals for unknown source public availability;
- end-to-end six NIH KG metrics, including unsatisfiable class detection.

These are **failures observed against the Phase 2-style functional questions**, not excuses to launch more original-source archive downloads.

## Run directly

```sh
python -m pip install 'rdflib>=7,<8'
python -m unittest -v network.tests.test_nih_phase2_direct_reproduction
python -m systems.workspace.nih_phase2_direct_reproduction \
  --output-dir /tmp/nih-phase2-direct
```

The dedicated GitHub Actions runner must execute the actual emitted original W13 program for all cases and upload its task-by-task actual native outputs and hashes.

**Next movement determined by failures:** extend the **smallest reusable A/B relationship operation** to cover a longitudinal time-respecting path and independently verify it against this unchanged gold suite, without silently mutating the original W13 and without adding 48 universal laws. Then support revision/supersession, connect RDF inference and eventually test actual biomedical datasets and a stronger static KG baseline. Keep the NIH official eligibility and later shared-benchmark boundary independent.
