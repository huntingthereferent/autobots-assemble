# NIH Phase 2 — training-frozen heterogeneous source relationships, genuinely new heldout questions

The [first original PharmKG heldout probe #288](https://github.com/huntingthereferent/autobots-assemble/pull/288) used the published original train/test split, with 64 source-positive questions: same-relation path-proxy Hits@1 **13/64**, Hits@3 **23/64**, filtered MRR **0.410417**, **zero** disagreement with an equally capable static graph reasoner. The source-positive `P` and `T` questions had no same-predicate path alternatives. The published split is **random**, not chronological.

This branch tests **whether training-observed mixed relation-code paths carry additional structural signal** on a *different*, untouched heldout subset. It does not equate mixed graph paths with biomedical conclusions.

## Frozen design before heldout scoring

1. Re-fetch original complete source-owner `biomed-AI/PharmKG` train/test/valid files from the same immutable commit and authenticate all three Git blob identities. Exact source file bytes and duplicate counts are retained as metadata; source bodies never shipped with A/B.
2. **Only original deduplicated TRAIN rows** form the source graph for pattern learning. For each of four already declared target relation codes (`GG`, `T`, `P`, `I`), select 64 training examples using a frozen SHA-256 ordering with salt `AB-P2-pharmkg-train-calibration-26023`.
3. From those *training-only* original head/tail pairs, enumerate real **two-edge graph paths whose two predicates differ** (`head --r1--> middle --r2--> tail`, `r1 != r2`). Avoid a path using the target direct edge by disallowing intermediate source/target self-node. Freeze the **three most frequently witnessed** ordered relation-code pairs per target code. These are structural *candidate patterns*, NOT medical implications or valid OWL relation composition. Retain training support counts and calibration-source SHA-256 in the source receipt.
4. Only **after freezing patterns**, select 16 **new original heldout positives per target code** with a different SHA salt `AB-P2-pharmkg-untouched-test-26023`, excluding *all* 64 prior #288 scored triples, plus any training triple. Use eight predeclared, relation-compatible **unlabeled** alternative tails per test-positive question; exclude published positives and training direct edges. Alternatives are **not verified false**.
5. Evaluate **all 64×9** new candidate queries on the training-only source graph: bounded A/B original exact-edge heterogeneous witness; separately implemented independent static graph query under the **same frozen patterns**; the unchanged prior same-relation 2–3-hop algorithm; and an **untyped** independent static two-hop comparator. Every A/B positive reports both original training edges, intermediate source node and exact SHA-256 fingerprints. Reject source-witness fabrication or A/B/static frozen-pattern disagreements.
6. Report tie-aware Hits@1, Hits@3, MRR and per-relation path coverage for **each** method, including weak/no results. Retain all original case-level scores, not just aggregate success.

## What a result means

The equal-strength static graph reasoner **should match** the A/B operation when supplied the exact same training graph and frozen relation patterns. We do not claim A/B wins against an identical static computation. We are testing whether **relating distinct source predicates**, not simply extending same-predicate paths, provides a meaningful **held-out structural signal** on data the operation didn't use to select the rules.

The patterns were learned from original TRAIN graph connectivity, but source relation codes alone cannot justify a new direct biomedical fact: neither an apparent metapath nor a network similarity is a proven treatment indication, disease mechanism or clinical event time. Source-owner `preprocess.py` uses random train/test partitions; no original biological event timestamp, bitemporal evaluation or NIH shared data is provided. Scores use only a small filtered nine-candidate ranking proxy, **not the author's original full-ranking protocol**, and comparisons to their published embedding results would be invalid.

The original W13 emitted temporal Python, 12-job native journal, World48 math and A/B license remain untouched. This draft stacks on #288 for an independent audit of learning and evaluation selection.

## Follow the actual evidence

A stronger mixed-predicate result would motivate **external semantic typing, constraints and independently justified biomedical relation composition** before any biomedical claims. A weak result would falsify the idea that blindly chaining different predicates is enough. Either way, **genuine temporal Phase 2 remains a separate test** requiring real event timestamps, temporal gold, OWL satisfiability and appropriately strong static-KG controls.

Run via `.github/workflows/nih-p2-pharmkg-frozen-heterogeneous.yml`; no performance numbers should be claimed until its actual original-source CI finishes.


## Actual unchanged heldout experiment — October 20, 2026

**Dedicated original-source focused verification passed 8/8 tests** on [GitHub Actions #39478639842](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39478639842). Immutable source-owner train/test/valid Git blob hashes were rechecked. All rules were selected **only from original TRAIN calibration triples**, then **64 entirely new source-owner TEST positives** were selected by the frozen new SHA salt, excluding the previous 64 questions from PR #288. New positive targets were never added to the training source graph.

[Actual source-by-source derived artifact #12291380906](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39478639842/artifacts/12291380906); ZIP SHA-256 `b656c24905411573931127a94b0c18809fd97b503f39828f4705a7fc9fff0189`. Every positive A/B two-edge witness was checked against original training triples and source SHA256s; the separately implemented equal-strength static reasoner agreed exactly.

| Same **new 64-question** heldout selection | Mixed-predicate A/B paths | Previous same-predicate A/B paths | Static untyped two-hop |
| --- | ---: | ---: | ---: |
| Hits@1 | **6/64** | **8/64** | 1/64 |
| Hits@3 | **30/64** | **19/64** | 25/64 |
| Tie-aware MRR | **0.380434** | **0.361531** | 0.313991 |
| Mean filtered rank (lower is better) | **3.539062** | **4.046875** | 3.773438 |

The equally capable *independent static mixed-pattern reasoner* matched A/B identically at **6/64 Hits@1, 30/64 Hits@3 and MRR 0.380434**, with **zero** source-witness/rank disagreements. **No static-KG advantage is claimed.**

| Target relation-code | New heldout positives with original mixed-relation source witness | Mixed-path Hits@1 | Previous same-predicate Hits@1 |
| --- | ---: | ---: | ---: |
| `GG` | 8/16 | 3/16 | 6/16 |
| `I` | 1/16 | 1/16 | 2/16 |
| `P` | **15/16** | 2/16 | 0/16 |
| `T` | **14/16** | **0/16** | 0/16 |

This **does not confirm biomedical reasoning success**. Training-only heterogeneous code patterns offer more opportunities to witness an alternative route for `P`/`T`, but many alternative tails are reachable too: the mixed-predicate operation **lost two first-place rankings** even while increasing top-three rankings by eleven. The source relation codes have not been independently justified as biological entailment operators, and the alternatives are unverified negatives. Prior #288's score must not be directly compared with this new holdout selection; the preceding method was **re-evaluated on this same new selection** for the paired comparison above.

The measured next limitation is **selectivity and semantic grounding**, not simply path existence or number of hops. A scientifically legitimate follow-up requires source-provided biomedical relation meanings/type constraints and held-out external evaluation that can falsify proposed relation rules. Training-only pattern frequency is not evidence that one relation implies another. No real event timestamps exist in this split, so this cannot demonstrate the official NIH Phase 2 temporal benchmark. Broad `protocol-tests` remains a separate CI check; this is an unmerged draft.
