# A/B chatbot — extending a witnessed path union one edge at a time

**12 October 2026 · local finite mathematical experiment**

The previous `PathUnionAgent` joined compatible rooted paths but performed no new observations. This continuation adds **`UnionEdgeExtender`**: given the union's selected partial state correspondence, examine every missing `A` and `B` transition on its mapped states and decide whether each paired transition can join the relation without changing any previously admitted pairing. Newly admitted mapped states add their outgoing transitions to the work queue. Runs are incremental and can resume after an observation allowance is exhausted.

This demonstrates *growth of a selected witnessed partial relationship*, not discovery of universally appropriate mappings or generalization to real-world movement.

## Exact observation and admission rule

For an already paired state `f(s) = t`, observing original transition `s --a--> u` and changed transition `t --a--> v` permits admitting the edge only if

- if `f(u)` already exists, it equals `v`;
- if `v` already has a known preimage, that preimage is `u`;
- both transitions replay on the **same pinned snapshots**, with local owner checks where a loopback owner is genuinely bound.

When either pairing condition fails, the agent records an explicit rooted pair of action words whose endpoints are equal on one side and unequal on the other. It **never removes, overwrites, or silently reassigns** a previously admitted pair. Candidate edges are considered in deterministic queue order (initial old states sorted, `A` before `B`; add new states as encountered). It is a **greedy** extension of one preselected union. Changing order or starting union may admit a different partial graph; no global optimality is claimed.

## Reproduced cases

With original `FiniteSystem((0,0,1))`, changed `FiniteSystem((0,0,0))`, and an initial root-only union:

| Measurement | Initial | After edge investigation |
| --- | ---: | ---: |
| Paired states | 1 | **9** |
| Admitted A/B edges | 0 | **15** |
| Excluded incompatible A/B edges | 0 | **3** |
| Unique source-side / changed-side edge observations | 0 / 0 | **18 / 18** |

Status: `PARTIAL_EXTENSION_WITNESSED` because 3 outgoing edges cannot join this pairing. Each exclusion carries a replayable differing word-equality witness. For example, `BA` and `ABB` have unequal endpoints in the original law and equal endpoints under the changed law.

**Same-law control:** starting again from the root with both systems `FiniteSystem((0,0,1))`, the extension reaches all **27 states and 54 A/B edges** per side with no exclusions. Status: `ROOTED_CLOSED_WITNESSED`. This is closure of the **root-reachable component in this declared finite 27-state law**. It is not a claim about arbitrary spaces, physical data, language, or A/B itself.

**Preserving a larger initial union:** starting from the previously selected two-goal union found at branch depth 7, the agent retains every existing paired state and every existing admitted edge, adds 3 compatible edges, and returns a 9-state / 12-edge partial graph with 6 explicitly excluded edges. Those numbers depend on the chosen initial union and are not a universal restriction size.

## Evidence handling and limits

- Accepts a completed, audited `PathUnionAgent`; it does not invent a pairing as input or sidestep branch-history validation.
- Retains the original selected words, union edges, newly admitted edges, and all excluded-edge witnesses.
- Rechecks old path history, accepted edges, goal-transported state words, and rejected word-equality witnesses on each continuation call.
- A repinned source becomes `UNKNOWN_VERSION`. Missing or tampered cached evidence becomes `WALL_OBSERVATION`. A per-source capacity exhaustion becomes `UNKNOWN_BUDGET` and can resume **only after the caller explicitly increases its budget**.
- Reports `CONTINUING` when the **per-call** observation allowance is exhausted, including when one side is observed but the paired side is still pending. It never spends more than that allowance on new edge queries.
- Untrusted remote observations are `*_REMOTE_REPORTED`, never `*_WITNESSED` merely because source labels match.
- `ROOTED_CLOSED_*` is reported only if **all** outgoing edges of all admitted states have been investigated and **none** excluded. In a finite reachable component this is an action-closed rooted correspondence for the chosen pairing, not proof of a full-system bijection if unreachable states exist.
- A rejected edge is an obstruction **within this mapping**. Another initial union or a non-greedy search may admit it.

## Files and commands

New files only: `ab_chatbot_union_extension.py`, `test_ab_chatbot_union_extension.py`, `run_union_extension_demo.py`, `UNION_EXTENSION_README.md`, and `REGRESSION_RESULTS.txt`. All 50 files in the preceding zipped package remain **byte-for-byte unchanged**.

```bash
python run_union_extension_demo.py
python -m unittest test_ab_chatbot_union_extension -q
# Test modules individually if all-module discovery stalls in local HTTP fixtures:
for f in test_ab_chatbot_*.py; do
    python -m unittest "${f%.py}" -q || exit 1
done
```

**Local verification:** 15 new focused tests passed. Separate completed unittest runs across the **20 modules** report **312/312 passing tests** (297 prior plus 15 new). The independent reference computes transition closure directly from `FiniteSystem.step` for three rule-change pairs, not from the extension's output. See `REGRESSION_RESULTS.txt` for per-module results. A grouped run was interrupted; it is **not** counted in these totals. There is no GitHub commit, deployed service, hosted CI result, physical-world data collection, or unrestricted mathematical generalization.

## Next investigatory boundary

Presently the extender commits to the first compatible edge along its deterministic queue and does not reconsider that choice. A next narrow experiment would retain **alternative extension branches** when a new pairing decision is not forced, then compare which complete declared goals each branch can carry, with negative controls to prevent conflating alternatives.
