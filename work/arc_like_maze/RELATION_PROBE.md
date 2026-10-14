# Finite relational probe — correspondence-process feasibility experiment

## Referent

Can an independently executing mathematical process select its next discriminating observation from A/B relationships, rather than relying on a language model to select each move?

The [A/B Ground Record — Current Note](../../AB_Ground_Record_Current_Note_2026-10-11.md) keeps A/B as language for continuing relationships; the finite transformations below are a **mathematical translation of a selected question**, not A/B itself. This experiment concerns **a nine-member finite construction grammar**, not a deployed conversational system, a general A/B solver, a claim about physical systems, or a definition of A/B itself. The standalone precursor was `ab_chatbot_relation_probe.py` (2026-10-11); the integrated version reuses the repository's native [`math.py`](math.py) and [`alignment.py`](alignment.py) rather than maintaining duplicate transformation laws.

## Operation and witness

- **Candidates:** the nine `World(3, (0,a,b))`, with `a,b` in `F3`, from `inverse_candidates()`.
- **Actions:** A and B are the native labeled state transformations, applied to the distinguished origin; they are not arbitrary conversational tasks.
- **Observable:** whether two specified A/B action words end at the same state. The target is observed by a boolean response only; its law/parameters are not read by the selection algorithm.
- **Probes:** exact counterexample word pairs from `discover_alignment` between declared candidates. An `OPEN` witness must actually produce different endpoint-equality answers across the compared candidates.
- **Next mathematical test:** select a probe that minimizes the larger of the two remaining candidate partitions, then prefer balanced and shorter queries. Only the mathematical candidate signatures select the next probe; no LLM is in the continuation loop.
- **Stop:** return `CONDITIONAL_CLASS` when no admitted probe separates survivors, `UNKNOWN_BUDGET` at a query cap, or `NO_MATCH` when a result contradicts all candidates. `CONDITIONAL_CLASS` **never certifies membership** in the nine-member family.

## Reproduction

From the repository root:

```bash
python -m work.arc_like_maze.relation_probe
python -m unittest network.tests.test_arc_like_relation_probe -v
```

In the nine-member grammar, the native exact rooted-reachable equivalence partition has five classes of sizes `[1,2,2,2,2]`. The prototype builds **three** distinct separating word-pair questions; when its target is one of the nine members, **two or three** questions suffice to select its class. This result is a bounded simulation over declared finite transformations, not an empirical measurement of a physical target or live-language user.

The negative control `World(3, (1,0,0))` violates `phi(0)=0` but produces the same answers as the `((0,1,0),(0,2,0))` class on these three tests. Consequently, an apparently successful classification does not establish admission of an unknown target to the candidate grammar. The result is explicitly conditional, and all positive interpretation requires a separately witnessed family-membership argument.

## What survived and what did not

**Survived:** (1) exact rooted A/B correspondence and its counterexample words, (2) autonomous bounded next-question choice, (3) observational invariance under relabeling, (4) repeatable finite test outcomes, (5) explicit provenance through native model and alignment code.

**Not established:** general family admission, arbitrary test invention, generalized continuation to unrestricted mathematical problems, verified cost reduction over LLMs, natural-language interpretation, or a deployed autonomous conversational system. Precomputed selection of a known finite family is not a proof of open-ended independent problem solving.

**Next referent:** test a mathematically justified admission witness, or an explicit unknown-state rejection mechanism, against held-out transformation laws. Keep the existing A/B research separate from software scheduling; only after that test consider whether the observer can be connected to a language-model interface without the language model silently choosing the mathematical move.
