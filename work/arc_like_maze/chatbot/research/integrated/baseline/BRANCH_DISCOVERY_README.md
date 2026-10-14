# A/B chatbot — bounded branching discovery of path restrictions

**Local executable experiment (October 12, 2026).** No GitHub commits, deployment, or physical motion claims.

## What changed

The prior `GoalSelectedRestrictions` compares two deterministic greedy partial correspondences, `BFS_AB` and `DFS_BA`. Neither is exhaustive. This experiment adds `BranchDiscoverer`, an **independent bounded search of rooted A/B action paths**. It generates its own words and constructs a partial state pairing from paired observed transitions along each admitted path.

At each extension, the agent checks whether a newly reached old state would acquire two different new images or whether two different old states would collapse to one new image. If either happens, that *branch* is rejected. The rejection includes two explicitly replayable action words witnessing an endpoint equality on exactly one side of the changed rules. It does **not** prohibit the edge in every possible correspondence or prohibit other branches.

The search continues along other consistent prefixes, with depth bound `max_depth` (default 7, supported 0–8). All candidate restrictions are **path-level partial labeled correspondences**. Off-path edges remain unexamined by that candidate; we do **not** claim a full rooted conjugacy, maximal restriction, exhaustive collection of all partial graph isomorphisms, or universal generalization.

## Reproduction: a goal unavailable to the two-strategy chooser

- Original pinned law: `FiniteSystem((0, 0, 1))`
- Changed pinned law: `FiniteSystem((0, 0, 0))`
- Common roots: `(0,0,0)`
- Declared original-side goal: `(0,1,1)`

The earlier two-strategy chooser returns `GOAL_OUTSIDE_TESTED_RESTRICTIONS`, which is only a statement about its *two* tested maps.

The new branch discoverer, with `max_depth=7`, discovers the action word **`ABBAA`** and independently replays:

| Step | Original | Changed |
| --- | --- | --- |
| root | `(0,0,0)` | `(0,0,0)` |
| A | `(1,0,0)` | `(1,0,0)` |
| B | `(1,2,0)` | `(1,2,0)` |
| B | `(1,1,1)` | `(1,1,0)` |
| A | `(2,1,1)` | `(2,1,0)` |
| A | `(0,1,1)` | `(0,1,0)` |

The demo finds **three** distinct accepted goal paths within its seven-step bound and retains **25** rejected attempted extensions with their own word-relation witnesses. One rejected extension compares the empty word with `BBB`: endpoints differ in the original system and agree in the changed system. Running the demo *after* the two-strategy chooser reuses the existing pinned observations; the combined demonstration used **30 old-side and 18 changed-side unique transitions**. These counts are **not** all additional observations attributed to the new branch agent.

## Status and evidence boundaries

- `GOAL_CARRIED_WITNESSED`: at least one complete, admitted goal path exists under the depth bound; all edges replay against explicitly bound local owners.
- `GOAL_CARRIED_REMOTE_REPORTED`: path evidence is reported by at least one unverified remote observer; it is **not** local-owner verification.
- `GOAL_OUTSIDE_SEARCH_BOUND`: the declared goal had no self-consistent path of at most the chosen number of steps; does **not** mean globally unreachable.
- `CONTINUING`: additional paths or observations remain under the current per-call allowance.
- `UNKNOWN_BUDGET`: pinned observer exhausted its separately declared total unique-edge budget; can resume after an explicit budget change.
- `UNKNOWN_VERSION`: a source's pinned revision changed; prior evidence is not carried over.
- `WALL_OBSERVATION`: replay or local-owner consistency failed; no certified goal is returned.

The selected route is the shortest discovered admitted word, breaking ties lexicographically. All other candidate paths and **alternate target images** remain in the report. A selected route is not a uniquely determined mathematical correspondence.

The program still relies on a given finite system and goal; it does not invent the semantics of A/B, solve arbitrary mathematics, or attest any physical coupling.

## Files

- `ab_chatbot_branch_discovery.py`: resumable branching path search, admitted prefix histories, rejection witnesses, version/owner/budget checks, and goal selection.
- `test_ab_chatbot_branch_discovery.py`: **13 focused tests** including an independent finite-law enumerator of every consistent path up to depth 7 for three law pairs and comparison over all 27 destination states; provenance, observations, negative cases, forged caches, and repins.
- `run_branch_discovery_demo.py`: executable comparison against the previous two-strategy result.

No pre-existing chatbot source file was modified. The prior two-strategy chooser remains available as a separate method.

## Verification

**282/282 tests passed in 18 individually run unittest modules** on this local copy: 269 existing tests plus 13 new focused tests. The full new focused module passed separately (`Ran 13 tests`), and every earlier module was rerun individually to completion. No hosted CI or external physical test was run.

```bash
python run_branch_discovery_demo.py
python -m unittest test_ab_chatbot_branch_discovery -q
for f in test_ab_chatbot_*.py; do
    python -m unittest "${f%.py}" -q || exit 1
done
```

## Next unresolved mathematical step

This experiment enumerates **self-consistent path restrictions**, not all possible useful **branched** partial subgraphs. A next test could combine individually admitted paths into one correspondence and verify whether their shared states and edges remain consistent. A union cannot be presumed valid just because each individual path was valid.
