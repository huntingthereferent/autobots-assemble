# A/B chatbot — reusable restricted correspondence under changed rules

**Date:** October 12, 2026  
**State:** local, independently exercised finite mathematical extension; not committed or deployed.

## Question

The earlier finite rule-change experiment found preserved word equalities and a
broken equality (`BA == ABB` in the old law but not in the changed law). It
stopped at the obstruction. Can the chatbot *continue past that obstruction*,
retain only a coherent restricted relationship, and then complete a new task
using that relationship, instead of declaring the entire comparison failed?

**Scope:** In these examples `A` and `B` are declared operations on `F_3^3`
(27 states). They do not define the investigator's broader language-level A/B,
any general law of physical motion, or an unconstrained autonomous chatbot.

## New module

`ab_chatbot_restricted_rule_transport.py` introduces `RestrictedRuleTransport`.
It uses the existing two independently pinned `LanguageBridge` observers, the
existing edge cache and owner-verification contract, and existing goal reports.
It does not read the unknown transformation law directly or accept a prefilled
coordinate mapping.

Its self-directed *bounded* discovery does this:

1. Pair the declared roots, then visit discovered pairs in BFS order, trying
   the two action labels `A` and `B`.
2. Observe actual edges in **both** pinned systems under the combined per-call
   edge budget. Previously queried edges are reused.
3. Admit a transition if it extends or agrees with an injective mapping of the
   paired states. If its endpoint conflicts with that mapping, **exclude the
   transition**, recording a replayable two-word equality obstruction.
4. Once all outgoing edges of the admitted states have been considered,
   independently replay all admitted edges **and** excluded counterexamples,
   including owner checks for locally bound data.
5. For a user-selected source-side destination, plan a route along only
   admitted edges, replay it on both pinned systems and return a transported
   destination. Carrying a prior source-side `GoalReport` first checks its
   evidence, but **replans** if the old path crosses a rejected edge.

The result is a rooted **partial labeled graph isomorphism** (a partial-action
relation) for a chosen root and BFS admission order. It is deliberately **not**
asserted to be unique, maximum-size, generator-closed on its vertex carrier,
or sufficient for all goals. A denied arc is excluded **under this chosen
pairing**, not mathematically impossible under every alternative restriction.
A goal outside the admitted graph is `GOAL_OUTSIDE_RESTRICTION`, **not** globally
unreachable.

## Exact controlled example

Old finite law: `FiniteSystem((0,0,0))`.
Changed finite law: `FiniteSystem((0,1,2))`.
Both are pinned, explicitly local-owner-bound HTTP observer instances with
independent source identity/version; coordinate labeling is unchanged.

```text
Restriction: RESTRICTED_SUBGRAPH_WITNESSED
Mapped state pairs: 9
Admitted generator arcs: 12
Excluded generator arcs: 6
Original unique edge observations: 18
Changed unique edge observations: 18

Source task: reach (0,2,0)
GoalAgent's original answer: BB (COMPLETE_WITNESSED)
Restricted transported result: BB (GOAL_CARRIED_WITNESSED)
Old endpoint: (0,2,0)
Changed endpoint: (0,2,1)
The subsequent action B from those paired endpoints returns to root
  old: (0,0,0)
  changed: (0,0,0)
```

The route `BB` and its coordinate correspondence were not handed to the
transport agent. The goal target was declared; the allowed route and image
were discovered from edge observations.

**Important negative control / replanning:** The old system sends both `BA`
and `ABB` to `(1,1,0)`; the changed system sends `BA` to `(1,1,0)` but `ABB`
to `(1,1,2)`. A legitimate old-law witness `ABB` therefore cannot be carried
unchanged. The new agent admits `BA`, excludes `ABB` and returns `BA` as the
replanned way of reaching the paired goal. It does not promote source-side
endpoint equality into an unwarranted cross-law equivalence.

## Safeguards and limits

- Incremental per-call edge limits, including zero and one, and a separate
  underlying pinned total edge limit that is **never silently increased**.
- `UNKNOWN_NOT_CERTIFIED` until the comparison's finite partial-graph audit
  completes; `UNKNOWN_BUDGET` when the authorized owner-observation budget is
  exhausted. Existing observations survive continuation.
- `UNKNOWN_VERSION` after repinning; no cross-version transport.
- A forged cached **admitted or excluded** edge invalidates the audit.
- Prior `GoalReport` documents are not trusted by themselves: they must replay
  against original pinned observations and match pinned identity/scope.
- Unbound HTTP sources return `*_REMOTE_REPORTED`, never owner-verified claims.
- Identical laws and genuine nonlinear relabelings are accepted as **rooted**
  correspondence without spurious exclusion; the comparison asserts nothing
  about unvisited states or physical-world applicability.
- The choice of partial graph is greedy/deterministic relative to the declared
  BFS ordering; it does not search all potential subgraphs or prove optimality.
- The system still uses a fixed two-generator finite grammar, predeclared goal
  format and external stopping criteria. It does not autonomously invent a
  general completion condition or independently generalize beyond these
  mathematical models.

## Tests / reproduction

Python 3.11+, standard library only. Unzip the package and from its folder:

```sh
python ab_chatbot_restricted_rule_transport.py
python -m unittest -q test_ab_chatbot_restricted_rule_transport
```

**Verification:** 15/15 new focused tests. The earlier 239 tests across the
original 15 modules were individually/batched rerun and passed; total
**254/254 across 16 modules**. The monolithic suite was interrupted by a
runtime timeout; that interrupted execution has **not** been counted as a
passing result. No GitHub CI, deployment, physical test, or external provenance
attestation occurred.

## Suggested next mathematical question

Can the bot **choose between two admissible restricted correspondences** based
on a goal it is trying to complete, while preserving exact replay and
reporting when no sufficient evidence selects one? The current algorithm
constructs one BFS-priority restriction and does not optimize for goal coverage.

**No repository changes made.**
