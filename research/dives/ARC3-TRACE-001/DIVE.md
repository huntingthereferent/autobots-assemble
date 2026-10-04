# ARC3-TRACE-001 — ARC-AGI-3 Causal Reasoning Trace

**Status:** active  
**Protocol:** `research.dive`  
**Primary lane:** Theory / Research  
**Relations:** Open Source; Prize / benchmark

## Current referent

📍 **Trace ARC-AGI-3 first-contact interaction as witnessed relations, then test whether the same admission contract transfers across environments without game-specific rewriting.**

ARC3 has now been **swallowed** into this dive. The official benchmark, scoring method, interface, competition mode, testing policy, and current public prior art are attached evidence rather than separate architecture.

See:

- [ARC3_SWALLOWED.md](ARC3_SWALLOWED.md)
- [arc3_contract.json](arc3_contract.json)

## Ground after swallowing

The benchmark itself gives us a clean external sequence:

```text
exploration
→ model formation
→ goal acquisition
→ planning / execution
```

but the trace must not collapse those into one inference.

For our purposes:

```text
observable state
+ available actions
+ chosen intervention
→ observed delta
→ candidate relation
→ prediction
→ later witness
→ supported / partial / falsified / unknown
```

Mechanics, world-model relations, and inferred goals remain different relation classes.

## Important correction — public demo is not the impressive boundary

The official ARC Prize Community Leaderboard already contains near/complete public-demo systems whose methods overlap our initial idea:

- Tycho: falsification-tested executable world model used for planning;
- Retrodict: hypotheses must explain recorded history before spending new live actions;
- baseline1: executable Python world model followed by planning.

Therefore a clean trace of one public environment is useful research evidence, but **not a novel or impressive external claim by itself**.

The differentiating boundary is now one or more of:

1. the same relation-admission contract transfers unchanged across unseen environments;
2. it learns useful relations with materially fewer environment actions;
3. provenance exposes exactly where unsupported abstraction enters the model;
4. it survives official Competition Mode / first-contact constraints;
5. it receives hidden/private external evaluation.

## Scoring changes what “good tracing” means

ARC-AGI-3 uses Relative Human Action Efficiency (RHAE). Solving eventually is not enough; environment actions spent learning and acting matter.

So preserve both:

```text
truth / witness quality
AND
action cost
```

Internal reasoning can be long without directly costing RHAE, while blind environment probing is explicitly expensive.

## Interface ground

Official docs establish a bounded action surface: RESET plus ACTION1–ACTION7, with only currently available actions exposed. The game provides affordances, not their game-specific meaning.

That is useful for us:

```text
ACTION1 available       = supplied evidence
ACTION1 means "move X"  = hypothesis until transition-witnessed
```

## Evaluation boundary

Keep claims separated:

```text
local/public trace
≠ community public-demo score
≠ verified semi-private score
≠ private competition score
```

The private competition set is intentionally unavailable.

## Earlier ar25 target

The previous ar25 replay reference is now **PARTIAL**, not deleted. Through the current retrieval path the replay shell is visible, but its game metadata/reasoning did not load. The earlier descriptive characterization is therefore not strong enough to orient the experiment.

We will select a **currently available official public environment directly through the ARC toolkit** for first contact.

## Trace record

For every movement preserve:

| Field | Meaning |
|---|---|
| state | observable configuration before action |
| available_actions | affordance supplied by the environment |
| action | intervention actually taken |
| effect | observable delta afterward |
| candidate relation | rule currently proposed |
| witness state | supported / partial / unknown / falsified |
| prediction | next observable consequence if relation is real |
| action cost | environment actions spent to acquire/use the relation |
| correction | what changed after failed prediction |
| provenance | exact frame/action/source supporting the movement |

## Handoff boundary

GEMS remains pinned at:

`state/pins/GEMS-001_2026-10-03.json`

Nothing in ARC3 resolves or replaces the GEMS wall.

## Next movement

Use the official toolkit to select a currently exposed public environment.

Capture only:

```text
first-contact state₀
available actions
chosen action₀
state₁ - state₀
```

Then continue until a candidate relation can make a prediction **before** its witness is observed.

No inherited game semantics. No replay answer leakage. No “I recognize this.”
