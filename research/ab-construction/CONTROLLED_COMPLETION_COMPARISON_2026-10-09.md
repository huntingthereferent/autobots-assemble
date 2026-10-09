# Controlled A/B construction comparison — execution pending

Date: 2026-10-09
Branch: `ab-inverse-construction-math-2026-10-08`
PR: https://github.com/huntingthereferent/language-network/pull/14
Test: `network/tests/test_ab_construction_comparison.py`

## Purpose

Test the original research goal: does adding an evidence-derived construction direction to the **existing** A/B process improve the number of **held-out multi-operation tasks completed**, over simply replaying original witnessed configurations?

**Important comparison boundary:** The control is **evidence-only A/B replay**, NOT an unconstrained human agent, standard software engineer, or every possible ordinary A/B planner. The test therefore measures the value of widening a finite candidate set with an inverse-category recombinator. It cannot prove a global AI capability improvement.

## Common evidence and budget

Each independent domain begins with exactly **four** configurations from its actual native Continuity code, using one initial observed operation:

- Activation registry: `ActivationRegistry.resolve`.
- Repository work ledger: `read_active_work`.

The existing `information_closure` sees the same four first-step observed continuations for both arms. Each returns two tested categories. Both arms are given the **same held-out goal** and **max eight native checks**. Candidate ordering is fixed *before* looking at the held-out goal.

Arms:

- Control: replay only the four original witnessed configurations, up to the cap.
- Construction: replay those same four first, then test up to four **new** configurations from `derive_relation_constructions` (same witness values, sufficient proof-block boundaries, no custom per-domain generator).

Completion is NOT inferred from a candidate being generated. The native two-operation acceptance checks must pass.

## Held-out native API checks

**Activation:** resolve the route, then run `run_activation` with a separately supplied READY task. Accept only if the actual registry selects the target (assignee and required relation match).

**Repository ledger:** parse the fixture, then call `admit_active_work` into a fresh in-memory `HandoffRuntime`. Accept only if one READY handoff is admitted **and** its stored lane and next movement satisfy the goal.

Six cases, predeclared:

| Domain | Goal | Intended comparison |
|---|---|---|
| Activation | target `james`, relation `review` | Only novel witnessed-value recombination can satisfy |
| Activation | target `james`, relation `study` | Already in source evidence; tie expected |
| Activation | target `missing-user`, relation `review` | Required value absent; neither should finish |
| Ledger | lane `Research`, next `Check validation` | Only novel witnessed-value recombination can satisfy |
| Ledger | lane `Research`, next `Compare witnesses` | Already in source evidence; tie expected |
| Ledger | lane `Research`, next `Unwitnessed validation` | Required value absent; neither should finish |

The positive tasks were *chosen to be reachable only by recombination*. They are favorable fixtures, not randomly sampled independent work. The negative and already-solved tasks prevent an unconditional success narrative and show the opportunity cost of widening the candidate set.

Planned test assertions imply a **hypothesized** result of **2/6 control** vs **4/6 construction**, with construction using more native evaluations. **These numbers are NOT yet verified measurements.**

Test also checks source-address conservation, goal blindness of the generator, equal maximum budgets, no live tasks or lineage mutations, and identical results under a four-evaluation budget (construction only reaches its new proposals after its four witnessed sources).

## Execution status / GitHub Actions blocker

The benchmark test and GitHub Actions workflow edits are committed.

A prior focused workflow, **before this benchmark**, passed 67/67 tests:
https://github.com/huntingthereferent/language-network/actions/runs/37890778461

The *new* benchmark workflow **has not executed successfully**, so there is no trustworthy task-completion result yet. The first new focused run
https://github.com/huntingthereferent/language-network/actions/runs/37893065430
reported failure with **no recorded job steps**, and its log download returned `BlobNotFound`. Re-running its failed job again resulted in a failure with **no recorded job steps**. The broad `protocol-tests` run at the same time likewise failed with no steps. This does **not** establish any Python assertion failure or prove the cause of the CI blockage.

Another focused run after improving per-task metrics:
https://github.com/huntingthereferent/language-network/actions/runs/37893348278
also failed without a usable test execution. Do not cite it as test evidence.

When an online runner is available:

```sh
python -m unittest discover -s network/tests -p 'test_ab_construction_comparison.py' -v
```

The aggregate test prints a single `AB_CONSTRUCTION_HELD_OUT_COMPARISON` JSON record including six scenario outcomes, both candidate counts, total successful tasks and native API check counts. Review that actual log before recording any completed-task scores.

## Research boundary

If the experiment eventually passes, its result will establish a narrow improvement: under fixed witnessed candidate inventories, one general A/B inverse operation expands the set of configurations that can be tested and can complete selected held-out API fixture tasks that evidence-only replay cannot. It will **not** demonstrate autonomous end-to-end app building, unrestricted semantic synthesis, native ARC/world construction, or superiority to all traditional A/B planning.

The repository-wide CI also has the existing, separate Online School regressions; do not merge into `main` based on focused checks alone.
