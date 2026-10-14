# Conflict-guided policy benchmark — October 12, 2026

## Referent

Keep the current mathematical chatbot and evaluate whether using **replayed rejected transitions to prioritize the next seed** improves finite goal completion, admissible edges, or observation cost compared with the existing fixed candidate order. These are **two declared policies over one scoped finite mathematical test family**; they are not a general A/B definition, new engine, external source verification or physical movement proof.

## Result

**KEEP_FIXED_DEFAULT.** Conflict guidance remains an opt-in research policy. It is not supported as a better default by this declared benchmark.

Six deliberately specified old-law/new-law/goal pairs, each with fixed and guided policies at trial caps **2, 3, and 4**: 18 paired comparisons / 36 fully completed executions. Both policies use the same law pair, roots, candidate generation parameters, source observer limit of **54 possible A/B edges per owner**, and a common **completed-trial cap**. Each policy gets a fresh independent local snapshot, so actual observed edges are counted independently. Those actual observations need not be equal.

| Criterion | Guided wins | Fixed wins | Ties |
|---|---:|---:|---:|
| Goals completed | 0 | 0 | 18 |
| Admitted edges in selected completed trial | 0 | 1 | 17 |
| Fewer original+changed transition observations | 0 | 2 | 16 |

Across these 18 paired runs, cumulative observed transitions were **1,422 (fixed)** versus **1,426 (guided)**. This is the sum of per-run unique cached observation counts, not the count of globally distinct transitions across independent runs. Guidance actually attempted witness-selected next seeds in **12** of 18 runs; its behavior was not simply a no-op in every test.

### Concrete negative controls

- Old phi=(0,0,1), changed phi=(1,0,1), goals (0,1,0) and (0,1,1), trial cap 4: fixed retains **42** admitted edges, guided **41**, and both carry 2/2 goals. Both queried all 54 possible edges in each owner snapshot.
- Old phi=(0,0,1), changed phi=(0,0,0), goals (0,1,1) and (0,2,0), caps 3 and 4: each policy carries 2/2 goals with 13 admitted edges. Fixed observes **26+18=44** transitions, guided **28+18=46**. Selected goal words and selected seed words are identical in this case; guidance incurred additional observations on other trials.
- All other comparisons tie for these evaluated metrics. A tie is not evidence of beneficial guidance.

## Verification

The benchmark instrument independently replays each selected goal action word and **every admitted edge** against the finite transformation laws, checking each paired state and injective mapping. Observations are counted separately from completed trials; every paired comparison verifies matching completed trial caps. Each case preserves the source law, changed law, goals, selected words, completion state, admitted/excluded counts, tested candidate limits and observation counts.

Completed test modules run as separate local processes (not one merged run):

| Module | Tests passed |
|---|---:|
| `test_ab_chatbot_policy_benchmark.py` (new) | 4 |
| `test_ab_chatbot_conflict_guided.py` | 10 |
| `test_ab_chatbot_post_extension_portfolio.py` | 25 |
| `test_ab_chatbot_seed_first_extension.py` | 12 |
| `test_ab_chatbot_union_extension.py` | 15 |
| `test_finite_conflict_guidance.py` | 4 |
| **Total completed and passing** | **70** |

Earlier one-process full benchmark and grouped regression commands exceeded their execution windows; they were not counted. Budget segments **2, 3, 4** and the focused modules completed separately. The full historical chatbot suite and GitHub CI have **not** been rerun/verified during this continuation.

## Reproduction

Unzip the complete local archive to a directory, then in that directory run these commands **in separate processes**:

```bash
python ab_chatbot_policy_benchmark.py --budget 2
python ab_chatbot_policy_benchmark.py --budget 3
python ab_chatbot_policy_benchmark.py --budget 4
python ab_chatbot_policy_benchmark.py --aggregate
python -m unittest -q test_ab_chatbot_policy_benchmark.py
```

Input package immediately before this change: `ab_chatbot_conflict_guided_2026-10-12.zip`, SHA-256 `dd353e2e39025c1474b9712be3a2378a9f50babdf97d39979ad3ee0a98ed0072`, 91 original ZIP entries. The new archive preserves those original members byte-for-byte. `BENCH_BUDGET_*.json` contains each separate completed run; `POLICY_BENCHMARK_RESULTS.json` combines them and records the machine-readable decision. The benchmark code is new and does not change the old agent's behavior.

## Wall and next

The sample is a **declared nonrandom selection** of finite transformation laws/goals; it is not exhaustive across all laws or policies. Neither global dominance nor universal no-improvement follows from it. Guided trial ordering may still help on untested cases. An observation budget counts distinct owner transitions, not CPU time or physical sensing cost.

Next supported movement: retain fixed-order selection by default, use exclusions as research evidence, and test whether avoiding demonstrably incompatible seeds *before* committing observations improves a new collection of held-out finite goals without increasing cost. Any claimed improvement needs equal budgets and fresh independent replay. The separate Continuity project's default repository pointer should not be changed.
