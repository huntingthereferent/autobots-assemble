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

## Tested native relations — before adopting F3 coordinates

The [LS20 native relation record](runs/LS20_F3_NATIVE_RELATIONS_2026-10-17.md) is now the return point for the F3 experiment. Native exact-color groups 9 and 12 were observed translating rigidly five pixels per ACTION1/3/4 step; two color-11 cells changed to color 3 per native step independently of the object's apparent movement. A simple color/coordinate modulo-three map is **not** admitted from this evidence.

Short **native** rooted words also have context: 34 and 43 have the same visible final full frame; 23 and 32 likewise; 12 and 21 differ. ACTION2 does not move the observed glyph at the initial boundary but moves it downward after ACTION1 has moved it up. Thus the native observation is richer than a single independent "position" coordinate.

The original nine mathematical F3 worlds require A³=id and AB!=BA at the rooted origin. The [source-derived F3/native comparison](f3_native_word_comparison.py) reports qualitative agreement for the 12/21 inequality only; equality of visible native frames never proves hidden state equivalence, and a three-step native F3 cycle has not been witnessed. Do not silently promote this agreement to a solved ARC level or claim the nine-world F3 family now fits LS20.

Next admitted experiment must state a falsifiable, **predeclared** native-state factorization and demonstrate preserved predictions on newly executed mixed action words, including actual return and boundary cases. If no nontrivial native 3-cycle is witnessed, retain an explicit mathematical WALL rather than renaming a native integer coordinate to F3 by arbitrary modulo.

## Native suffix evidence and exact F3 obstruction (Oct 17, 2026)

[LS20 suffix experiment](runs/LS20_F3_SUFFIX_2026-10-17.md) is the current return point: 120 actual native actions (36 fresh resets) tested identical suffixes after the previously observed 34/43, 23/32, and 12/21 rooted words. The equal visible prefixes remained equal under all six tested suffixes; the unequal 12/21 prefixes visibly converged after suffix 2 and suffix 21. Equal native frames are **not** proofs of equal hidden native states.

[Source-checked F3 mathematics](f3_suffix_permutation_witness.py) independently verifies that the two corresponding F3 endpoints under provisional ACTION1=A, ACTION2=B must **remain mathematically distinct in all nine original worlds** after the common mathematical suffixes. This obstructs an **injective raw-visible-state F3 realization**, not all F3 correspondences. Do not patch the original field operators, select a modulo-three position solely to make a fit, or present this as a game win. The next admitted F3 move needs a predeclared, newly testable state relation with explicit history/trace dependence and independent native frame witnesses.

## Current measured LS20 visible-state dynamics

[Native factor prediction and counterexamples](runs/LS20_NATIVE_FACTOR_PREDICTION_2026-10-17.md): independent native initial/root calibration witnessed 25 pixels (15 in native color 9 and 10 in native color 12) that translate rigidly in five-pixel steps, with a separate two-cell trace advancing on each action. The first unbounded motion model failed **6/34** exact full-frame predictions near native walls; trace predictions survived **34/34**. A predeclared static-native-background collision rule repaired those failures and then predicted **35/35 complete native frames** on eight fresh mixed action words not used to identify the wall mechanism (**69/69** total including retests).

This is **not** an F3 law or general ARC solver. The original F3 nine-law source and its A³ and invertibility obligations are unchanged; raw native blocking and trace changes still defeat a direct F3-state correspondence. The research can now attempt an independently tested mathematical state factorization over the *witnessed* native transitions, not invent a modulo-three map or adopt an ARC heuristic agent. No actual game win or new autonomous worker has been shown.
