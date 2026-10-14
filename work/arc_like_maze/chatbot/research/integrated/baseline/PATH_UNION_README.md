# A/B chatbot — bounded discovery of jointly usable path restrictions

**October 12, 2026. Local research prototype.** No GitHub write, deployment, physical-motion validation, or universal mathematical claim.

## What was tested

The previous `BranchDiscoverer` enumerates separately valid rooted A/B action paths (within a declared depth). A separate path being self-consistent does **not** mean it can be combined with another path: one original state must have one changed-state image, and different original states must have distinct changed-state images.

This experiment adds `PathUnionAgent`, which **takes the existing completed branching history** and constructs a candidate pool of independently observed goal paths. The candidate words and coordinate pairings are not specified to the new agent. It searches **every subset of its explicitly bounded candidate pool** and merges paths only if:

1. Every original state has just one target image (`source` functional consistency).
2. Two original states never collapse to the same target state (injectivity).
3. Every admitted A/B-labeled edge from every selected path has matched mapped endpoints in both versions.
4. All underlying path evidence still replays using pinned source revisions and locally bound owners, where available.

Accepted edges form a **partial generator-labeled graph correspondence on a union of rooted paths**; this makes the partial relationship reusable for more than one completed goal. **No closure under unobserved A/B edges is asserted.** It is not a largest possible restriction of either system, full conjugacy, physical coupling, or generalized autonomous theorem proving.

## Reproducible examples

Original finite law: `FiniteSystem((0, 0, 1))`, changed finite law: `FiniteSystem((0, 0, 0))`, root `(0,0,0)`, initial branch search depth 7. The completed branch search reports 142 valid prefixes and 25 rejected attempted extensions. Both observers use independent locally bound loopback sources.

**Compatible path union** (one shortest path candidate per declared goal):

| Declared original-side goal | Path discovered from branch history | Changed-side destination |
| --- | --- | --- |
| `(0,1,1)` | `ABBAA` | `(0,1,0)` |
| `(2,2,0)` | `ABA` | `(2,2,0)` |

The candidate paths jointly admit **7 state pairs and 6 distinct labeled edges**. Both goals remain reachable through the admitted union. Each route is replayable; the new agent was never provided the words `ABBAA` or `ABA` as target answers.

**Incompatible path union** (also using one candidate per goal):

| Goal | Individually admitted path | Pairwise union |
| --- | --- | --- |
| `(0,1,1)` | `ABBAA` | Cannot be merged with `B` |
| `(0,1,0)` | `B` | Cannot be merged with `ABBAA` |

The replayable separating equality is **`ABBAA` versus `B`**: they end at *different states* under the original law, but at *the same state* under the changed law. Mapping both original states to one changed state would violate injectivity. The agent returns `PARTIAL_UNION_WITNESSED`, not a successful two-goal completion. A rejection in this pool **does not** rule out another map, other paths, or another depth bound.

The demo's full discovery and two zero-read unions consumed **30 original-side and 18 changed-side unique edge observations**, including cached observations. Path union itself performs **zero new edge queries**: it audits and replays existing pinned evidence.

## Selection and limits

The tool accepts one or more distinct original-side goal states and selects up to `variants_per_goal` previously discovered paths for each; paths are ordered shortest-first, then alphabetically. Candidate selection interleaves goals rather than taking all the options for the first goal. `max_candidates` limits the finite pool (maximum 16) and `candidate_pool_truncated` reports whenever the selected options exceeded that limit.

Within this selected pool, all nonempty subsets are tested. The deterministic objective is: (1) maximize the number of declared goals carried, (2) maximize number of distinct witnessed labeled edges, (3) maximize distinct paired states, (4) minimize number of paths. No general optimality outside this candidate pool is inferred. If some goals are missing, the result is `PARTIAL_UNION_*` with an explicit carried-goal count. The report also retains replayable pairwise incompatibilities and alternative images seen among separately valid subsets achieving the highest coverage; such alternatives need **not** coexist with the chosen subset.

Statuses preserve provenance: `UNION_WITNESSED` / `PARTIAL_UNION_WITNESSED` require both locally bound owners, otherwise `_REMOTE_REPORTED`. Other states include `DISCOVERY_INCOMPLETE`, `UNKNOWN_VERSION`, `WALL_OBSERVATION`, and `GOALS_OUTSIDE_CANDIDATES`.

## Files and reproduction

- `ab_chatbot_path_union.py` — no-read path-union selection, witness-preserving conflict reports, deterministic multi-goal objective.
- `test_ab_chatbot_path_union.py` — 15 new tests, including an independent powerset oracle for three law pairs, replayable obstructions, finite search limits, forged cache, remote provenance, repins, and zero-read behavior.
- `run_path_union_demo.py` — produces the compatible and incompatible examples above.

```bash
python run_path_union_demo.py
python -m unittest test_ab_chatbot_path_union -q
# Separate-module regression to avoid counting incomplete test discovery:
for f in test_ab_chatbot_*.py; do
    python -m unittest "${f%.py}" -q || exit 1
done
```

Only the new files are required for this continuation; original files are unchanged.

## Next open boundary

A bounded candidate pool can produce a usable joined partial graph, but the search still starts from a declared original-side goal and already-discovered finite paths. A subsequent experiment could **generate additional paths specifically where the current partial union is missing a needed edge**, and rerun admission with a budget and independent replay. That has not yet been demonstrated here.

## Completed local verification

**297/297 unittest tests passed across 19 modules** (282 pre-existing and 15 new), executed in independent module runs. The full-suite result is recorded in `FULL_REGRESSION_LOG.txt` in the working directory, and all 46 pre-existing files were checked byte-for-byte unchanged. A runnable local demo independently reproduced both the successful union and the collision. No hosted CI or external/physical testing was performed.
