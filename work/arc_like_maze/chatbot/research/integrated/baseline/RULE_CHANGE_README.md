# A/B chatbot — rule-change relation witness and continued goal work

**Date:** October 12, 2026. **Status:** local, tested mathematical extension; **not committed to GitHub**.

## Investigated question

If the finite model's **transition law itself** changes, can the same bounded agent independently observe which *rooted action-word relationships* still hold and find an explicit counterexample when another relationship fails? Can a previously unreachable goal become achievable under the new law without handing the route to the program?

**Scope warning:** Here `A` and `B` denote the two named operations of a deliberately chosen 27-state finite example. They do not define James's language-level A/B referent, a physics model, an absolute source, or a universal mathematics of the in-between.

## Construction

Added `ab_chatbot_rule_change.py`, which uses the **existing** two `LanguageBridge` pinned observers instead of reading unknown laws or constructing a second engine. Its `RuleChangeAgent`:

1. Begins at a declared root in each system. It observes actions `A` and `B` in breadth-first order, tracking their effect on **pairs** of states reached by the *same* action word.
2. When two words lead to identical endpoints in **both** systems, records a **preserved word equality**. When the equality holds in one but not the other, returns both replayable action words and four recorded endpoint paths as a **counterexample**.
3. If every outgoing edge on the paired rooted carrier is observed and the correspondence is consistent and bijective, returns `ROOTED_PRESERVED_*` (never full 27-state equivalence unless it actually covers the whole set).
4. Observes at most the authorized **combined per-call new-edge budget**; a separate pinned total budget is never silently raised. Previously read transitions survive an incomplete iteration and are reused.
5. Preserves each observer's identity/version; refuses repinning and reports a wall on invalid observations. It differentiates a live **explicitly bound in-process owner** from an unverified remote observer. Owner-backed cached edge values are checked again before mathematical claims.

For a failed comparison, the `compared_pairs` field counts discovered state pairs **before** the first counterexample. It is not a count of a fully verified closed invariant component.

## Observed controlled example

Owned source law: `FiniteSystem((0,0,0))`.
Owned changed law: `FiniteSystem((0,1,2))`.
Both use identical coordinate labels at the interface, but a **different B rule**; neither is merely a coordinate shear of the other.

```text
RULE_CHANGE: RELATION_CHANGED_WITNESSED
Discovered state pairs before obstruction: 8
Unique old transition observations: 10
Unique new transition observations: 10
Preserved equalities observed:
  '' == 'AAA'   (under both laws)
  'AA' == 'AAB' (under both laws)
Breaking equality:
  'BA' == 'ABB' in old law:
     (1,1,0) == (1,1,0)
  'BA' != 'ABB' in changed law:
     (1,1,0) != (1,1,2)
```

Here `''` means the empty action word. All endpoints were replayed from cached action transitions. Thus the claim is more precise than 'the model changed': a particular equality was preserved while another was not.

## A continued completion task

The **previous** goal agent is reused. For the target `(1,1,2)` and root `(0,0,0)`:

```text
Original law: UNREACHABLE_CLOSED_COMPONENT
New law:      COMPLETE_WITNESSED
Discovered new action word: ABB
New endpoint: (1,1,2)
```

`GoalAgent` chose `ABB` by bounded BFS over observed edges; the action word was **not** provided as the task's answer. The change in reachability is established for these two pinned owned finite systems, not for arbitrary changes in physical circumstances.

## Safeguards / negative controls

- Same rule under nonlinear state relabeling: **rooted correspondence preserved** (9 states), no false rule-change counterexample.
- Identical 27-state owned laws: complete rooted generator agreement (27 mapped states, 54 unique edges per observer).
- Purely off-root relabeling: returned **rooted** agreement even though some off-root transitions differ.
- Reverse change: detected an equality that holds only under the *new* law.
- A single-new-edge per-call limit, zero budget, exhausted total budget, subsequent explicit reauthorization, repin, bad root, unbound remote, invalid observation, and forged cached edge were separately tested.
- No claim is made about off-root dynamics after an early obstruction, general mathematical generalization beyond the declared finite grammar, independent source authentication over external HTTP, or physically witnessed coupling.

## Reproduction

Unzip beside the other Python modules (Python 3.11+, standard library only):

```sh
python ab_chatbot_rule_change.py
python -m unittest -q test_ab_chatbot_rule_change
```

The latest regression ran **15 test modules separately**, with **239/239 tests passed** (the previous 225 plus the 14 tests in `test_ab_chatbot_rule_change.py`). This was not a single monolithic test-run success and does not constitute GitHub Actions CI, real-world deployment, or external benchmarking.

## Warranted next experiment

Instead of only detecting a broken rooted correspondence, let the agent identify **a restricted stable relation that can still be used for a specified next goal** after the rule change, while keeping endpoints outside that restriction unknown or obstructed. That is a different mathematical obligation from merely re-labeling states or identifying one counterexample.

**No repository write or external deployment occurred.**
