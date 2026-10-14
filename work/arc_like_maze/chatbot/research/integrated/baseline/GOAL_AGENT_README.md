# A/B chatbot — bounded constructive goal loop

**Status:** Local repair and new goal-driven experiment, October 12, 2026.

**Referent:** The language-level A/B investigation remains distinct from the *particular* finite mathematical models in these scripts. This agent does not define A/B, model the in-between universally, or establish a physical theory of motion.

## What's new

1. **Controlled completion condition:** Caller specifies a destination in the existing 27-state `F3^3` model. The agent searches for an observed A/B action word that reaches it from a declared start state.
2. **Agent-generated next questions:** Breadth-first search chooses which `(state, action)` transition to observe; no LLM selects an action word, and no predicted edge is accepted as witnessed without observation.
3. **Retained evidence and re-entry:** Cached edges from `LanguageBridge` are reused by the next task. A completed task's final state can be the next task's starting state on the same pinned version. Each call observes at most a caller-chosen number of new transitions.
4. **Explicit completion and failure:** `COMPLETE_WITNESSED` carries a replayed shortest path under a controlled, bound local observer. `COMPLETE_REMOTE_REPORTED` keeps unverified external observations separately labeled. `NO_ROUTE_WITHIN_DEPTH`, `UNREACHABLE_CLOSED_COMPONENT`, `UNKNOWN_BUDGET`, `UNKNOWN_VERSION`, and `WALL_OBSERVATION` remain separate statuses.
5. **Provenance fix:** Providing `owner` and seeing matching revision/digest/source labels is no longer enough for `LOCAL_OWNER_VERIFIED`. A `RemoteObserver` must be explicitly bound to an active `LoopbackHTTP` in-process handle with the identical owner object and URL. Each returned edge must match that source-owned immutable view. This is *not* a general authentication mechanism for outside servers.

## Run a completed task

Place the `.py` files together and use Python 3.11+ (standard library only).

```sh
python ab_chatbot_goal_agent.py --target 1,2,2 --budget 12 --per-call 2
```

Observed sample:

```text
CONTINUING: states=3, edges=2, version=0
COMPLETE_WITNESSED: states=5, edges=4, version=0
WITNESSED ACTIONS: AB
STATE PATH: (0, 0, 0) -> (1, 0, 0) -> (1, 2, 2)
```

The action word `AB` was **not** supplied to the search routine. The task and finish condition were supplied. All reported path edges were read from the pinned source and replayed.

## Loop through tasks using the same observation cache

```python
from ab_chatbot_goal_agent import GoalAgent

# `bridge` is an existing LanguageBridge over the same pinned source.
first = GoalAgent(bridge, target=(1, 2, 2))
result = first.advance(max_new_edges=4)
while result.status == 'CONTINUING':
    result = first.advance(max_new_edges=4)

if result.status == 'COMPLETE_WITNESSED':
    second = GoalAgent(bridge, target=(1, 1, 0), start=result.path.states[-1])
    second_result = second.advance(max_new_edges=4)
    # Continue second only while second_result.status == 'CONTINUING'.
```

This uses the existing observer, not a separate mathematical engine. The destination and verification conditions can change between completed tasks while the pinned evidence remains useful.

### Mathematics of this narrow completion

Breadth-first search on a finite directed graph with unit-cost labeled A/B edges is complete for the declared 27-state model if the observer is stable/coherent and every needed outgoing edge can be queried. A successful path is shortest in action count. If all reachable outgoing edges have been observed without reaching the destination, the destination is unreachable from that starting state under those A/B actions. The maximum number of distinct required observations is `2 * 27 = 54`; earlier cached observations are never read again by the ordinary loop.

This **does not** prove general completion for unknown/infinite mathematical structures, physical systems, unobserved source changes, arbitrary natural language, or every possible user task. Finite observations alone cannot determine a completely unrestricted unknown transition law.

### Evidence gates

- **Goal and domain:** The task accepts a start and destination from the declared 27 states. No unknown action is invented.
- **Observer:** The target is a fixed historical mathematical version; changing `LanguageBridge.snapshot` causes `UNKNOWN_VERSION` rather than silently continuing on a new version.
- **Budget:** Per-call new transition limit defaults to four, and a separate total edge cap exists on the pinned observer. Reaching either does not imply failure of the mathematical question. Raising the total cap requires calling `authorize_total_edge_budget(new_max)` explicitly.
- **Trust:** A reachable path from an unbound remote observer yields `COMPLETE_REMOTE_REPORTED`, not locally verified origin. Even a correctly bound local test is not third-party source authentication.
- **No artificial A/B closure:** The code does not classify this finite BFS operation as the definition of A/B's moving referent.

## Regression tests

```sh
python -m unittest -q test_ab_chatbot_goal_agent
python -m unittest -q test_ab_chatbot_language_bridge
```

The full local collection contains 13 test modules. In the latest independent runs, **214 tests passed** across those modules (original 198 plus 14 goal tests and two source-verification tests). The modules were executed separately; a previous monolithic discovery run exceeded its time allowance and is not used as evidence of a finished combined run. Independent results do not certify deployment or external benchmarking.

## Next admissible expansion

A practical next extension is another **declared completion contract** (for example, witnessing a specified relationship pattern or finding a counterexample), using the *same* observation source, provenance rules, cache, and bounded continuation contract. That expansion must be justified by the actual goal rather than forcing the original referent into a newly invented engine.

**Repository:** These modifications are a local working copy only. Neither the mathematical repository nor the public profile was edited by this task.
