# A/B chatbot — goal-selected partial rule correspondence

**Local experiment:** October 12, 2026. No GitHub writes, deployment, or physical coupling claims.

## Question

A prior locally witnessed finite example used one greedy breadth-first restriction to carry previously completed A/B goals across a rule change. That restriction was not unique or guaranteed optimal. Can the existing bot **construct more than one usable partial pairing**, select one for the declared goal, and explicitly retain the competing answer and the negative cases?

## Scope

The toy systems have 27 states in `F_3^3` and two named operations, `A` and `B`. A/B in this program are **labels of declared finite operations**, not a definition of James's language-level A/B or of physical movement. Two trial strategies are deliberately bounded: `BFS_AB` and `DFS_BA`. They do **not** enumerate all possible partial correspondences or prove that one choice is maximal.

## Files

- `ab_chatbot_restricted_rule_transport.py`: backward-compatible addition of configurable frontier (`BFS`/`DFS`) and action (`AB`/`BA`) admission order. The original defaults remain `BFS` and `AB`.
- `ab_chatbot_goal_selected_restrictions.py`: new goal-based chooser. It constructs both restrictions incrementally from **two independent pinned observers**, reuses cached observations, audits admitted and excluded arcs, and selects the shortest admitted goal route among those two candidates. A final selection requires both candidates to complete their own audits.
- `test_ab_chatbot_goal_selected_restrictions.py`: 15 focused tests, including 27 target goals in each of three distinct law-change pairs, checked against a separate oracle directly applying the finite rules. Tests also cover stale versions, forged caches, remote-vs-owned provenance, budgets, and alternate destination images.
- `run_goal_selected_demo.py`: stand-alone reproducible loopback demonstration.

## Working contrast

Pinned systems: old `FiniteSystem((0,0,1))`, changed `FiniteSystem((0,0,0))`. Roots in both systems: `(0,0,0)`.

| Old-side requested target | `BFS_AB` | `DFS_BA` | Selected |
| --- | --- | --- | --- |
| `(1,1,1)` | Outside this restriction | Admitted `ABB`; changed-side endpoint `(1,1,0)` | `DFS_BA` |
| `(1,1,0)` | Admitted `BA`; changed-side endpoint `(1,1,0)` | Outside this restriction | `BFS_AB` |

The first goal run used 22 distinct old-side and 18 distinct changed-side observations. The second reuses the same cached observations. Neither required a pre-supplied route or pre-supplied state pairing. The goal itself **is** supplied, and the choice is between **these two algorithms only**.

### Non-uniqueness control

For old `FiniteSystem((0,0,0))` and changed `FiniteSystem((0,0,1))`, old target `(1,1,0)` is admitted by both restrictions:

- `BFS_AB`: route `BA`, changed image `(1,1,0)`.
- `DFS_BA`: route `ABB`, changed image `(1,1,1)`.

The program selects the shorter tested route `BA` but **reports both images** and states that this is not a uniquely proved correspondence. A different legitimate partial pairing can change the target image.

## Result types

- `GOAL_SELECTED_WITNESSED`: route replayed against **both locally bound owners** and both candidates passed their individual audits.
- `GOAL_SELECTED_REMOTE_REPORTED`: route is reported from at least one unverified remote observer and is **not** promoted into local-owner verification.
- `GOAL_OUTSIDE_TESTED_RESTRICTIONS`: neither of these two completed candidate restrictions admits the target; **not** a universal unreachability proof.
- `UNKNOWN_BUDGET`, `UNKNOWN_VERSION`: insufficient observations or invalidated pin; not a mathematical impossibility claim.
- `WALL_OBSERVATION`: cached evidence failed a witness or local owner consistency check.
- `CONTINUING`: the current incremental step has not finished.

### Verification

**269 individual tests passed across 17 independently executed test modules**: 254 earlier tests plus 15 new ones. One whole-suite discovery invocation timed out without a verdict; it is **not** counted as a pass. Each module was separately executed to completion and passed. The 15 new tests were rerun after the final ambiguity handling change.

The direct independent oracle sweep compared the selected candidate, path word, target image, and reachable-goal status across all **27 goals for three different law pairs**. This is finite family testing, not evidence for unrestricted mathematical generalization.

## Reproduce

From the extracted package directory:

```bash
python run_goal_selected_demo.py
python -m unittest test_ab_chatbot_goal_selected_restrictions -q
python -m unittest test_ab_chatbot_restricted_rule_transport -q
```

To recheck all modules individually (helps where one combined discovery invocation times out):

```bash
for f in test_ab_chatbot_*.py; do python -m unittest "${f%.py}" -q || exit 1; done
```

No GitHub files have been modified. This remains a **bounded mathematical software construction**. The next unresolved step is discovering richer families of candidate restrictions, rather than assuming these two search orders exhaust the possibilities.
