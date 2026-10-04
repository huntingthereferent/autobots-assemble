# Live First-Contact Run — G0.1 — 2026-10-04

**Phase:** Solve the Whole Thing  
**Run type:** untouched generic public first-contact sweep  
**Status:** COMPLETE

## Runtime

- Authorized Windows desktop via Remote Desktop Commander.
- Native Windows setup; WSL was not required.
- Python 3.12.10.
- `arc-agi` 0.9.9.
- Official `arcprize/ARC-AGI-3-Kaggle-Starter`.
- Official `arcprize/ARC-AGI-3-Agents` framework.

## Provenance

Frozen/generic agent lineage:

`research/dives/ARC3-TRACE-001/direct_agent/my_agent.py`

Run SHA-256:

`8ddb2fd7743824c9c352e0711e44a3023785869f7d42426ed4e8150ad0c79e64`

Rules preserved by the runner:

- discovery actions counted;
- no banked replay substitution;
- no per-game answer branches;
- same agent file across all 25 games.

A prior attempted baseline using SHA
`d73e8d2b5f6bae658b26b03ce7ec714f66548baba293a8262f1e84412255bc36`
failed immediately because the official Agent seeds its history with a synthetic empty `FrameData`.
That failed witness was preserved locally. The only solver change before G0.1 was the generic runtime correction:
ignore that synthetic empty bookkeeping frame when learning a prior transition.

The first-contact runner also required a Python 3.12 loader fix:
register the dynamically loaded module in `sys.modules` before executing it.
That is runner plumbing, not agent logic.

## Result

```text
games seen:                25 / 25
full games won:             0 / 25
levels completed:           2 / 183
real environment actions: 15025
official aggregate score:   0.0059025446738094935
```

Every game consumed 601 counted actions.

## Only observed level-ups

### VC33

```text
1 / 7 levels
first level-up: action 426
actions: 601
```

Official first-level baseline: 7 actions.

### LP85

```text
1 / 8 levels
first level-up: action 74
actions: 601
```

Official first-level baseline: 17 actions.

All other 23 public games remained at level 0.

## Direct diagnosis

This baseline is not failing because its action API is broken.

It can:

- inspect real frames;
- issue all official action types;
- make coordinate clicks;
- survive resets;
- detect at least two genuine level-ups;
- complete a full 25-game execution loop.

It is failing because its decision representation is too shallow.

Observed behavior matches the oracle hard-case ledger:

- click games often collapse into repeated salient-click probing;
- directional games often collapse into one locally favored direction;
- ACTION5 games can repeat interaction without inferring the latent procedure;
- symbolic games receive no symbolic task representation;
- no mechanism exists for reasoning about hidden history, temporal helper roles, multi-representation constraints, or procedural goals;
- exact transition memory does not by itself create a useful objective.

## Important comparison to the target

The target is not:

```text
make G0.1 explore longer
```

G0.1 already spent 15,025 real actions for only two levels.

The next move must improve **inference per action**.

## Evidence-driven next movement

Build the next direct solver generation around the first decision humans make that G0.1 does not:

```text
observe initial board
→ infer what kind of problem this is
→ infer candidate goal / progress variables
→ choose the smallest discriminating action
→ update the representation
→ switch from discovery to execution once supported
```

The hard-case ledger constrains what that representation must be able to express:

1. spatial/object relations;
2. ordered procedures;
3. symbolic strings/programs;
4. latent/history state;
5. multiple simultaneous constraints;
6. autonomous/other-agent dynamics;
7. temporal role splitting;
8. model-incompleteness uncertainty.

Do not hard-code public game IDs or oracle action paths.

## Current status

`MOVE — LIVE EXECUTION BRIDGE OPEN`

The computer is no longer a deferred dependency.
