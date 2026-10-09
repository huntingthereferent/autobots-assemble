# Axioms Handoff

Updated: 2026-09-30 (America/Chicago)

> **ACTIVE PROJECT:** Axioms is the active build/research project. Do not continue Eggy unless the user explicitly reopens it. Eggy is retained as an evidence/regression bank only. Fresh Codex sessions must read `CODEX_HANDOFF.md` before implementation.

## 1. Current Ground

Axioms is a clean-start mathematical kernel for observing what recursive A/B can carry and where it honestly stops.

Target shape:

```
X0 --A/B--> X1 --A/B--> X2
```

The same A/B entry point must be able to receive its own evidence-bearing output without a human supplying the middle orientation.

The first bounded two-step witness is complete.

Recorded candidate: exact integer finite differences over all explicitly available binary axes, oriented `0 -> 1`.

Recorded fixture:

```
00 = 0
01 = 1
10 = 1
11 = 0
```

Recorded result:

- X1: both axis routes produce `+1, -1`
- X2: routes `a,b` and `b,a` each produce `-2`
- same `ab` entry point received X0 and X1
- X1 was directly admissible
- no adapter, new WATCH, pair selection, layer parameter, or second operator was supplied between calls
- original source nodes and signed parent references survived
- result: `SUPPORTED_TWO_STEP_NATIVE_MOVEMENT`

This is a bounded finite-difference candidate only. It is **not** identified with general A/B.

## 2. What The First Witness Actually Established

The first witness established bounded recursive admissibility:

```
X1 = A/B(X0)
X2 = A/B(X1)
```

under one declared native rule.

It did **not** establish general recursive distinction discovery.

The second contrast was already represented in X0 by the initially supplied axis set and the policy "process every remaining axis."

In the current candidate, the first pass carries forward the list of remaining axes. The second pass can therefore continue because X1 already says, in effect, which native axis remains available.

That is valid evidence for the first witness, but it leaves a sharper question open:

```
Can the next comparison be earned from relations retained inside X1
rather than from a carried schedule of future axes?
```

## 3. Evidence Rules Already Earned

The following are inherited as constraints, not as architecture:

1. Missing correspondence alone does not prove loss or gain.
2. Coverage alone does not prove distinction preservation.
3. A native comparison must be supported by the witness; do not invent one.
4. Missing required evidence remains UNKNOWN/PARTIAL rather than being normalized into a stronger result.
5. Earned zero/no-boundary is valid; absence of observed movement is not automatically evidence of zero.
6. Source/provenance needed to support a relation must survive any output that may recurse.
7. A result label by itself is not a recursively sufficient witness.
8. Replay/reconstruction of an earlier reading is not recursive closure.
9. Structural resemblance alone is not identity or continuation.
10. A code/input-contract failure is not a mathematical UNKNOWN.

## 4. Relationship to Eggy

Eggy remains frozen unless the user explicitly reopens it.

Useful prior evidence includes:

- evidence-preservation failures and fixes;
- Small Eggy accepted-prefix/restart witnesses;
- upward piece-only inspection;
- Boundary Math 0.4 W1-W5 evidence semantics;
- Boundary Math 0.5 recursive-closure diagnostics.

Port only invariants/test ideas when they answer a specific Axioms question. Do not import Eggy implementation structure.

## 5. Completed First Experiment

Local/USB evidence from the completed first witness:

- `two_step.py`
- `evidence/first.json`
- `REPORT.md`

The witness ran once and was not rerun.

The first witness remains immutable evidence for comparison with later experiments. Do not silently rewrite it to make a later experiment cleaner.

## 6. Next Authorized Seam — Experiment #2

**User has authorized the next bounded test.**

Keep the same binary-square fixture and the same integer subtraction/orientation rule.

Do **not** make the problem larger.

The only intended pressure is to remove the carried "remaining axes" list as the authority for what A/B may compare next.

### Current first-witness shape

The existing candidate effectively does:

```
X0 contains axes [a,b]

first A/B:
  choose a -> output retains remaining [b]
  choose b -> output retains remaining [a]

second A/B:
  consume the carried remaining axis
```

This demonstrates recursive execution, but the future comparison schedule is already present.

### Experiment #2 target

Retain the actual relational support instead of a future-axis schedule.

The initial square may still contain native source relations such as:

```
00 --b-- 01
10 --b-- 11

00 --a-- 10
01 --a-- 11
```

The first A/B may derive first-order movement nodes, for example along `a`:

```
d_a0 = 10 - 00 = +1
d_a1 = 11 - 01 = -1
```

Those derived nodes must retain their signed parents and enough source relation evidence to inspect them again.

On the second call, A/B must **not** read "remaining axis = b" from a carried schedule.

Instead, a relation between `d_a0` and `d_a1` is admissible only if X1 itself supports it through their parent relations. In this fixture, the support to inspect is:

```
10 --b-- 11
00 --b-- 01
```

If that common parent relation is sufficient under the candidate contract, then the second movement may be earned:

```
d_a1 - d_a0 = -1 - (+1) = -2
```

Likewise for the opposite route.

This is still a bounded numerical witness. Do not call it general A/B discovery.

## 7. Experiment #2 Constraints

Preserve the completed first witness byte-for-byte.

Do not edit `two_step.py`, `evidence/first.json`, or the original first-witness report merely to make experiment #2 pass.

Use a new isolated experiment/evidence path.

Do not add:

- a third call;
- a new fixture;
- a third axis;
- a human-selected higher WATCH;
- a planner;
- a classifier;
- a second operator;
- a layer system;
- Eggy architecture;
- TOP/psi/Meta;
- persistence/runtime machinery;
- an adapter that merely re-encodes a human-chosen next comparison.

The second comparison must be supported from relation/evidence already carried in X1.

## 8. Required Experiment #2 Outcomes

The run must distinguish:

### SUPPORTED_RELATION_CARRIED_RECURSION
X1 itself contains enough relational support for the same A/B entry point to earn X2 without a carried future-axis schedule.

### UNKNOWN / PARTIAL
The parent/source relations retained in X1 are insufficient to earn the next comparison.

### EARNED ZERO
The supported relation exists and positively earns zero/no movement.

### CONTRACT / IMPLEMENTATION LIMIT
The representation cannot express or consume the required evidence. Do not relabel this as mathematical UNKNOWN.

## 9. Experiment #2 Stop Rule

Run exactly one bounded experiment #2 witness.

STOP after the first honest result.

Report:

- exact files created/changed;
- exact command executed;
- whether the old "remaining axes" schedule is absent as an authority;
- X0 relational shape;
- X1 derived nodes and retained parent/source relations;
- the exact evidence used to admit or reject the X1 -> X2 comparison;
- X2 if earned;
- the first unsupported relation if it stops;
- whether any outside choice was supplied between calls;
- whether the result is supported movement, UNKNOWN/PARTIAL, earned zero, or implementation/contract limit.

Do not repair and rerun in the same authorized witness.

## 10. Current Question

The next bounded question is:

```
Can A/B carry the relation that makes its own next A/B admissible,
rather than carrying a schedule that names the next axis?
```

That is the active seam.


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
