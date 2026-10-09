# Codex Handoff — Axioms

Updated: 2026-09-30 (America/Chicago)

## ACTIVE PROJECT

**You are working on Axioms, not Eggy.**

Repository:

```
huntingthereferent/axioms
```

Local working copy may be on the USB/workspace. Read the local `AXIOMS_HANDOFF.md` and preserve its completed witness evidence.

Eggy is frozen as an evidence/regression bank unless the user explicitly reopens it.

Do not resume Eggy development.
Do not copy Eggy architecture into Axioms.
Do not treat old implementation names as definitions of A/B.

## 1. Important Status Correction

The first Axioms task has already been completed.

Do **not** rerun the first witness as though it were still pending.

Completed evidence:

```
X1 = ab(X0)
X2 = ab(X1)
```

The same entry point accepted X1 directly.

Fixture:

```
00=0, 01=1, 10=1, 11=0
```

Observed:

- X1: both first-order routes produce `+1, -1`
- X2: routes `a,b` and `b,a` each produce `-2`
- result: `SUPPORTED_TWO_STEP_NATIVE_MOVEMENT`
- no new WATCH, adapter, pair selection, layer argument, or second operator was supplied between calls

The candidate is bounded integer finite differences and is not identified with general A/B.

Preserve the first witness.

## 2. Why A Second Test Is Needed

The first candidate still carries a future-comparison schedule.

Its tables include an axis list. After differentiating along one axis, the output records the other axis as "remaining." The next call therefore already knows which native contrast remains available.

This is a valid first result, but it does not answer whether the witness itself carries the relation that makes the next comparison admissible.

The next test removes only that crutch.

## 3. Authorized Task — Experiment #2

Keep:

- the same four source values;
- the same binary square;
- the same integer subtraction rule;
- the same `0 -> 1` orientation;
- one A/B entry point;
- exactly two calls.

Change only the authority for the second comparison.

The new experiment must not use a carried "remaining axes" list, queue, schedule, route plan, or equivalent hidden future-selection field to tell the second call what to compare.

Instead, X0 must retain explicit native source relations and X1 must retain the relational support needed to test whether its derived nodes themselves stand in an earned relation.

A useful bounded representation of the source support is:

```
00 --b-- 01
10 --b-- 11

00 --a-- 10
01 --a-- 11
```

First-order derived nodes may still retain signed parents, e.g.:

```
d_a0 = 10 - 00 = +1
d_a1 = 11 - 01 = -1
```

On the second call, do not use "b is the remaining axis."

Instead ask whether the support carried in X1 earns a relation between `d_a0` and `d_a1`.

For this fixture, inspect whether both signed parent sides are related by the same native source relation:

```
10 --b-- 11
00 --b-- 01
```

If the candidate contract earns that relation, A/B may compare the derived nodes and produce:

```
-1 - (+1) = -2
```

The opposite route should be treated by the same rule.

Do not hard-code the expected `-2` as an outcome. It must arise from the retained evidence and native arithmetic.

## 4. What This Test Is And Is Not

This test asks:

```
Can A/B carry the relation that makes its own next A/B admissible?
```

It does **not** ask:

- whether Axioms can search arbitrary provenance for patterns;
- whether general A/B has been defined;
- whether unrepresented distinctions can always be discovered;
- whether recursion should continue indefinitely;
- whether Eggy should be rebuilt.

A pass would demonstrate a stronger bounded property: witness-carried relational recursion without a pre-carried future-axis schedule.

## 5. Preserve First Evidence

Do not overwrite or rewrite the first experiment.

Preserve, if present:

- `two_step.py`
- `evidence/first.json`
- `REPORT.md`

Create a new isolated source/evidence/report path for experiment #2.

Do not mutate old evidence to make the new representation look retroactively cleaner.

## 6. Required Result Categories

### SUPPORTED_RELATION_CARRIED_RECURSION
The same A/B entry point earns X2 from relation evidence retained in X1, without a future-axis schedule.

### UNKNOWN / PARTIAL
The retained relation evidence is insufficient for the next comparison.

### EARNED ZERO
The next relation is supported and positively earns zero/no movement.

### CONTRACT / IMPLEMENTATION LIMIT
The representation cannot express or consume the needed evidence.

Do not collapse these categories.

## 7. Hard Constraints

Do not add:

- a new fixture;
- a third axis;
- a third recursive call;
- a human-selected higher WATCH;
- a second operator;
- a planner or classifier;
- a layer parameter;
- TOP, psi, Meta, Eggy runtime structures;
- persistence/database/filesystem observation;
- an adapter that selects the next comparison;
- a repair-and-rerun loop.

The source relation may be explicit in X0. The **future comparison schedule may not be**.

The same A/B entry point must receive the complete returned X1.

## 8. One-Run Stop Condition

Run exactly one experiment #2 witness.

STOP immediately after the first honest result.

Record:

- exact files created/changed;
- exact command;
- X0 relation representation;
- X1 derived nodes;
- retained signed parents;
- retained source relations;
- how the X1 -> X2 relation was admitted or rejected;
- whether any future-axis schedule remained;
- X2 if earned;
- first unsupported relation if not;
- result category;
- any outside choice supplied between calls.

Do not broaden after success.
Do not repair after failure in the same run.

## 9. Handoff Back

Update `AXIOMS_HANDOFF.md` after experiment #2.

Keep the first witness history intact.

The handoff back must answer:

```
Did the next A/B arise from relation carried by X1,
or was some next-comparison choice still supplied from outside?
```


## Experiment #2 completed — 2026-09-30

Status: STOPPED FOR REVIEW. The Experiment #2 instructions above have been executed once; do not treat them as a pending run.

Result: SUPPORTED_RELATION_CARRIED_RECURSION, exit 0. Same ab entry point, two calls; complete X1 directly admitted. Four first differences (+1,+1,-1,-1), followed by two -2 values. No carried remaining-axis or future-comparison schedule exists.

The second comparisons were admitted from both signed parent pairs having the same directed native source relation: d4 -> d7 via a1/a0, and d5 -> d6 via b1/b0. No outside choice was supplied between calls. The native source edges, orientation, subtraction, same-sign lifting rule and all-pairs policy remain initial candidate choices.

See experiment2/REPORT.md, experiment2/second.json and experiment2/two_step.py for the exact evidence and limits. Experiment #1 source, JSON and report were verified unchanged by SHA256. Old local handoffs were archived in experiment2 before importing the updated repo instructions. No repair/rerun, third call, GitHub write or Eggy change occurred.

This is bounded relational recursion on the retained square; no claim of general A/B discovery. Missing/partial support, zero, malformed inputs and further calls remain untested. Further work awaits user direction.

## Experiment #3 removal attempt completed — 2026-09-30

User authorized this attempt in conversation; remote instructions still described #2. One isolated run removed the special lifting branch, preserving the square, arithmetic, source relations, and two calls. X1 remains admissible with +1,+1,-1,-1. No second-call pair was admitted; X2 current is empty.

Raw outcome UNKNOWN; interpretation CONTRACT / IMPLEMENTATION LIMIT: the remaining admission function recognizes source edges only and has no operation consuming parent structure to earn derived relations. This is a dependency ablation, not evidence that lifting cannot be expressed by A/B. The broader collapse question remains unresolved.

No outside choice was added between calls. No replacement rule or repair was invented. Prior source/evidence/report files for #1 and #2 were verified byte-for-byte unchanged. See experiment3/REPORT.md and experiment3/third.json. STOPPED FOR REVIEW; do not rerun earlier instructions.

## Code-review correction — 2026-10-01

Experiment #4 has not been implemented or run. Its proposed recursive parent-admission mechanism was already present in Experiment #2.

Verified in experiment2/two_step.py, relations(), lines 13-22:
- It recursively asks relations() about the positive parent pair.
- It recursively asks the same function about the negative parent pair.
- It admits the derived relation when both witnesses have the same native relation kind.
- It retains both support witnesses.
There is a difference-type guard, but no generation number or second-layer special case.

Thus "special lifting" in earlier descriptions denotes this supplied recursive inference rule, not a separate nonrecursive layer. Experiment #3 removed that recursive branch. Its empty second result records the remaining source-edge-only implementation's dependency on the branch.

Replacing the difference-type guard with a general signed-support contract could broaden representation, but would leave the same inference condition supplied. Reproducing -2,-2 after that refactor would not show that correspondence was derived from A/B or that an axiom had been eliminated.

Current evidence:
1. Experiment #1: two-step execution using remaining-axis tables.
2. Experiment #2: relation-carried two-step recursion under the supplied corresponding-parent rule.
3. Experiment #3: removal exposes the existing implementation's admission dependency.
4. Proposed Experiment #4: reviewed for equivalence; no new witness run.

Unresolved: whether a separately specified account of A/B earns that correspondence rule, or whether it must remain an explicit premise. Neither necessity nor irreducibility has been established. Avoid treating a rename or recursive implementation as a derivation.

No new mathematical rule, fixture, code modification, or experiment is introduced by this correction. Earlier experiment sources, reports, and JSON remain historical evidence. Next implementation needs a materially distinct question; do not rerun #2 under the label #4.
