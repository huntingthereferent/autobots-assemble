# NIH Phase 2 — held-out original biomedical graph task, not a made-up positive oracle

## Why this lane

After [PR #285](https://github.com/huntingthereferent/autobots-assemble/pull/285), the finite A/B source-preserving multi-hop operation matched **402/402** original OBO ontology/SPARQL+ queries, recovering longer source relations. But all original OBO facts and test questions were already available when the algorithm was inspected. A **held-out external biomedical task** is a harder next probe, and it must be recorded even if the result is weak.

The source-owner's [PharmKG-8K original graph](https://github.com/biomed-AI/PharmKG) provides **published, separated train/validation/test triples** across genes, drugs, diseases and other entities. Unlike our authored 13-case Phase 2-style trial, selected **test positives are not admitted to the model's source graph**.

## Frozen original source and data split

- Source `biomed-AI/PharmKG`, immutable Git commit `a7daec6b4d6c785c157b8cf693a4651756cb8647`.
- Entire *training* source `data/PharmKG-8k/train.tsv`; read-only source-owner Git blob SHA-1 `9047084dd741eab80499c19a5d11d80143d99906`.
- Entire *test* source `data/PharmKG-8k/test.tsv`; Git blob SHA-1 `6f842d19d8fd49017335ac71e2e7e9479ed75595`.
- Entire *validation* source `data/PharmKG-8k/valid.tsv`; Git blob SHA-1 `1f82ceb4ac678581401ead95f8a000d975bc0288`. Validation data is authenticated but **not fed into reasoning**.
- Source-owner train/test/valid blobs are read-only and never redistributed or absorbed under A/B's All Rights Reserved license. Only SHA-256 digests and derived evaluation metrics are retained.

Before benchmark execution, the relation codes `GG`, `T`, `P`, and `I` were preselected, with **16 deterministic SHA-256-ranked held-out positive triples per relation**. These are 64 externally authored positive questions, not chosen based on successful predictions. The seed `26022` controls eight distinct relation-compatible **unlabeled alternative tails** per question, excluding the original published training and test positive edges. The alternative tails are not confirmed true negatives; their status remains *unknown*. Choosing the alternatives after reading test positives is a filtering convention, and that is separately stated.

## Executable A/B source paths vs strong static baseline

The A/B operation reads **only original training edges**, preserving directed `head,relation,tail` and original source-edge SHA-256. For each held-out positive and each alternative, it tests whether **a separate two- or three-hop training-graph source path with exactly the declared relation code** exists, preserving intermediate original entities.

The independent **static graph reasoner** uses a separately written breadth-first search over the **full relation-specific original training graph**, up to three hops. Both algorithms must agree on shortest path length, not just whether any path exists. Every positive A/B source witness is independently checked against the original training set, with exact original source-edge hashes.

This is a deliberately **equal-strength static baseline**. A/B should **not** claim a temporal advantage over the same graph under the same untimed conditions. In fact, the test asserts that A/B and the full-training-graph static reasoner return equal Hits@1 on the benchmark. There is no genuine temporal sequence in PharmKG's supplied split.

Metrics: held-out positive alternative-path coverage, mean tie-aware rank among nine candidate tails, Hits@1, Hits@3, mean reciprocal rank and corresponding static Hits@1. All case-level results are preserved. A network path is a source-connectivity observation, **not proof of an unobserved biomedical fact** such as a treatment recommendation or therapy effectiveness.

## Important negative conclusions must survive

- The published split is **not chronological**. Train/test partition must not be interpreted as historic `known_at` or clinical `valid_at`.
- A positive original test edge is real source evidence, but if the model sees it, **the evaluation leaks**; the operation must use training only.
- Corrupted/unlabeled alternative endpoints are **not confirmed false**. Hits@1 and MRR are only **filtered held-out-link ranking proxies**, not externally certified biomedical diagnostic accuracy or actual true-negative specificity.
- Same-relation path reachability cannot entail a new direct treatment/disease association without a separately justified biomedical reasoning rule.
- A/B's original W13 native journal, temporal emitted Python, current WORLD lanes and licensing remain unchanged.
- This cannot be described as official NIH Phase 2 benchmark performance, temporal event-validity evidence, clinical decision-making ability, or eligibility.

## Run original source benchmark

```bash
python -m unittest -v network.tests.test_nih_p2_external_pharmkg_heldout_trial

python -m systems.workspace.nih_p2_external_pharmkg_heldout_trial \
 --train /original/train.tsv --test /original/test.tsv \
 --valid /original/valid.tsv \
 --output /tmp/nih-p2-pharmkg-heldout.json
```

The dedicated GitHub Action retrieves all three immutable published source files, verifies exact Git blob hash identities, runs the **independent held-out** evaluation and retains only derived results. Do not invent or hardcode the scores before CI.

### What to do with the actual failures

If held-out link ranking is weak, that is valuable falsification: relationship traversal on original biomedical ontology hierarchies **does not by itself establish general biomedical knowledge inference**. Need typed heterogeneous multirelation query semantics, actual longitudinal event/time data, held-out real time-stamped gold and external static graph baselines, then OWL satisfiability and scalable KG metrics. **Do not return to Phase 1 source-history loops just to collect dates.**


## Observed actual original held-out result — October 20, 2026

The [original-source GitHub run #39476489005](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39476489005) succeeded **7/7 focused admission and source-leakage checks**. All source TSV bytes were independently authenticated against source-owner pinned original Git blob SHA-1; no original TSV bodies were retained. [Derived task-by-task artifact #12289721506](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39476489005/artifacts/12289721506), archive SHA-256 `012d30b3d979627ca148a307d37b56ff9e5699e3687e4e5a5f980ada81b76454`.

**Original entire published data:** training **400,788 physical rows (386,768 unique; 14,020 duplicates)**, test **50,036 physical rows (49,771 unique; 265 duplicates)**, validation **49,536 physical rows (49,267 unique; 269 duplicates)**. The original file bytes are unchanged, and source duplicates are counted separately rather than being silently discarded. The source README's test/validation count labels do not match the actual named files; exact immutable files and file names take priority over the README table.

| Original source relation code | Held-out positive questions | Questions with alternate same-relation source path | Mean filtered rank of source-positive target |
| --- | ---: | ---: | ---: |
| `GG` | 16 | **15** | 1.7500 |
| `I` | 16 | **8** | 3.3125 |
| `P` | 16 | **0** | 5.0000 |
| `T` | 16 | **0** | 5.0000 |

**All 64 actual fixed held-out original biomedical link questions:** A/B same-relation source paths **Hits@1 = 13/64**, **Hits@3 = 23/64**, tie-aware **MRR = 0.410417** on **nine candidates each** (one original test-positive plus eight *unlabeled* alternative tails). Independent full-training-graph static shortest-path ranker produced **Hits@1 = 13/64**, exactly matching A/B; **zero source-path existence/length disagreements across 576 candidates**. This is no quantified static-KG advantage, so no NIH Phase 2 correctness claim.

The score is a *small filtered link-ranking proxy*, **not directly comparable** to PharmKG's originally published MRR/Hits@K over its own evaluation protocol or to a real biomedical clinical performance metric. We did not train the original authors' embedding models. Source-owner `data/preprocess.py` explicitly uses `sklearn.model_selection.train_test_split(random_state=2020)`, not source event timestamps; therefore the published held-out split **cannot** establish historical `known_at`/clinical `valid_at`. Alternative candidate tails were only filtered to avoid original known positives; they are not verified negatives.

### Capability boundary that directly follows from this evidence

The current **same-relation** 2-3-hop A/B query has a source-preserving path witness, but it fails to find an alternate path for any of the **32 held-out `P`/`T`** cases. This exposes the limitation of assuming that biomedical inference repeats the same predicate along every hop. The next substantive investigation should derive *explicit heterogeneous relation composition* from **training-only, independently justified biomedical metapath schemas**, then freeze those schemas **before** scoring a separate held-out test partition. Never deduce a clinical recommendation from mere graph connectivity, tune a rule using held-out labels without keeping a fresh holdout, or claim improved temporal performance absent actual source event times.

Original W13 journal/executable, World48 and A/B ownership remain unchanged. PR remains draft; full repository-wide CI is separate from the successful focused run.
