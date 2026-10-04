# ARC3-TRACE-001 — ARC-AGI-3 Causal Reasoning Trace

**Status:** active  
**Protocol:** `research.dive`  
**Primary lane:** Theory / Research  
**Relations:** Open Source; Prize / benchmark

## Current referent

📍 **Trace one public ARC-AGI-3 environment from raw observation through causal model, inferred goal, plan, action, correction, and replay evidence.**

This is intentionally narrower than “solve ARC-AGI-3.” The first object is a complete, falsifiable trace.

## Why this is an unusually strong trace target

ARC-AGI-3 does not provide natural-language instructions, rules, or goals. An agent must interact with an unfamiliar environment, infer mechanics from state changes, discover what counts as progress, plan over multiple steps, and revise when its model fails.

That gives the trace an external structure:

```text
raw state
→ intervention / action
→ observed state delta
→ candidate relation
→ prediction
→ confirming or falsifying transition
→ compact world model
→ inferred goal
→ plan
→ action sequence
→ replay / score witness
```

The benchmark is useful because a convincing-looking explanation is not enough. Public replays expose the action history, and hidden benchmark evaluation provides a separate external witness for any later agent work.

## First environment: ar25

Start with **ar25**, a public demo environment.

Why ar25:

- public and inspectable;
- model replays already show substantial exploration;
- the replay contains failed interpretations, reversals, resets, and partial progress;
- those mistakes are useful evidence because the trace must preserve corrections rather than rewrite history after the answer is known.

The first pass must **not** inherit the model replay's prose as truth.

Build the state/action/effect ledger from observable transitions first. Model reasoning becomes comparison evidence afterward.

## Trace contract

For each movement preserve:

| Field | Meaning |
|---|---|
| state | observable configuration before action |
| action | intervention actually taken |
| effect | observable delta afterward |
| candidate relation | rule currently proposed |
| witness strength | supported / partial / unknown / falsified |
| prediction | what should happen next if the rule is real |
| correction | what changed when prediction failed |
| provenance | frame/replay/source that supports the movement |

Separate three things that agents often collapse:

1. **mechanic** — what an action does;
2. **world model** — how mechanics interact with objects/state;
3. **goal** — what future state actually counts as success.

## First definition of solved

The first trace is complete when:

- admitted mechanics are tied to observed transitions;
- failed hypotheses remain visible;
- at least one rule makes a correct prediction about a later transition;
- the inferred goal is evidenced separately from the mechanics;
- the action path can be replayed/explained without hidden instructions;
- the resulting trace structure can be reused unchanged on another public environment.

## Known failure mode worth testing

ARC Prize's own model analysis reports a recurring pattern: models can correctly notice a local action effect but build the wrong higher-level world model from it.

That is exactly where this trace should be strongest. A local transition is evidence for the local relation only; it does not automatically license the larger semantic story.

## Source map

- ARC-AGI-3 benchmark: https://arcprize.org/arc-agi/3
- ARC-AGI-3 technical report: https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf
- ARC Prize 2026 ARC-AGI-3 competition: https://arcprize.org/competitions/2026/arc-agi-3
- Human baseline/replay dataset: https://arcprize.org/blog/arc-agi-3-human-dataset
- ARC-AGI-3 model failure analysis: https://arcprize.org/blog/arc-agi-3-gpt-5-5-opus-4-7-analysis
- ar25 replay used as initial comparison evidence: https://arcprize.org/replay/7752f433-a3a4-4026-ae8c-6c32b4afcf9d

## Handoff boundary

GEMS was not closed.

Its exact state was pinned at:

`state/pins/GEMS-001_2026-10-03.json`

The move to ARC3-TRACE-001 is an explicit user-directed referent change, not evidence that the GEMS wall was resolved.

## Next movement

Reconstruct **ar25** from the earliest observable transitions.

Do **not** begin by asking what the game “means.” Begin with:

```text
state₀
+ action
→ state₁ - state₀
```

Build the ledger until a candidate relation can make a falsifiable prediction.
