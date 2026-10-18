# ARC-AGI-3 — source F3 probes on independent native games

**Research date:** October 17, 2026 (America/Chicago; GitHub runner timestamps are October 18 UTC). **Status:** Native evidence collected; **no verified native-to-F3 correspondence and no game win**.

This test intentionally left the previously studied LS20 environment. It uses only the official public native `arc-agi` game runtime for observations, and the source [nine F3 worlds](../../arc_like_maze/math.py) plus their [mathematically selected separating word probes](../../arc_like_maze/relation_probe.py) for predictions. It does **not** inspect the FT09 or SK48 game's source, import routes from historical research, or infer game rules from ARC solver advice.

## Reproduce

- [Initial native cross-game run](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39091045793).
- [Native FT09 click-effect search and F3 source comparison](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39091384089), including the [native raw-frame and source-signature artifact](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39091384089/artifacts/12123260794).
- [Native independent repeated-click algebra test](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39091731824), [real pixel frames and all mathematical word comparisons](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39091731824/artifacts/12121944845).
- Actual executables: [cross-game source probes](../native_f3_other_games.py), [FT09 coordinate measurement and rooted comparisons](../native_ft09_f3_clicks.py), and [follow-up click algebra](../native_ft09_click_algebra.py).
- The GitHub Actions artifact contains complete native frame arrays and JSON traces and has 14-day retention. Committed scripts preserve a separate rerun path.

## F3 reference, frozen before native interventions

For all nine declared F3³ worlds, mathematical A is an order-three transformation: the origin and AAA endpoint are equal. Every declared world also has distinct AB and BA mathematical endpoints at the origin. The exact [original F3 separator implementation](../../arc_like_maze/relation_probe.py) additionally supplied rooted equality questions; the complete five tested pairs were:

| Source mathematical word pair | Original nine F3 laws predicting equality |
| --- | ---: |
| empty word versus AAA | **9/9** |
| AB versus BA | **0/9** |
| empty word versus BBB | 3/9 |
| A versus BAB | 3/9 |
| ABB versus BA | 3/9 |

The source-rooted questions are not native observations. A formal law match is **conditional** on independently establishing a meaningful mapping from the native game to mathematical generators and states.

## New game 1 — SK48

The untouched native SK48 reset offered native action IDs 1,2,3,4,6,7. For this explicitly provisional direct-mapping test only, assign **native ACTION1=A and ACTION2=B**; use 8 unique rooted word trajectories on independent resets (17 actual native actions). All full native roots matched; all source-word trajectories completed.

| Source words | Actual native whole-frame equality | Original F3 worlds predicting equality |
| --- | --- | ---: |
| empty / AAA | **Different** | **9/9** |
| AB / BA | Different | 0/9 |
| empty / BBB | Equal | 3/9 |
| A / BAB | Different | 3/9 |
| ABB / BA | Different | 3/9 |

The universal original F3 A³ identity is directly contradicted on the literal full native visible frame. Under the explicitly stated **injective, action-preserving full-visible-state** interpretation, **0/9 original F3 candidates survive** this candidate native action-ID assignment. A different state factor, hidden-state interpretation, or different native generator remains an open question; this result is not a theorem that SK48 cannot contain an F3-related structure.

## New game 2 — FT09

The actual native reset exposed **ACTION6 only**, which is a *coordinate-parameterized click*. Assigning native ACTION1 and ACTION2 as mathematical A/B is unavailable.

The first ten click locations, chosen deterministically from distinct native non-background color components, produced no whole-frame changes. Before inspecting further outcomes, the follow-up experiment fixed an evenly spaced 8x8 pixel-site lattice across the untouched 64x64 native frame, including native majority-color cells. Across **74 total single-click measurement sites**, the experiment found **8 distinct native frame effects**. The first two differing, independently tested visible effects came from pixel coordinates **(36,36)** and **(44,36)**.

Those two observed click transformations were **provisionally** assigned mathematical A and B strictly to challenge the existing F3 family. Their rooted AB and BA sequences ended at the **same visible full frame**, whereas **all nine original F3 laws distinguish AB from BA** mathematically. The tested candidate assignment had **0/9 source F3 worlds consistent with a direct injective identification of complete visible frames**. Rooted A³ and the additional separating questions were also executed and logged; the result is not upgraded into an F3 success on the basis of visually equal states.

This is a genuine interface finding: **the action parameter is part of the experimental transformation**. A click action has no single intrinsic A/B identity without selecting coordinates and checking the native effect. No coordinate was taken from a solved path or an ARC game-specific rule. In this run, no pair of clicks was established as source F3 generators.

## FT09 repeat-action and action-order witnesses

The eight source-observed FT09 click effects were all located at native-color-9 measurement sites in the uniform spatial lattice, and each first click changed **38 native pixels**. Their diff bounding boxes extended from the clicked coordinate toward the lower-right native frame corner. This is a pixel-level observation, not an inference that the game internally represents a rectangle or a fixed 38-cell button.

To test two source-grounded candidate transformations again, **two click pairs were predeclared from the prior 74-site observation** before executing a new set of independent native resets:

- Pair 1: native coordinate clicks (36,36) and (44,36).
- Pair 2: native coordinate clicks (36,44) and (52,52).

The additional real FT09 experiment executed **62 native click actions**, each word from a fresh native reset, comparing original mathematical word identities directly to native complete-frame equality.

| Witness question | Pair 1 native visible result | Pair 2 native visible result | Original 9 F3 worlds |
| --- | --- | --- | --- |
| Root versus A | Different | Different | Different (9/9) |
| Root versus AAA | **Different** | **Different** | **Equal (9/9)** |
| A versus AA | Different | Different | Different (9/9) |
| B versus BB | Different | Different | Different (9/9) |
| AB versus BA | **Equal** | **Equal** | **Different (9/9)** |

**Correction:** repeated clicks were *not* visibly idempotent at the tested root. In both native pairs A and AA remained different, as did AA and AAA. Do not describe these controls as idempotent, irreversible, globally commutative, or invertible without the corresponding direct evidence. Only **the tested rooted two-click orders AB/BA** visibly commuted at their endpoints. Equal observed final frames may conceal different native histories.

**The original source F3 discrepancy reproduced for a second spatially different pair:** native A³ did not return the complete frame to its origin, and native AB/BA had equal visible endpoints. Thus neither pair supplies a verified direct injective native-frame realization of original F3 generators.

This is development evidence on public FT09, not an untouched hidden-game benchmark, a proof about all coordinate pairs, or a native win.

## Result and boundary for the agent

There are now independent native counterexamples to **direct literal F3 generator assignment** in LS20, SK48, and FT09. They are not counterexamples to the original mathematics itself. The FT09 observations further demonstrate that the available native action *type* alone does not identify a mathematical transformation: coordinate parameterization is observable and necessary.

Do **not** change the F3 laws, reduce game pixel colors or coordinates modulo three to fit them, infer that a visually identical frame proves an identical hidden native state, or claim a native game completion. The existing `work/arc3/agent/my_agent.py` remains an experimental F3-first prototype; its default provisional first-two-action identification is known to be **unsupported across these games**.

**Next admissible mathematical work:** define and validate *how to propose native action roles from evidence*, including coordinate-parameterized actions, before treating any native control as source F3 A/B. Require observable distinctions and independent predicted returns; if these are absent, record an **unestablished correspondence** instead of blindly continuing or inventing a new bot system.
