# Protocol — Activation Route

## Referent

A registered human-language entrance into existing ecosystem state.

## Input

- exact surface expression;
- actor/context;
- activation registry;
- current handoff/runtime state.

## Witness contract

- the actor+surface pair must resolve to exactly one registered activation;
- the activation must preserve its declared current referent;
- selectors may expose only existing supported handoffs/state;
- projection may change presentation but not silently change handoff evidence, status, or provenance;
- activation must not invent tasks, schedules, obligations, or state transitions;
- activation-specific boundaries must survive rendering.

## Output

A projection request and zero or more existing handoff projections.

No network/runtime mutation occurs merely because an activation was spoken.

## Closure

If the user acts on a returned item, that action is handled by the relevant handoff/result contract. The activation itself remains an entrance/view over state.
