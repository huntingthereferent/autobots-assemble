# LS20 — bounded native glyph macro test of the original F3 A generator

**Research date:** 2026-10-17 (America/Chicago); GitHub Actions recorded this run in UTC on October 18.

**Scope:** original F3 mathematical models compared with a native-calibrated **visible glyph-position factor** for the public LS20 game. This is not a new ARC game, an ARC solver, a F3 theorem about all ARC environments, or a hidden/competition result.

## Mathematical question

In all nine original F3³ worlds (phi=(0,a,b)), the source-defined A advances the first field coordinate by one and has **exact order three** at the root:

- A(root) != root
- A²(root) != root and A²(root) != A(root)
- A³(root) = root

The executable [source code](../../arc_like_maze/math.py) was used to verify that exact relation independently in all nine worlds. A native composite word can be considered an A *candidate on the observed glyph factor* only when it has the same nontrivial three-state orbit in **actual observed pixel coordinates**, without reducing arbitrary pixels modulo three.

## Frozen native-derived factor and bounded search

The [geometry-corrected native factor model](../native_factor_geometry.py) had already predicted **69/69** complete native frames, including **35/35** previously unseen actions. The current test does not alter that movement rule. It calibrates the original 25-cell color-9/12 glyph with one actual native ACTION3 and uses the previously tested static-obstacle collision rule.

[The bounded macro search](../native_f3_macro_order.py) examines **all 5,460 nonempty words of length 1–6** over actual native controls ACTION1..ACTION4, calculating W, W² and W³ on exact glyph offsets. In addition to the origin, the same predeclared computation visits all **34 model-reachable glyph offsets** from the calibrated native root. These reachable offsets are **model predictions**, not 34 separately witnessed native states.

| Model computation | Result |
| --- | ---: |
| Different native macro words screened at the root | 5,460 |
| Model-reachable native glyph offsets | 34 |
| Origin macros fixed after first application | 672 |
| Origin macros failing a return after three applications | 4,788 |
| Strict order-three glyph cycles at origin | **0** |
| Strict order-three glyph cycles at other model offsets | **0** |

No candidate macro of length at most six produced a nontrivial three-state glyph cycle anywhere in this finite measured model. This does not exclude longer macros, other observable state factors, hidden engine state, or different mathematical representations. It does **not** prove a global absence of three-cycles in the native game itself.

## Independent native confirmation

[GitHub native F3 macro run #39090226133](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39090226133) repeated six predeclared macro words **three times each**, on independent native LS20 resets, preserving expected and actual pixel frames for every step.

[Native raw frames, full predicted/actual JSON and mathematical witness](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39090226133/artifacts/12122751109) — the artifact is retained 14 days.

| Actual native macro repeated 3 times | Native actions | Exact predicted full frames | Glyph at original location after 3 repeats? | Complete native frame returned? |
| --- | ---: | --- | --- | --- |
| 1 | 3 | 3/3 | No | No |
| 34 | 6 | 6/6 | Yes | No |
| 12 | 6 | 6/6 | Yes | No |
| 3214 | 12 | 12/12 | Yes | No |
| 113422 | 18 | 18/18 | No | No |
| 3142 | 12 | 12/12 | Yes | No |
| **Total** | **57** | **57/57** | — | — |

One additional native ACTION3 calibrated the glyph template before the six experimental trajectories. No level completion or win was observed in these confirmations.

The words that return the glyph return its *position immediately* after a single macro, so they are not strict F3 A witnesses. In those cases, the native two-cell progress trace keeps changing; the **complete 64x64 frame never returns** after the three tested repetitions.

## Boundary preserved

The original nine F3 laws were neither changed nor rejected as abstract mathematics. Rather, the following identification attempt remains unsupported:

> Interpret any one of the 5,460 short native action combinations as source-defined F3 A on the independently witnessed LS20 glyph-position factor.

No candidate survived the bounded geometry-model search. Representative real native tests exactly matched the model over 57 held-out frame transitions. Because the verified model was developed from this same public LS20 level, this is a **scoped mathematical negative witness**, not an independent cross-game benchmark.

The trace makes raw-frame returns impossible within these tested paths, while native obstacles cause certain moves to be blocked. A mapping manufactured by taking position modulo three would simply impose F3 rather than discover it.

**Next admissible movement:** Either obtain a native-visible, genuinely nontrivial three-state recurrence from an independently motivated state factor, or retain the A-generator correspondence as an explicit open wall and move to a different native game/evidence question. Do not alter the canonical F3 agent to treat this negative result as progress toward an ARC win.
