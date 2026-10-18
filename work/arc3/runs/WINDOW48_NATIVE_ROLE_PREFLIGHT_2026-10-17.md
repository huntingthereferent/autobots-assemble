# Window48 — native generator preflight and rooted question plan

**Investigation date:** October 17, 2026, America/Chicago (GitHub Actions logs October 18 UTC). This checkpoint uses the ORIGINAL 48-law marked-window F3 source, not the archived nine-world phi agent. It does not replace the canonical native agent or assert an ARC score.

## Source requirement and actual native preflight

[Original Window48 source](../../arc_like_maze/window_combined.py): 48 concrete source laws, 16 marked-root classes, 14 full-state conjugacy classes. Mathematical A increments its first F3 coordinate by one; A cubed is identity and its origin has a strict period-three orbit.

[Native run #39096203935](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39096203935) and [actual raw frames/JSON artifact](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39096203935/artifacts/12125050313).
[Reproducible native source](../native_window48_roster_preflight.py).

The official public ARC native roster had 25 games and a native root frame was observed for every one. Every advertised native simple control ACTION1 through ACTION5 was separately tested from a freshly reset native state. No saved solution routes, fabricated game engine, or unknown click positions were used.

| Observation | Result |
| --- | ---: |
| Public games and roots observed | 25 / 25 |
| Games lacking an eligible simple native control | 7 |
| Independently reset individual-action probes | 75 |
| Native environment actions | **225** |
| Different full frame after 3 repetitions: literal source A-cube contradicted | **74** |
| Visible root returned but strict period-three was absent | **1** |
| Nontrivial visible 3-cycles witnessed | **0** |
| Incomplete classifications | **0** |

The seven no-simple-control public games were ft09, lp85, r11l, s5i5, su15, tn36, vc33. Their native interfaces were observed, not mapped onto nonexistent A/B controls. They need not all be click-only.

**Bounded negative result:** NONE of the 75 single advertised native controls realizes original F3 A **as a direct, action-preserving complete-visible-state mapping at the native game root**. This neither excludes native macros, different states, coordinate click actions, observable quotients, or hidden engine relations, nor refutes the mathematical F3 family. No game level completed.

## Source-backed mathematical rooted discriminators

[Independent passing rooted-question check #39096459991](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39096459991) and [full question/signature artifact](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39096459991/artifacts/12124499584). [Generator](../window48_rooted_questions.py) and [tests](../../../network/tests/test_arc3_window48_rooted_questions.py).

For all 120 unordered pairs of the 16 marked-class representatives, the script requests rooted collision evidence in BOTH directions from the original rooted_conflict implementation. The witness is directional: no collision from X to Y does not imply rooted equivalence. There were 17 distinct source-derived question pairs, and deterministic greedy set cover picked SIX comparisons that separate all 16 rooted classes. It is NOT claimed to be a globally minimum set.

| Rooted mathematical word 1 | Rooted mathematical word 2 |
| --- | --- |
| empty word | BBB |
| BA | ABB |
| BAA | BAAB |
| ABABA | AABABB |
| AA | AAB |
| ABA | ABAB |

The source regression independently verifies 16 DISTINCT rooted equality signatures, each shared by the 3 shear-chart concrete laws within one rooted class (48 total). In the original support 0 and 3, pulse 1, balanced-edit switch, a full-state conjugacy moves the origin: the selected questions STILL distinguish these rooted classes instead of improperly collapsing them to the 14 full-state classes. The longest selected word has six mathematical letters.

**These six are mathematical questions, not witnessed ARC transformations.** Applying them to native ARC requires an independently supported mapping of complete action parameters, action history, and observable state factors to F3 A/B. Native visible frame equality cannot prove hidden-state identity or full-state conjugacy.

## Current decision

The canonical [48-law ARC entry](../agent/my_agent.py) and original mathematical laws remain unchanged. An ARC success was NOT measured. Further assignment of arbitrary direct action IDs or fabricated coordinate clicks to F3 letters is not admissible just to exercise these questions.

Next justified experiment: discover a native composite or parameterized action on an explicitly witnessed observable factor, then predeclare and independently test source A³ before proceeding to these six rooted class questions. A failure is recorded as a wall; the archived nine-law branch stays historical.
