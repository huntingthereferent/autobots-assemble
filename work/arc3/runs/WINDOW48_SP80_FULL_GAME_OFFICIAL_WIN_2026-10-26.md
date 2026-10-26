# SP80 — Independent original SDK complete 6/6 WIN (external positive witness)

**2026-10-26 · Confirmed official game result, not a source-simulation proxy.** Two independently reset and genuinely entered SP80 original `Arcade(OperationMode.NORMAL)` games reached **`levels_completed=6`, `state=WIN`**, byte-identical final 64×64 original source frame `2edefbe248213aff77eec9068a7f816d`.

## Authorship and attribution

The first four native level transitions are established by the **pre-existing owned ARC research** in this repository: its exact `PREFIX` (Level0→1), two distinct Stage1 source witnesses (Level1→2), `STAGE2_VERIFIED_WORD` (2→3) and `STAGE3_WINNER` (3→4). These were genuinely replayed from independent original SDK resets, not converted to a substitute game.

**The final two level-solving words are third-party published evidence, NOT our original discovered ARC solutions.** Provenance: [synchopate/arc-agi-crystalline](https://github.com/synchopate/arc-agi-crystalline), [public `solvers/recorded_solutions.json`](https://github.com/synchopate/arc-agi-crystalline/blob/main/solvers/recorded_solutions.json), `sp80` action indices48–64 (fifth game level) and65–96 (sixth/final game level), zero-based in that public file. That project reports SP80 6/6 WIN. We independently tested the public claim using our *own*, differently rooted SDK entrance and the original public game engine. No external solver source was copied into the owned canonical agent. Source-to-goal reasoning and attribution must remain separate.

Our genuine replay source and evidence:
- [**Successful original SDK full-game Actions workflow #40384614054**](https://github.com/huntingthereferent/autobots-assemble/actions/runs/40384614054)
- [Complete original public SDK native level receipts and returned frame arrays — artifact #12680500452](https://github.com/huntingthereferent/autobots-assemble/actions/runs/40384614054/artifacts/12680500452)
- [Exact independent normal-SDK reproduction script](../native_sp80_full_game_external_replay.py)
- Independent fifth-level confirmation before final replay: [Actions #40383702393](https://github.com/huntingthereferent/autobots-assemble/actions/runs/40383702393) and [artifact #12679821728](https://github.com/huntingthereferent/autobots-assemble/actions/runs/40383702393/artifacts/12679821728)

## Actual official six-level transition audit

The runner opened fresh original normal-mode SDK game instances twice, one for original Stage1 witness A and one for witness B. The complete official action/level ledger for each source witness:

| Game level completed | Original native program provenance | Actions A / B | Actual SDK `levels_completed` after | SDK state after |
|---|---|---:|---:|---|
| 1 | Owned `PREFIX` | 6 / 6 | 1 | NOT_FINISHED |
| 2 | Owned independent original Stage1 witness | 9 / 11 | 2 | NOT_FINISHED |
| 3 | Owned `STAGE2_VERIFIED_WORD` | 11 / 11 | 3 | NOT_FINISHED |
| 4 | Owned `STAGE3_WINNER` | 34 / 34 | 4 | NOT_FINISHED |
| 5 | **External published fifth-level action witness**, attributed above | 17 / 17 | **5** | NOT_FINISHED |
| 6 | **External published sixth-level action witness**, attributed above | 32 / 32 | **6** | **WIN** |

For each stage, the actual SDK action/level oracle was validated **after every action**, not inferred from animation. The original true game Stage4 root `fa8fd32d3bfd2c8b3ff7765aec373512` and newly genuine Stage5 root `633788a7d98fbec041de79dd1abf49f4` were explicitly hash checked against independently archived previously confirmed originals. Every final SDK result and source digest agreed across both entrances.

The published Stage5-level word (SDK Stage4 index) is:

```text
3 3 1 6@25,34 4 1 1 6@34,22 3 2 6@34,43 4 4 4 1 1 5
```

The published **sixth/final** level word (SDK Stage5 index) is:

```text
4 4 4 2 2 2 2 2 6@44,20
3 3 3 3 3 3 3 2 2 2 2
6@29,32 4 4 4 1 1
6@32,47 4 1 1 1 5
```

They are recorded **only as attributed external positive controls**, not presented as predictions derived by A/B/F3.

## Independent A/B negative/positive floor-spill discrimination

This research uncovered the actual game-level description in a public [SP80 mechanics guide](https://arc3.markbarney.net/arc3/games/sp80). The currently investigated SDK `levels_completed=4` is the game's **fifth** level, drawn upside-down and containing a movable purple L piece. It must fill all yellow cups **without any spill-line contact**. On the upside-down level, the source floor line is the **top screen border**; another side line can also fail the pour. This is a community-authored description, not the official SDK oracle.

We tested our preexisting 21-action `BASE + ACTION5` (22 native Stage4 actions total) as **A**, and the public 17-action Stage4 positive as **B**, from the exact same initial original SDK Stage4 root under both independent verified entrances:

| Entire genuine original SDK ACTION5 observation | A: owned four-cup control | B: attributed public winning fifth-level trace |
|---|---|---|
| SDK after-level | **4** | **5** |
| Returned native 64×64 animation frames | 32 | 28 |
| Complete four cup windows all 45 palette13 pixels | frames23–30 | frames25–26 |
| First actual **top horizontal spill line** color1→14, with corner excluded | **frame20** | **never before stage transition** |
| Actual right vertical spill line warning (non-overlapping, y5–58,x59–61) | not seen | not seen |
| Source palette6 upper floor-adjacent strip y5..7 before terminal return | x26–28 by frame19, later x44–46 and x56–58 | **no such source6 water through frame26** |
| Exact native public status | Level4 NOT_FINISHED | **Level5 NOT_FINISHED** |

The public winner has all four cups full transiently **but no observed floor spill** before the SDK moves to the next level at animation frame27. The failure also colors all four cups but touches the spill line, then fails. Earlier "top and right border simultaneous flashes" were a measurement artifact of overlapping rectangles in the top-right corner; right-side vertical events must be measured excluding that corner.

A separate offline read-only audit of **65 archived original SDK Level5-game four-cup-complete pour sequences** from 12 evidence ZIP artifacts found **65/65** with a top spill-line contact sometime in the animation. In 17, visual four-cup occupancy came *before* that warning; none advanced. This old archive contains repeat programs and entry-witness observations, not 65 independent experiments. Our independently verified winning source sequence is the missing positive class. Do not use mere visual cup fill, duration, source stream connectedness or warning timing alone as a success proxy.

## Research limits and next handoff

**Actual SP80 6/6 WIN is established in the original SDK with independently repeated source evidence.** The original solver's unsolved owned Level5 geometry remains scientifically distinct: these external published last-two-level action words provide **positive control and A/B ground truth**, but do not demonstrate that the original A/B finite 48-law mathematical method autonomously discovered them. Genuine reproducibility is not the same as independent algorithmic discovery.

If continuing ARC research, valid next work is to reverse-compare this actual positive fifth-level source flow with failed configurations, identify minimal rules or relationships *from independent input/output evidence*, or build a fresh agent that solves without merely replaying the published words. Preserve original goal/action referents, external attribution, official SDK score separation, all native frames and rooted histories. **Do not retroactively credit the public route to the user's canonical agent.** Exact 48-world F3 mathematics and canonical agent remain untouched. PR #537 remains **open and unmerged**.
