# ARC-AGI-3 — Direct Observation Work Lane

**Lane ID:** `arc3-direct-observation`  
**Purpose:** Work toward solving real ARC-AGI-3 environments from native, observed interactions, preserving every action and correction. This is a separate `work/` lane, not another bot, solver generation, game imitation, or replacement for the existing research.

## F3 mathematical starting point

[The native F3-first experimental agent](agent/my_agent.py) uses the **actual depth-three transformations** and all nine phi(0)=0 candidate laws from [the original finite mathematical source](../arc_like_maze/math.py). [AGENTS.md](AGENTS.md) records the investigation rules and evidence boundary. The independently tested equations drive candidate endpoint-collision probes; this is not another G0/G2 solver, bot, or orchestration layer.

The current agent tries one **provisional** assignment of two advertised native simple actions to mathematical A/B. It checks visible-frame counterexamples without relabeling colors as F3 values. A surviving candidate remains conditional; a contradiction yields OUTSIDE_DECLARED_F3_FAMILY. The initial policy does **not** infer goals or demonstrate an ARC win. Other native action assignments and richer finite-field grammars remain separate questions.

Reproduce source-law conformance and the falsification cases:

```sh
python -m unittest -v network.tests.test_arc3_f3_agent
```

No native ARC gameplay has yet been witnessed for this F3 prototype. Historical G2.3 public-game evidence is retained as a comparison, not imported as the new agent's reasoning.

## Current F3/native observation

[LS20 native relational evidence](runs/LS20_F3_NATIVE_RELATIONS_2026-10-17.md) now records the result of using the original F3 laws as a hypothesis against the real game: exact co-transport of native color groups, a separate persistent 2-cell change on every tested action, visible final-frame collisions for native words 34/43 and 23/32, and order-sensitive 12/21. All measurements came from official native action calls, not a synthetic ARC imitation.

The mathematically necessary F3 order-three relation did **not** survive the literal raw-state mapping; the new observed glyph/trace distinction is not yet a justified F3 state representation. The single-file F3 agent remains experimental, and no game win is claimed. [Reproducible native tests](native_mixed_relation_probe.py) and [the direct original-law comparison](f3_native_word_comparison.py) preserve that boundary.

## Existing source, not rewritten

- [Direct-solve objective](../../research/dives/ARC3-TRACE-001/DIRECT_SOLVE.md) — solve the actual games, with discovery actions counted.
- [Operator shell](../../research/dives/ARC3-TRACE-001/direct_agent/operator_shell.py) — the existing one-action-at-a-time native ARC interface and append-only JSONL observations.
- [Operator instructions](../../research/dives/ARC3-TRACE-001/direct_agent/OPERATOR.md) — exact manual operation.
- [First-contact runbook](../../research/dives/ARC3-TRACE-001/direct_agent/RUNBOOK.md) — separates untouched evaluations from tuned replays.
- [Native observation adapter](../../runtime/ARC_NATIVE_OBSERVATIONS.md) — source-owned before/after frame observation, not an actuator.
- [Recorded routes](../../research/arc_native_runs/README.md) and [negative autonomous trials](../../research/arc_native_runs/AUTONOMOUS_TRIALS.md) — historical evidence, **not** first-contact wins by this lane.

The independent [mathematical ARC-like experiments](../arc_like_maze/README.md) stay in their own directory. Their finite constructions do not serve as results for this native game lane.

## First operating slice

Use the existing official ARC runtime on an authorized machine and the **existing** operator shell; do not replay saved winning routes as first-contact results:

```sh
python -m work.arc3.lane open --journal runtime/data/workspace.jsonl
python research/dives/ARC3-TRACE-001/direct_agent/operator_shell.py --game ft09 --log runtime/data/arc3/ft09-new-session.jsonl
```

In the ARC shell: inspect `show` / `info`, choose a concrete action, issue `act N` or `act 6 X Y`, inspect what actually changed, and continue. This action is performed by the operator shell, **not** the lane code.

After at least one native action:

```sh
python -m work.arc3.lane inspect --trace runtime/data/arc3/ft09-new-session.jsonl
python -m work.arc3.lane record --journal runtime/data/workspace.jsonl --trace runtime/data/arc3/ft09-new-session.jsonl
```

`inspect` reads the source log without launching ARC, scheduling a process, or altering a journal. `record` links its digest and source-reported action changes into **only this lane's** existing `WorkspaceStore` journal. An identical trace cannot be recorded twice. Another lane's return point and current focus are preserved.

## What we can and cannot conclude

- `LANE_OPENED` is a return point, **not** a completed observation or active session.
- The operator transcript records reported action IDs, before/after frame hashes, changed-cell counts, optional bounding boxes, levels, and resets. Continuity is checked **within the log**; original raw frames must be retained for an independent pixel-level audit.
- An action with a nonzero changed-cell count is a reported observed change, **not** a proven mechanism, prediction, level solve, or first-contact benchmark score.
- A previously solved FT09, LS20, or SK48 route is prior evidence, **not** a new live solve. A fresh session on a previously studied game is not first contact to that game's unseen rules.
- No general-purpose worker, delegated bot, automatic game action, invented environment trace, or new scheduler is created here.
- GitHub stores the source of this lane; private `runtime/data` journals and actual native actions only exist where explicitly run. Committing this branch alone does not start a remote ARC game.

## Next actual movement

Capture a real native start state, available actions, and one action's before/after observation. State the proposed effect and **predict a subsequent change before taking the next action**, then keep the actual correction if it differs. Continue toward the level win state and separately measure action efficiency.

## Checks

```sh
python -m unittest -v network.tests.test_arc3_direct_work_lane
```
