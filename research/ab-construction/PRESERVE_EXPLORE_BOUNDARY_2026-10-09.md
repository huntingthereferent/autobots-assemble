# Preserve vs explore — A/B construction-direction boundary

**Date:** 2026-10-09  
**PR:** https://github.com/huntingthereferent/language-network/pull/14  
**Stage:** committed implementation; current GitHub test execution **blocked**, not verified.

## Question

Must a construction operator preserve the tested continuation category of
its source? **No**: that is necessary when promising preservation, but not
when **proposing a new structure for independent testing**.

The agent remains a **single A/B system**. Construction is opt-in; the
forward information closure and native movement evaluator remain intact.

### Existing `preserve` mode (unchanged default)

- Use the evidence-sufficient proof blocks established by the forward A/B.
- Recombine only witnessed relation values inside that block.
- Preserve source history, horizon and tested continuation category.
- Output `PROPOSED`, never automatically native MOVE.
- May return nothing if there is no novel compatible within-block tuple.

### Explicit `explore` mode (new)

- Enumerate only source-observed relation names and values, bounded.
- Exclude witnessed tuples and combinations already possible within a
  single prior continuation fiber: genuinely cross-category candidates only.
- Retain independent source indices and locators for every component,
  and list which prior categories supplied the components.
- Set `ConstructionProposal.category = None`, with explicit
  `prior_continuation_category = UNASSIGNED`.
- Preserve deterministic candidate hashes and reject frame tampering.
- Never inherit a tested old continuation or claim that mixing works.
- Return the same existing `ABFrame` type for separate evaluation.

No new agent scheduler, native observer, implementation engine or
external access privileges are created.

## Reachable operation

```python
preserve = service.propose_ab_constructions(
    occurrences=occurrences, state=state,
    source_locators=locators, witness_contract=contract,
    horizon=1, intent="construct", mode="preserve",
)
explore = service.propose_ab_constructions(
    occurrences=occurrences, state=state,
    source_locators=locators, witness_contract=contract,
    horizon=1, intent="construct", mode="explore",
)
```

Both are read-only; a generated proposal is not task completion.

## Falsifying controlled native-code fixture

The existing `ActivationRegistry` witnesses initially correlate
`route_actor` with `selector_assignee`, while `selector_relation`
varies inside each category. From the same four source tuples:

- Preserve-mode test expects **0** novel candidates.
- Explore-mode test expects **4** unassigned cross-category candidates.
- A proposed `tester / other / review` tuple can be passed through
  real `ActivationRegistry.resolve` and `run_activation` logic
  against a fixed **isolated READY fixture** for `other / review`.
- The original four source tuples cannot select that fixed target.

This is a *designed test expectation*, **not a verified run result**.
The independent native API determines the actual continuation if the
runner eventually executes the test. The exploration routine does not
know or enforce the activation semantics; it only proposes mixtures.

## Test additions

`network/tests/test_ab_exploratory_construction.py` exercises:
- two modes from one forward A/B state;
- no inherited category or prediction;
- original witness provenance and content-hash validation;
- actual native registry holdout behavior;
- service read-only invariants and no agent/task birth;
- missing source, invalid mode and invalid intent rejection;
- deterministic bounded generation;
- non-repeatable/missing mechanics are never promoted as native;
- simulation retains the category-unassigned label.

`network/tests/test_ab_construction_comparison.py` also now asserts
that this exploration mode recovers the previously documented
cross-category blind Cartesian counterexample **only when a native
holdout accepts the resulting proposal**. Neither the generator nor
the A/B quotient itself counts as completion.

## CI status

The earlier **67/67 focused tests** passed at
https://github.com/huntingthereferent/language-network/actions/runs/37890778461.

The present new tests have **NOT** executed on an assigned GitHub runner.
Jobs for the focused workflow and the broad protocol workflow are
reported as failure with `runner_id=0` / `steps=[]` in Github metadata.
GitHub has not provided an accessible job log; root cause unknown.

Tracked at https://github.com/huntingthereferent/language-network/issues/15 .
Do not claim passing results for the new mode, do not merge/deploy.

## What this establishes when verified

The mathematical distinction is between
`preserve(Q_W)` (hypotheses retaining source-category commitments) and
`explore(Q_W)` (new-category-unassigned hypotheses crossing the source
partition). The same original A/B evaluator decides what actually
survives after independent testing.

It is **not** evidence of improved autonomous coding or universal
construction; comparative held-out end-to-end completion remains open.
