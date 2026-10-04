# ARC-AGI-3 — Swallowed Benchmark / Competition Evidence

**Attached to:** `ARC3-TRACE-001`  
**Status:** swallowed evidence, not a separate protocol or architectural layer  
**Retrieved:** 2026-10-03/04

ARC-AGI-3 is now treated as an evidence contract attached to the active trace. The benchmark, competition rules, scoring, toolkit/interface, testing policy, and current public state-of-the-art are inputs to the trace. They do not replace the current referent.

## Supported benchmark contract

ARC-AGI-3 is an interactive, turn-based benchmark intended to measure adaptation on novel environments without explicit natural-language instructions, rules, or stated goals.

The benchmark explicitly separates four functional demands:

1. **Exploration** — information must be acquired by interacting.
2. **Modeling** — raw observations must become a world model that predicts later states/outcomes.
3. **Goal-setting** — the system must infer desirable/terminal states without being told the objective.
4. **Planning and execution** — the system must map actions from current state to inferred goal and course-correct from feedback.

The official technical report additionally states that causal modeling is prerequisite and that the agent must infer environment mechanics including win conditions.

### Environment/interface

Official docs establish:

- turn-based 2D-grid environments;
- maximum grid size 64 × 64;
- integer cell values 0–15;
- state does not change asynchronously between agent actions;
- environment state exposes one or more frames plus metadata;
- states include `NOT_PLAYED`, `NOT_FINISHED`, `WIN`, `GAME_OVER`;
- each game exposes only its currently permitted subset of a standardized action vocabulary;
- actions are `RESET`, `ACTION1`–`ACTION7`;
- `ACTION6` accepts x,y coordinates;
- `ACTION7` is undo where supported;
- available actions are evidence about affordance, but ACTION6 availability does not reveal valid coordinates.

This means the trace must distinguish **provided interface affordance** from **inferred game semantics**. Knowing that ACTION1 is available is supported input. Knowing what ACTION1 means in the current game still requires an observed transition.

## Supported scoring contract

ARC-AGI-3 uses **Relative Human Action Efficiency (RHAE)**.

Per completed level:

```text
level_score = (human_baseline_actions / ai_actions)^2
```

with a per-level cap of 1.15.

Supported scoring facts:

- completion and efficiency both matter;
- the human baseline is based on controlled first-exposure play;
- the baseline is the upper-median best human action count per level;
- later levels receive larger linear weights than earlier levels;
- incomplete later levels cap the environment score even if early levels are very efficient;
- total benchmark score averages environment scores;
- internal reasoning/tool operations that do not alter the environment are not counted as game actions;
- official evaluation also imposes an action budget relative to the human baseline.

### Consequence for tracing

A correct world model reached through indiscriminate probing is not equivalent to an efficient one.

The trace therefore needs two separate witnesses:

```text
epistemic witness: did the proposed relation survive observed transitions?
efficiency witness: how many environment actions were spent to acquire/use it?
```

A trace that explains a solution after 500 wasteful probes may be scientifically useful but can still score badly.

## Supported competition contract

Official ARC Prize 2026 materials establish:

- ARC-AGI-3 track prize pool: $850,000;
- $700,000 grand prize for the first eligible 100% evaluation score;
- designated Kaggle competition submission;
- no internet access during Kaggle evaluation;
- prize eligibility requires open-sourcing authored code/methods;
- third-party code/methods must permit public sharing under an appropriate open-source license;
- ARC Prize 2026 final ARC-AGI-3 submission deadline: 2026-11-02;
- the official local starter uses Python 3.12 and packages the agent into the Kaggle code-competition path.

### Competition mode

The official toolkit's Competition Mode is stronger than ordinary local play:

- environments are interacted with through the API;
- all available environments count toward scoring even if skipped;
- only level resets are permitted;
- one `make` interaction per environment;
- one scorecard;
- in-flight score cannot be queried;
- Kaggle competition execution forces this mode.

This is the correct later transfer boundary. Repeatedly replaying one public game until solved is not equivalent to competition-first-contact evaluation.

## Evaluation / dataset boundary

ARC Prize's official testing policy distinguishes:

- **Public Tasks** — open and intended for research/development;
- **Semi-Private Evaluation** — used for verified frontier-model testing, with controlled provider exposure;
- **Private Evaluation** — tightly restricted and used for the competition private leaderboard.

Therefore:

```text
public-demo success
≠ verified ARC-AGI-3 score
≠ private competition score
```

Any repo claim must name which layer produced the evidence.

## Current public state of the art — important prior art

The official Community Leaderboard currently reports public-demo systems including:

- **Tycho — 100.0%**: maintains a growing per-game conversation and can delegate a falsification-tested executable world model to a builder for planning.
- **Retrodict — 99.9%**: logs frames and requires rule hypotheses to retrodict recorded history before spending live actions.
- **baseline1 — 99.0%**: coding agent builds and verifies an executable Python world model, then plans through it.

These are Community Leaderboard/public-demo results, not equivalent to private competition results.

### Consequence for ARC3-TRACE-001

The original idea “preserve transitions, falsify hypotheses, build a world model, then plan” is **not novel by itself**. Existing public systems already use closely related structures.

So the impressive referent cannot be:

> produce a nice trace of one public game.

It must become something externally differentiating, such as:

- transfer the same relation-admission contract across unseen public environments without game-specific rewriting;
- materially reduce action expenditure required for model acquisition;
- preserve a machine-auditable provenance graph that predicts later transitions and exposes exactly where a higher-level model became unsupported;
- demonstrate advantage under Competition Mode / first-contact constraints;
- ultimately obtain an external score on hidden evaluation.

This prior-art correction is now part of the ground.

## Trace evidence contract after swallowing

For every game movement preserve:

```text
OBSERVATION
+ AVAILABLE ACTIONS
+ CHOSEN INTERVENTION
→ OBSERVED DELTA

OBSERVED DELTA
+ PRIOR ADMITTED RELATIONS
→ CANDIDATE RELATION

CANDIDATE RELATION
→ PREDICTION
→ LATER TRANSITION
→ SUPPORTED / PARTIAL / FALSIFIED / UNKNOWN
```

Do not promote:

```text
local action effect
→ object semantics
→ world model
→ goal
```

without independent witnesses at each boundary.

Keep mechanics, world-model relations, and inferred goal as distinct relation classes.

## Supported / partial / unknown

### SUPPORTED

- Four benchmark pillars: exploration, modeling, goal-setting, planning/execution.
- No explicit instructions/rules/goals are given.
- Turn-based standardized action interface.
- RHAE scoring and human action baseline structure.
- Kaggle/no-internet/open-source competition boundary.
- Competition Mode restrictions.
- Public vs Semi-Private vs Private evaluation separation.
- Current official Community Leaderboard descriptions above.

### PARTIAL

- Exact full Kaggle terms/eligibility clauses are not represented in the ARC Prize page text retrieved here; joining the Kaggle competition requires accepting Kaggle competition rules.
- Exact final runtime/quota constraints beyond the official starter/toolkit surface should be re-read directly in the live Kaggle rules before submission.
- The previously linked replay session `7752f433-a3a4-4026-ae8c-6c32b4afcf9d` currently exposes the replay shell through this retrieval path but does not expose loaded game metadata/reasoning text. Do not use the earlier `ar25` characterization as a witnessed fact until the replay data or game source is directly inspected.

### UNKNOWN / intentionally hidden

- Private evaluation environments and mechanics.
- Private win conditions before first contact.
- Private leaderboard outcome for any local/public method.
- Any relation not witnessed by current-game interaction.

## Official source map

- Benchmark: https://arcprize.org/arc-agi/3
- Launch: https://arcprize.org/blog/arc-agi-3-launch
- Technical report: https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf
- Competition: https://arcprize.org/competitions/2026/arc-agi-3
- ARC Prize 2026 general rules: https://arcprize.org/competitions/2026
- Docs index: https://docs.arcprize.org/
- Game schema: https://docs.arcprize.org/game-schema
- Actions: https://docs.arcprize.org/actions
- Scoring: https://docs.arcprize.org/methodology
- Competition starter docs: https://docs.arcprize.org/arc-prize-2026
- Competition Mode: https://docs.arcprize.org/toolkit/competition_mode
- Testing policy: https://arcprize.org/policy
- Community leaderboard: https://arcprize.org/leaderboard/community
- Official benchmarking repo: https://github.com/arcprize/arc-agi-3-benchmarking
- Official toolkit: https://github.com/arcprize/ARC-AGI
- Kaggle starter: https://github.com/arcprize/ARC-AGI-3-Kaggle-Starter

## Next movement

Do not begin with semantic interpretation of a stale replay.

Use an **officially available current public environment** through the toolkit, capture the first-contact frame and available actions, and begin the state/action/effect ledger under the swallowed contract.

The first experiment should be selected to test transferability, not merely to maximize the chance of solving a game already known from public traces.
