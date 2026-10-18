# SP80 — longer native histories bound the occupancy-conditioned relation

**October 18, 2026.** Native source: official ARC-AGI-3 public SP80 under real arc-agi Arcade NORMAL. Mathematical context: the ORIGINAL 48-law WindowCombined F3 family, unchanged; no native generator correspondence is claimed.

## Previous source-owned checkpoint

The [independent pre-color native checkpoint](WINDOW48_SP80_NATIVE_OCCUPANCY_2026-10-18.md) had 50/50 exact ACTION4 native pixel/color transition maps under each of two previously frozen stage-0-to-stage-1 spatial mappings, plus a position-dependent bottom-row completion and a BEFORE-action native-color admissibility gate.

Both mappings remain fixed:
- T: translate native pixel positions by (+8,+20).
- R: reflect native y, then translate (+8,-8).

These predictions use BOTH actual stage-0 action effects and real level-1 frames BEFORE taking the same action. They cannot choose an ARC action autonomously, and neither mapping has been proved a mathematical conjugacy.

## Experiment 1 — longer native histories

[Successful actual public native run #39121709027](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39121709027), [complete raw frame arrays / observed native levels / transition evidence](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39121709027/artifacts/12134765659), [reproducible script](../native_sp80_occupancy_long_history.py).

Eight predeclared new context words of length 8 to 12 were tested from actual SP80 level 0 and separately at genuine level 1 reached by the previously witnessed first-level completion prefix 454545. Every word had TWO independent fresh-reset level pairs.

| Observed result | Count |
| --- | ---: |
| Real native resets | **32** |
| Real native actions | **356** |
| Paired native histories | 16 |
| Complete level-preserving paired histories | **6/16** |
| Genuine level-1 root entries | 16/16 |
| Valid paired ACTION4 effects (level unchanged on BOTH sides) | **66** |
| Completely exact frozen T and R predictions | **56/66** |
| Actual native changed pixels and native color pairs included | **2,078/2,078** |
| Extra predicted native pixel changes after occupancy gating | **72** |
| Native changes missed or wrong native color pairs | **0** |
| T and R disagree on a predicted native transition | **0/66** |

Ten paired histories were interrupted by a real **stage-0 native level-counter change**. Those later unmatched steps are UNKNOWN, not mathematical counterexamples; the 66 comparisons include only level-preserving actual observed effects.

**New falsification:** On native level 1 after six consecutive ACTION4 controls, the seventh ACTION4 in word 44444444 changed only one pixel, although the frozen model predicted a 16-pixel native 9-to-12 block at x=44..47,y=36..39. The block's target PRE-action pixels had the expected native starting color, so the earlier occupancy constraint could not reject these false changes. A corresponding mismatch recurred at action eight. The pre-color condition was effective in the old tested scope but is NOT sufficient across these longer native histories.

## Experiment 2 — distinguish uninterrupted ACTION4 streak from word position

[Successful independent public native run #39121972883](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39121972883), [actual source-owned frames / per-step counterexamples / native stage counters](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39121972883/artifacts/12133754161), [reproducible control script](../native_sp80_streak_vs_wordstep.py).

Before executing this run, fix eight new words that vary ACTION4 streak lengths independently of absolute action positions: 4444444, 44444544, 44444454, 54444444, 45444444, 45544444, 44445444, 545454544. Two independently reset level pairs each.

| Native result | Count |
| --- | ---: |
| Resets and actions | **32 resets, 348 actions** |
| Complete stage-preserving paired words | 14/16 |
| Comparable ACTION4 effects | **102** |
| Completely exact T and R predictions | **88/102** |
| Correct actual native color transitions | **3,024/3,024** |
| Extra after-gate predicted changes | **204** |
| Missed native transitions / wrong color labels | **0 / 0** |
| T vs R different predictions | **0/102** |

**Exact outcomes by absolute position in the native context word:**

| Word step | Exact ACTION4 effects | Extra predicted pixels |
| --- | ---: | ---: |
| 1 through 6 | **78/78** | **0** |
| 7 | **10/12** | **32** |
| 8 | **0/12** | **172** |

Failures also occurred after ACTION5 interrupted consecutive ACTION4 sequences. In the measured sample, failures appeared at uninterrupted ACTION4 streaks 1, 2, 3, 5, 6 and 7. Therefore seven uninterrupted ACTION4 controls are NOT required for a failure. The accumulated native word position is more predictive in these bounded cases, but it is not yet an identified causal mechanism. At each stage, other hidden state, progress, sprite geometry and event conditions may contribute.

The two geometric hypotheses still produce identical occupancy-conditioned predictions across all 168 paired ACTION4 effects in Experiments 1 and 2 combined; reflection is not independently identified.

## Separate independently confirmed native one-level progress

In the control run the stage-0 native counter advanced on the seventh action of 545454544. This motivated a **new independent** native trial testing its actual seven-letter prefix 5454545 against a six-letter negative control and the earlier positive control.

[Successful native independent level verification #39122140319](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39122140319), [native frames, exact action order, native counters and states](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39122140319/artifacts/12134267718), [reproducible script](../native_sp80_alternate_level_witness.py). Each word used three fresh resets.

| Native word | First-level 0 to 1 replays | Native step of progress |
| --- | ---: | ---: |
| 5454545 | **3/3** | **7** |
| 545454 | **0/3** | none through six actions |
| 454545 | **3/3** | **6** |
| 4545454 | **3/3** | **6** (runner stops at the transition) |

All positive native observations ended in **GameState.NOT_FINISHED**. These are actual native **one-level** progress records, NOT full SP80 wins, general policies or realizations of an original 48-law F3 generator. The alternate word was not imported from saved game routes or implementation files; it was identified as a native effect and independently replayed.

## Research decision

The previous exact 50/50 conditional relation is now **bounded** by longer, independently tested histories. All observed native changed pixels and original native color pairs are still represented in the frozen model, but the model predicts additional native changes which do not occur despite the target pre-color being admissible. The discrepancy is preserved; no post-hoc fitting or silent addition of a new temporal rule is justified.

The next admissible experiment can predeclare a directly observable history-dependent condition (with negative controls) from actual SP80 image and action records, then test its consequences on new native states. Do not equate success in native game progression with F3 mathematics. The canonical 48-law ARC MyAgent, 16 rooted/14 full conjugacy classification, and original mathematical sources remain unchanged.
