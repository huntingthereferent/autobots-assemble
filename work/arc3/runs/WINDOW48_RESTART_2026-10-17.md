# ARC-AGI-3: restart on the ORIGINAL 48-law marked F3 window

**Research date:** October 17, 2026 in America/Chicago (GitHub Actions logged October 18 UTC). This record supersedes the former nine-law **model choice**, not its preserved observations.

## Mathematical source and reproducibility

- [Authoritative mathematical source](../../arc_like_maze/window_combined.py) and [classification proof](../../arc_like_maze/WINDOW_COMBINED.md), not the nine-world phi source.
- [Active official single-file ARC entry](../agent/my_agent.py); [source-conformance and negative tests](../../../network/tests/test_arc3_f3_agent.py).
- [Historical nine-law source](../archive/nine_law_agent_2026-10-17.py) and [historical regression](../../../network/tests/test_arc3_nine_law_archive.py).
- [Passing original 48-law conformance workflow](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39092608522). The canonical file was then updated to stop before an extra unsupported native action; the PR checks retest the final revision.

The source family is k∈{0,1,2,3}, pulse e∈{0,1}, balance t∈{0,1}, nonlinear shear coefficient c∈{0,1,2}: **48 distinct mathematical transition tables**.

Source proof: **14 full-state labeled conjugacy classes**, but **16 marked-origin/root-preserving classes**. In support k=0 or 3 with pulse e=1, differences in balance t can admit a full-state *nonrooted* conjugacy which MOVES the marked origin, and the source supplies rooted word obstructions. Do not turn a full-state but origin-moving correspondence into a rooted ARC match.

The new single-file agent's 48 formulas, forward steps, inverse steps and rooted words are independently checked against all 48 CombinedWorld sources at all 27 depth-three states for both A and B. The original nine-world source and regression remain in the historical archive.

## First actual native test of the new entry

- [Native GitHub Actions run #39092926137](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39092926137) **passed**.
- [Original native frames and JSON source-law evidence](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39092926137/artifacts/12123436178), retained in GitHub Actions for 14 days.
- [Official native experiment runner](../native_smoke.py), same canonical agent for all three public games, official arc-agi Arcade NORMAL runtime. No saved winning routes, fake game simulation, local game source inspection, or model color reduction.

| Game | Native source action interface | Actions executed | Levels completed | Result |
| --- | --- | ---: | ---: | --- |
| SK48 | Directional/simple actions incl. 1 and 2 | **6** | 0 | No direct rooted 48-law match for provisional ACTION1=A, ACTION2=B |
| LS20 | Directional/simple actions incl. 1 and 2 | **6** | 0 | No direct rooted 48-law match for provisional ACTION1=A, ACTION2=B |
| FT09 | **Only coordinate-parameterized ACTION6** | **0** | 0 | Native frame and allowed-action list recorded; no A/B pair inferred and no click invented |

**Exact common mathematical obstruction in the first two games:**

All original 48 mathematical worlds have A³=id. Therefore the rooted mathematical words BAB and BABAAA must lead to the same *mathematical full state* regardless of k,c,e,t.

The actual native 64×64 full-frame BLAKE2b hashes in the new agent's independently recorded word trace were:

| Native game | Provisional native BAB | Provisional native BABAAA | Same native visible frame? |
| --- | --- | --- | --- |
| SK48 | 84768fbf9fcc7bf81ceb5b7ed45e104f | 04be4920e395c8464237244a3d85ff33 | **No** |
| LS20 | f7fd906bb3f18202258e2a90866980e9 | 22e274bb9477d87f7418f069abbd3b2d | **No** |

The exact source-owned raw frame arrays, every native-rooted intermediate word, complete hash list, 48-law candidate parameters remaining, and the true agent SHA-256 are in the run artifact. In both directional games the direct proposed source mapping is contradicted after six actions, and the new agent **stops rather than fabricating another action**.

FT09's only native action is ACTION6 with coordinates. The executable now checks its actual native reset and records the interface WALL, with **zero environment actions**. It does NOT issue a center-of-frame placeholder click, replay an FT09 route, or claim to have tested a mathematical A/B relation there.

## What this establishes — and what it does not

**Established:** the live ARC lane's mathematical core is now the original 48-law marked window; its source conformance is tested, the previous nine-world file is archived, and a real native observation experiment using the new entry has finished.

**Not established:** any real native ARC control or composite sequence realizing those mathematical generators, an injective visible-state identification, any full-state conjugacy, a native-to-F3 quotient, an ARC goal-reaching policy, or an ARC win. The nine-law investigations are historical only; the new native tests are new evidence under the 48-law contract.

**Next justified experiment:** derive testable native action/state correspondences FROM actual native relations, including coordinate actions, before assuming action IDs are mathematical letters. Preserve marked roots, full-state versus nonrooted witnesses, raw negative controls, and a WALL when unsupported. Do not expand the 48-law family with unproved rules or substitute ARC's heuristics for it.
