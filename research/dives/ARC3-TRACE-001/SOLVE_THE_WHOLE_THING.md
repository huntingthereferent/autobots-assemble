# Solve the Whole Thing

**Active phase name:** Solve the Whole Thing  
**Target:** ARC-AGI-3 100%  
**Mode:** direct solve

This phase begins at the user-directed pivot:

> instead of going this way can't you just solve 100% like human

## Rule

The goal is the benchmark result, not development of a favorite method.

Use whatever generic machinery helps:

- direct visual reasoning;
- ordinary human-style trial and correction;
- A/B underneath when useful;
- world models;
- search;
- planning;
- code;
- prior public evidence;
- Gen-0 / Gen-1 tooling.

But do not turn any one of those into the active project.

## Frozen supporting tooling

Gen-1 is retained at:

`research/dives/ARC3-TRACE-001/direct_agent/gen1/`

Status:

`FROZEN_SUPPORTING_TOOLING · HERMETIC_CI_PASS`

It may be used, tested, or modified later **only when a concrete solve failure requires it**.

Do not continue architecture work merely because another architecture improvement is imaginable.

## Current split

### Work possible without a computer

1. recover verified public solved cases;
2. understand concrete game mechanics and procedural win conditions;
3. preserve exact public solve evidence as **oracle-only** material;
4. identify where strong agents repeatedly failed before a successful solve;
5. turn those failure/success boundaries into concrete expectations for the future live run.

### Deferred until computer

The live first-contact run is pinned at:

`state/pins/ARC3_EXECUTION_BRIDGE_2026-10-04.json`

That dependency does not pause Solve the Whole Thing.

## Oracle boundary

Public solved traces may be stored as regression/oracle evidence.

They may **not** be embedded into the Competition-Mode agent as:

- game-id branches;
- memorized action sequences;
- hard-coded public goals;
- public coordinate lists.

The purpose of an oracle is:

```text
future generic solver output
→ compare against known public solved behavior
→ diagnose failure
```

not:

```text
recognize public game
→ replay answer
```

## Acceptance ladder

### Public oracle coverage

All 25 public games have verified source-free completion evidence available as regression oracle material.

### Public first-contact solve

One generic untouched run solves all 25 public games while counting discovery + execution actions.

### Official 100%

The same general solver receives 100% from the official hidden evaluator.

Only the last line establishes the competition result.
