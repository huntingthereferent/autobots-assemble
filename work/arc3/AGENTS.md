# ARC-AGI-3: F3-first investigation instructions

This lane uses **the repository's existing finite-field constructions** to propose and challenge relations in native ARC-AGI-3 gameplay. The objective remains to solve ARC efficiently; the present F3 agent is a bounded hypothesis-testing baseline, **not** a demonstrated solver or general ARC-to-F3 theorem.

## Mathematical source

- [Finite F3 worlds](../arc_like_maze/math.py): the exact depth-three A/B maps and nine phi=(0,a,b) candidate laws.
- [Rooted labeled alignment](../arc_like_maze/alignment.py): full mathematical correspondence and explicit conflicting action words.
- [Finite relational probe](../arc_like_maze/relation_probe.py): endpoint-equality questions, conditional classifications, and an outsider negative control.
- [Inverse construction engine](../arc_like_maze/engine_one.py): admissible successors within separate finite grammars. Different mathematical families are not interchangeable.

The finite mathematics is a scoped model within the Language Referent investigation, not the universal definition of A/B or proof that ARC is an F3 world.

## ARC observation boundary

[The single-file agent](agent/my_agent.py) is directly based on the equations in the original mathematical source. The regression test checks the two transformations against all nine source laws and all 27 states. The official Kaggle starter embeds exactly one my_agent.py file, so the submitted agent must not import work.*, gen1.*, g2.*, or other local research-only modules.

ARC action IDs do **not** intrinsically designate mathematical A and B. For an initial bounded experiment the agent treats the first two currently advertised simple native actions (ACTION1–ACTION5) as *provisional* A/B roles. It cannot infer the correct pair from the interface alone. Other ordered pair assignments remain untested. Coordinate clicks and undo are not silently promoted to mathematical generators. No real game correspondences are established yet.

Native full 64x64 frames remain intact; do **not** apply modulo-three to their colors. Two unequal exact visible frames give a definite non-equality observation. Two equal visible frames may conceal distinct histories; they never certify hidden native state equality. A candidate F3 law requiring equal endpoints is rejected if corresponding native frames actually differ. Surviving candidates are **conditional**, not proof of F3 membership.

This prototype only exercises one rooted forward action path. It does not infer goals, win conditions, full-state conjugacy, a general action mapping, or score-efficient plans. The fallback action after a wall is an interface placeholder, **not mathematical progress**.

## How to continue

1. Run math conformance and falsification checks: python -m unittest -v network.tests.test_arc3_f3_agent
2. Run the real native environment through the already-existing operator or official starter. Record exact agent source hash, root, available actions, provisional generator pair, predictions **before** each action, actual complete frame, action count, level score, and counterexample words.
3. Keep native frames and locally recorded evidence separate from the GitHub source. A mathematical synthetic witness or saved FT09/LS20/SK48 replay is not a new first-contact win.
4. On a contradiction, record it and keep the result OUTSIDE_DECLARED_F3_FAMILY. Investigate whether a different native action pairing, richer observable correspondence, or separately admitted F3 law family is warranted. Do not switch to ARC heuristics under a renamed class.
5. Compare new revisions against the old G0 and G2.3 native results without mixing discovery-inclusive, replay-assisted, and hidden/competition runs. A green unit test alone is not a game solution.

No new worker harness, bot ensemble, game simulator, or alternate scheduler is introduced here.

## Native LS20 F3 first experiment (2026-10-17 local)

[Native evidence and reproducible controls](runs/LS20_F3_NATIVE_2026-10-17.md) establish that **all four** advertised single directional controls fail the original F3 A³=root identity on the exact visible LS20 root frame. The F3 single-path agent under provisional ACTION1=A, ACTION2=B likewise exhausted the original nine-law family (0 levels won). Treat this as a **counterexample to direct full-frame generator identification**, not a proof that all native ARC games or other possible state representations cannot carry F3 relations.

Do not retry the same action-ID renaming as a mathematical improvement. A next attempt needs an independently motivated native-to-F3 state correspondence, with preserved action-word predictions and explicit negative controls. Use real native transitions through the [official-run smoke](native_smoke.py) and [root-generator probe](native_f3_generator_probe.py), not stored game scripts or a replacement game engine.
