# Continuity A/B construction — real in-process subsystem check

Date: 2026-10-09  
Scope: existing repository APIs, isolated local fixtures, GitHub Actions  
Stage: **measured in-process API behavior; not a native ARC or live-world claim**

## Question

Can the **same source-derived inverse A/B constructor** propose new relational combinations in real, *different* Continuity subsystems, with no domain-specific constructor, and does ordinary A/B identify when a longer continuation separates a prior category?

This advances the original agent-construction objective. It is **not** a test of autonomous software implementation or independent deployment.

## Method

The same `runtime.ab_relation_generator.derive_relation_constructions()` function is used twice, without a custom generator.

For each domain:

1. Collect four occurrences from real one-step API returns using an isolated fixture.
2. Run the original `runtime.ab_information.information_closure()`; each domain has two initial continuation categories.
3. Invert and recombine source *relation values only within a sufficient proof block*, withholding already witnessed tuples.
4. Preserve source locators, witness contract, tested horizon and PROPOSED status.
5. Send all new proposals through the actual API, with a separately evaluated second operation.
6. Run the same A/B closure again on the longer returned continuations.

No actual user's tasks, calendar, repo work ledger, or agent lineage were written. The work-ledger and handoff probes use disposable temporary inputs or in-memory runtimes. Source locators are locally generated fixture hashes; they are **not independent external attestations**.

## Two native software interfaces

| Interface | First native return | New source-derived proposals | Second operation | Observed result |
| --- | --- | ---: | --- | --- |
| `runtime.repository_tasks.read_active_work` | Is a row currently active (`MOVE`) or not (`FROZEN`)? | 4 | `admit_active_work` into isolated `HandoffRuntime` | All four preserve first-category behavior. Active work admits one isolated handoff; frozen work admits none |
| `runtime.activation.ActivationRegistry.resolve` | Does the registered actor+surface resolve? | 4 | `run_activation` against one fixed READY test handoff | All four preserve first-category behavior; crossed selectors correctly select no work |

### Horizon-dependent correction on real activation code

For the **observed originals plus new proposals**, the one-step route-resolution projection has two categories:

- Actor+surface cannot resolve.
- Actor+surface resolves (selector values are invisible to `resolve`).

The two-step projection additionally invokes `run_activation`, which checks selectors. There are **three** categories:

- Not resolved: `(0,0)`.
- Resolved and selected: `(1,1)`.
- Resolved but selector mismatch: `(1,0)`.

Thus a first-step equivalence breaks under another *actual repository operation*. The existing A/B closure returns three classes, and its sufficient proof must retain a selector relation to represent the continuation. The generator did **not** learn those selector semantics on its own: it proposed novel combinations; the existing registry's code supplied the decisive evidence.

### Preservation/negative checks

- No proposal crossed a first-step A/B proof category.
- No proposal replicated the original full relation tuple.
- Every proposed relation value and its locator came from an observed source in the same proof block.
- Proposed candidates were not passed to the native A/B movement evaluator as new witnesses.
- Isolated work admission never touched the actual GitHub ledger, persisted service data, or task queue.
- Existing ARC negative control remains: finite phase-history evidence with a single varying field yields no unjustified spatial/world construction.

## Reproduction

GitHub branch: `ab-inverse-construction-math-2026-10-08`

```sh
python -m unittest discover -s network/tests -p 'test_ab_native_subsystems.py' -v
```

The full focused GitHub Actions workflow additionally runs generic construction, synthetic world, existing information-closure, and recursive-loop tests. Last directly observed run: [inverse-ab-construction #33](https://github.com/huntingthereferent/language-network/actions/runs/37890778461), **67/67 tests passed**.

## Limits / next boundary

1. This demonstrates transfer of the **proposal operation**, not transferred semantic understanding or a general ability to finish tasks.
2. Both subsystem tests run isolated instances of real code. They do not validate interaction with live external accounts, actual GitHub task boards, production authorization, or native ARC game state.
3. First-stage class preservation is limited to its specified tested action and horizon. The activation example deliberately proves that subsequent operations can reveal new distinctions.
4. No generic engine for unknown actions was invented. A/B must use a real observer for those actions or leave the boundary unresolved.
5. Generic recombination does not itself improve end-to-end build quality. That requires independently specified tasks, baselines, execution costs and held-out acceptance checks.
6. The broad repository CI has separate Online School regressions and must not be described as green.

**Result:** One construction primitive can propose new relational candidates for two real, unlike Continuity APIs; actual second-step behavior can correct the original quotient. The agent remains witness-gated.
