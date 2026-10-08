# Opt-in recursive agent lineage (local proposal)

This is an **additive orchestration adapter** on top of the existing `runtime` handoff/event contract. It does not replace A/B mathematics, the `SwallowFirstBoundary`, the generic `Orchestrator`, or activation projections.

## Movement

```text
explicit registered activation + actor + instance ID
    -> one agent handoff (generation 1)
    -> caller-supplied A/B evaluation + movement witness
    -> resulting output enters next handoff (generation 2)
    -> next caller-supplied evaluation (generation 3)
    -> admitted descendant closure of an earlier ancestor
    -> if closure exposes a distinct admitted referent, another agent is born
    -> repeat while there is witnessed movement; otherwise stop/open wall
```

The agent's *execution* and the agent's *loop closure* are deliberately separate. An agent may be `COMPLETE` (its own result is witnessed) while its loop is `OPEN` until a later descendant closes it. `AGENT_LOOP_CLOSED` is an append-only event on the ancestor's handoff; it does not rewrite that ancestor's result. The descendant, admitting evidence, and event ancestry remain visible.

## Contracts

- A route with `projection='agent_lineage'` is required. Existing `ohayo` / task/day activation routes remain read-only. **This adapter is not wired into HTTP activation or front-page actions.**
- `instance_id` is supplied by the activation caller, stable for retry/replay; an identical activation instance does not create a duplicate root.
- `evaluate(handoff, state) -> AgentMove` is a **caller-supplied A/B comparison/admission**. This module does not implement or attest to A/B mathematics.
- Each `COMPLETE` requires a valid `movement witness` under the existing evidence contract, and this is validated **before** marking the handoff started.
- `closes=(ancestor_id,)` is only a *claim*. A separate, explicit `closure_evidence` plus an injected `admit_closure(descendant, ancestor, evidence)` must accept it. Without either, the ancestor remains `OPEN`.
- Closure only applies to genuine ancestors in this lineage. Neither self-closure nor cross-lineage closure is allowed.
- `closure_birth_referent` may spawn new work **only when a closure is admitted**. A closure does not inherently imply another task.
- `BLOCKED` and `UNKNOWN` are preserved; an optional same-runtime `SwallowFirstBoundary` may be provided. No unresolved wall is converted to `COMPLETE` merely to create an agent.
- Each child retains parent output, source witness locators and provenance, and parent-complete dependency via the existing `spawn()` function. No source content is copied into a universal database.
- Duplicates are suppressed by stable child IDs and repeated-input detection; `max_births` and `max_steps` bound the run.
- A saved completed result can be reconciled after a crash to finish closure/birth, without re-running its evaluator. This depends on an actual durable `RuntimeJournal` being supplied by the caller.

## Current scope

The example is simulated and only demonstrates **structural feasibility**. There is no automatic external tool access, real autonomous agent process, live A/B comparator, network-wide agent scheduling, or proven closure of research claims. Actual wiring into the website/activation HTTP route and a real A/B comparator are separate integration work, and should be tested against full repository CI after applying this proposal.

Run focused tests after applying the files to the repository:

```bash
python -m unittest network.tests.test_agent_lineage -v
python -m runtime.examples.agent_lineage_demo
```

The repository's existing `activations/registry.json` is intentionally unchanged. To use this new route in a real environment, register a compatible route explicitly and invoke `AgentLineage.activate()` from an authorized entry point.
