# A/B native map geometry — first independent predictions of unknown edges

Measured against official ARC-AGI-3 public LS20 on the experiment/ab-native-inverse-20261017 branch. No REA, no F3 hidden-state correspondence, no game solution claim.

## Prior evidence and rule frozen before native trial

The previous independent A/B transport model was sourced from 76 native trajectories and 304 observed actions, yielding 27 unique position/action edges. [Prior source verification](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39093565973). Its original artifact includes the 17 separately reset eight-step native trajectories. Before observing any of the new edges, the geometry investigator reconstructed the static background under the root glyph from an independently measured cleared frame, preserving the original 64x64 pixels.

The proposed rule was: the native glyph has a 5x5 footprint, and ACTION1/2/3/4 attempts a shift of 5 pixels up/down/left/right respectively. If every destination cell is a previously visible traversable terrain color (3 or 5), the glyph moves; otherwise the move is blocked. The rule reproduced all 27 prior source (glyph position, native action) transitions, including blocked movements.

This is a conditional **visible map geometry rule**, not an assertion of underlying game source code. Its extrapolation to unseen edges was the subject of the trial.

## Native action-word holdouts, specified in source first

Every holdout path comprises known, independently observed movement edges followed by a single **previously unrecorded** position/action edge. Each distinct unseen edge was tested exactly once.

| Native word | Unseen starting glyph (row,column) | New action | Predicted destination | Actual destination |
| --- | --- | --- | --- | --- |
| 41 | (45,39) | 1 | (40,39) | (40,39) |
| 113 | (35,34) | 3 | (35,34) blocked | (35,34) |
| 114 | (35,34) | 4 | (35,39) | (35,39) |
| 144 | (40,39) | 4 | (40,44) | (40,44) |
| 332 | (45,24) | 2 | (45,24) blocked | (45,24) |
| 334 | (45,24) | 4 | (45,29) | (45,29) |
| 441 | (45,44) | 1 | (40,44) | (40,44) |
| 442 | (45,44) | 2 | (45,44) blocked | (45,44) |
| 443 | (45,44) | 3 | (45,39) | (45,39) |
| 1113 | (30,34) | 3 | (30,34) blocked | (30,34) |
| 1114 | (30,34) | 4 | (30,39) | (30,39) |
| 3331 | (45,19) | 1 | (40,19) | (40,19) |
| 3332 | (45,19) | 2 | (45,19) blocked | (45,19) |
| 4441 | (45,49) | 1 | (40,49) | (40,49) |
| 4442 | (45,49) | 2 | (45,49) blocked | (45,49) |
| 4443 | (45,49) | 3 | (45,44) | (45,44) |
| 11113 | (25,34) | 3 | (25,29) | (25,29) |
| 11114 | (25,34) | 4 | (25,39) | (25,39) |

The frozen prediction and all the native actions are captured independently, with complete original raw frames, action metadata and hashes.

## Verification

- [GitHub Actions run 39096314847 — SUCCESS](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39096314847).
- [Original frozen predictions, original native pixel arrays, native manifest and independent verifier](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39096314847/artifacts/12124637495), artifact retention 14 days.
- Source/negative-path tests: 14/14 passed.
- Independent raw-frame oracle: 18/18 genuinely unseen edge destinations matched the source geometry rule; 12/12 movement predictions and 6/6 blocked-movement predictions were exact.
- Every known path to the unobserved edge was independently replayed and matched its previously recorded coordinates. All 18 native trajectories completed, 64 native actions, common visible root.
- Frozen forecast JSON SHA256: 1dea0084a3cf56263c4986b17d715d146278b20f05511ff49a6a7c3bfbe2631c.
- Actual new native manifest SHA256: ad02f8dc4d96d61e164361430c22e02a5ba3a3de80de4cb2c4d740a169373f59.
- Actual raw NPZ SHA256: efc7f798dee3797c36bd5dc1d24c705c621e4ebe53470af1cd23d0ae77359a2d.
- Independent verifier JSON SHA256: 16c9346a0b5fa64706c8e13912ff5163cb6ea0fc993dae4a8f2dae309b5c292c.

## Interpretation, without overreach

Unlike the preceding eight-step test, this experiment predicted state/action relations **absent from the training graph**. The geometry-based rule succeeded at 18 new native edges including wall collisions and movement into distinct traversable positions. This is independent evidence for its predictive value in the **measured portion of the LS20 visible map**, not a total proof of the game's movement code, all map colors, all action effects or complete hidden state.

The earlier action-dependent glyph transport relation and the independent visible trace clock remain separate observations. Equal visible frames are not hidden-state identity, and there is still no validated native-to-F3 map or ARC solve. The natural next mathematical test is a broader predeclared map survey including unmeasured tile types and boundary cases, with explicit negative predictions and retention of any counterexamples. Do not generalize the source rule to another game without new evidence.
