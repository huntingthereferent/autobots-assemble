# Solve the Whole Thing — Hard-Case Ledger

This file is not a solver architecture.

It is a compact list of concrete ways already-solved ARC3 games defeated otherwise reasonable solving strategies.

## Current hard cases

### BP35 — missing procedure

A strong local mechanic model still failed late.

Failure form:

```text
I know what the pieces do
→ therefore I know how to win
```

False.

### LF52 — insufficient horizon

The successful public solve required preserving notes, building a proven level copy, then searching it offline at scale.

Failure form:

```text
my model is good
→ local planning should be enough
```

False.

### RE86 — proxy is not reward

Search found states that scored as deeper/better but did not trigger the specific level-up.

Failure form:

```text
progress proxy improves
→ I am approaching the real objective
```

Not necessarily.

### WA30 — the world acts too

Boxes must be pushed while autonomous helper/antagonist bots evolve on every step.

Failure form:

```text
this action improves the board I see
→ therefore the future board is improved
```

False when environment actors respond.

### DC22 — incomplete-model impossibility

An exhaustive search/proof within a learned model concluded the goal was unreachable. A later clean source-free run solved the game.

Failure form:

```text
my model has no solution
→ the game has no solution
```

False unless model completeness is independently established.

### G50T — past-you is part of the plan

A recorded path is replayed by a ghost so the ghost can hold a switch while the fresh player continues.

Failure form:

```text
map current reachable states
→ therefore I have represented the important planning state
```

False when the solver must deliberately construct a future helper from its own past trajectory.

### SB26 — the interface is not the task

Near-perfect transition models and good controllability still did not solve the game. The latent problem is program synthesis over subroutine slots and a target flattened color sequence.

Failure form:

```text
I can predict every click
→ therefore I have represented the problem correctly
```

False when the task lives in a different symbolic/compositional representation than the visible interaction dynamics.

### SK48 — one framing is insufficient

The solve simultaneously has spatial Sokoban-like constraints and a covered-color sequence objective. Earlier attempts were described as plateauing from one framing.

Failure form:

```text
I found the right representation
→ therefore I can discard the others
```

False when independent spatial and symbolic constraints must remain satisfied together.

### SP80 — pixels can omit causal history

The win depends on an accumulated ACTION5 interaction condition after a move sequence.

Failure form:

```text
same-looking current frame
→ same task state
```

False when earlier interactions create latent accumulated state that is not fully visible in the endpoint image.

## Practical use

When live solving resumes, this ledger is a diagnostic.

If a level stalls, ask which failure form fits the evidence before changing tools.

The ledger does not prescribe one universal algorithm and does not modify A/B.
