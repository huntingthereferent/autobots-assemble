# Multiple explicit mathematical preservation requirements

**Date:** 2026-10-12  
**Referent:** Continue the existing finite A/B chatbot, giving it a task contract that can explicitly require several labeled edges to survive in **one** replayed partial correspondence. This is a scoped finite software experiment. A/B as relational language is not defined by these toy generators.

## User-facing task grammar

Accepted narrow text:

```text
goals: (0,1,1), (0,2,0); require: edges (0,0,0) B, (0,1,0) B
```

Equivalent structured input:

```json
{
  "goals": [[0,1,1],[0,2,0]],
  "required_edges": [
    {"state":[0,0,0],"action":"B"},
    {"state":[0,1,0],"action":"B"}
  ]
}
```

`read_multi_task` admits 2–8 **distinct** explicit edges and 1–8 distinct goals. Unknown task text returns `UNKNOWN_TASK` without observing either system; malformed schema, duplicate requirements, unknown keys, or combined singular/plural keys are rejected. The original goals-only and singular `required_edge` inputs are dispatched to the **unchanged** existing task/portfolio layer. State coordinates are elements of `F_3^3`. Accepted input preserves the original form, declaration channel, explicitly normalized edges, and deterministic SHA-256 contract fingerprint; this digest is not proof of source authenticity.

## Required-edge conjunction

`MultiRequiredEdgePortfolio` composes the existing `BranchDiscoverer` → `PathUnionAgent` → `UnionEdgeExtender`, with `inspect_required_edge` over every declared edge. Zero-read preflight can prune a *seed union* only where pinned local owner observations contradict that candidate's **already assigned** paired state relation. It retains a separate `ExclusionCertificate` for every contradictory requirement, replayed on each advance. Missing evidence is `UNDECIDED` and cannot authorize pruning. Remote reports do not acquire local-owner authority.

After each candidate is extended and replayed, the winner is selected **only from candidates admitting the entire required-edge set**. No subset of the requirements is quietly discarded. If none of the completed bounded candidates proves the conjunction, the status is `REQUIREMENTS_UNPROVED`, not "inconsistent in all mathematical models" or "no solution". The report withholds a selected solution and retains which requirements were missing per candidate. Original goal coverage remains a separate quantity, and a feasible partial-goal result cannot be mislabeled full-goal completion.

Revision changes return `UNKNOWN_VERSION`. Corrupted cached observations or saved exclusion witnesses return `WALL_OBSERVATION`. The existing observation-budget and zero-read replay conditions remain in force.

## Reproduced finite results

Original `FiniteSystem(phi=(0,0,1))`, changed `FiniteSystem(phi=(0,0,0))`, both independently pinned under their local owners. Root `(0,0,0)`, goals `(0,1,1)` and `(0,2,0)`, search depth 6, variants per goal 4, candidate limit 7, trial limit 12:

| Explicit must-admit edges | Candidate extensions before → after | Individual contradiction certificates | Goal result | Old + new owner observations |
|---|---:|---:|---|---:|
| root B and `(0,1,0)` B | 11 → 9 | 2 | Partial 1/2 goals, **both requirements met** | 26 + 18 |
| root B and `(1,2,0)` B | 11 → 7 | 4, from two distinct required edges | Partial 1/2 goals, **both requirements met** | 26 + 18 |
| root B and `(0,0,1)` A | 11 → 9 | 2 | `REQUIREMENTS_UNPROVED` within this pool | 26 + 18 |

The third row is *not* proof that no other partial correspondence could satisfy those requirements. The first row's selected result matches the earlier one-required-edge baseline with the additional compatible required edge. Identical-law testing independently verifies both goals and both requirements across 27 paired states and 54 admitted edges.

The finite standalone `finite_multi_required.py` replays the fixed candidate word tuples under complete specified finite laws, independently checking **11 → 9** and **11 → 7**, including the two separate counterexample sources. It is an arithmetic oracle, not a replacement for the HTTP-pinned integration or a claim of independent human measurements.

## Reproduce

From this directory:

```bash
python run_multi_required_demo.py
python -m unittest -q test_ab_chatbot_multi_required
python -m unittest -q test_finite_multi_required
python -m unittest -q test_ab_chatbot_task_contract test_ab_chatbot_evidence_prefilter test_finite_explicit_task
```

Completed runs in this session: **13/13** new integrated tests; **4/4** new independent finite controls; **11/11** prior explicit-task tests; **8/8** prior required-edge tests; **4/4** prior standalone explicit-task tests; **3/3** selected post-extension, union-edge, and path-union regression tests. **43 tests passed**, counted only from completed runs. One larger grouped legacy run exceeded its execution time and is not counted. The entire historical suite was not rerun, and GitHub Actions was not verified.

**Preservation:** All 115 previous package files remain byte-for-byte unchanged; only this new layer, tests, demo, report and independent oracle were added. The full chatbot is a downloadable local package, while GitHub receives only the separately runnable finite research witness and its limitations. The unrelated Continuity `state/current.json` pointer must stay unchanged.

**Next boundary:** Allow requirements to express other **explicit** relations (e.g. final-state and history-preservation obligations) with a typed schema, without deriving constraints from vague language. Validate each against its native witness, compare resource costs on held-out finite cases, and preserve unsupported obligation types as `UNKNOWN`.
