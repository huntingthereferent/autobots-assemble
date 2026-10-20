# Original SP80 level2 — authentic coordinate-click inventory

October 19–20, 2026. Actual original public `arc_agi.Arcade(OperationMode.NORMAL)` SP80 SDK. **Source-confirmed level2 bar-selection controls**, not a game clone, inferred engine physics or six-level victory.

## Original source referent and frozen input
The [independent original stage2 baseline](WINDOW48_SP80_STAGE2_BOUNDARY_NATIVE_BASELINE_2026-10-19.md) had already reached genuine SDK level2 on 24 source game resets and retained a byte-identical level2 entry screen BLAKE2b digest-size16 `4e57697162471ec9065cc7afe9de97b4`. Native source-visible level2 horizontal bars: upper **16×4 color8 x8–23,y20–23**, middle **20×4 color8 x40–59,y28–31**, lower **24×4 color8 x8–31,y32–35**, bottom initially selected **24×4 color9 x36–59,y40–43**.

Prospectively froze `native_sp80_stage2_click_inventory.py` before gameplay with **16 stage2 control words**: ACTION6 on each of four bars, three source upper display pixels, a source background pixel, then matched native ACTION4 or ACTION5 after each bar click. Each word was repeated on **two independent original game resets using EACH of two exact genuine previous stage1→2 witnesses A and B**, for **64 separately reset authentic native games**. Every game starts at original SDK level0, witnesses true `454545` native stage0→1, then a previous independently source-authenticated `ACTION6`/movement/ACTION5 sequence advancing native stage1→2. Stage2 was never injected, synthesized or inferred from screen colors. Every native ACTION6 carried real `data={"x":x,"y":y}`, and all observed actual source pixels-under-click are recorded.

## Genuine SDK execution and independently audited artifact
[Official original-native source run #39368739359](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39368739359) PASSED: **64/64 freshly reset original SP80 games** reached SDK `levels_completed=2`, **1,120 actually accepted original SDK action responses**, including **64 genuine stage2 coordinate clicks** and **256 genuine coordinate clicks in total** across the prior level1 witnesses and stage2 probes. All final native source states remained **level2, NOT_FINISHED**; **zero native level3 or WIN**. The 16 frozen controls were each reproduced under both previous source witnesses and two resets.

[Unmodified original SDK full frame-stack NPZ and complete event JSON artifact #12240252756](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39368739359/artifacts/12240252756). Its downloaded ZIP SHA256 **`09f5a88d8cb5837a20a10a4f67b476b03f71066b578c31f1bc76913ed464f639`** was independently recalculated and matched GitHub's original digest. Contains **7,184 genuine 64×64 native source images**, including 64 reset images and **7,120 returned action images**.

**Independent native source verification:** decoded the original NPZ and original 222 MB unfiltered JSON. Reconstructed and reconciled the exact **7,120/7,120 original SDK-returned frame transitions**, with **867,520/867,520 native changed (x,y,before-color,after-color) pixel events**, **zero discrepancies**. All **256 original coordinate clicks** were independently checked against the true pixel at that location in the immediately preceding source frame: **zero mismatches**. No modeled or interpolated frame was substituted. Source game, prior F3 mathematical investigation, canonical agent, historical records and owner rights untouched.

## Genuine original level2 ACTION6 selection behavior
Each first native stage2 ACTION6 result was reproduced across both independent source entry witnesses and both resets (**four true games per probe**):

| Frozen coordinate | Actual pre-click source pixel | Selected source bar before | Selected source bar after | Native last-frame pixels changed |
| --- | --- | --- | --- | ---: |
| Upper bar (12,21) | **8** | x36–59,y40–43 | **x8–23,y20–23** | **161** |
| Middle bar (44,29) | **8** | x36–59,y40–43 | **x40–59,y28–31** | **177** |
| Lower bar (12,33) | **8** | x36–59,y40–43 | **x8–31,y32–35** | **193** |
| Initially selected bottom bar (40,41) | **9** | x36–59,y40–43 | unchanged | **1** |
| Upper display (14,5) | **11** | x36–59,y40–43 | unchanged | **1** |
| Upper display (30,5) | **11** | x36–59,y40–43 | unchanged | **1** |
| Upper display (46,5) | **12** | x36–59,y40–43 | unchanged | **1** |
| Background (62,50) | **12** | x36–59,y40–43 | unchanged | **1** |

The original source pixel at (46,5) is **color12**, not color11; its label as a generic upper display location remains appropriate. The one changed source pixel in nonselection controls is observed, not interpreted as zero SDK action processing. Real native bar clicks instead produce visible selection transfer and roughly 161–193 changed original pixels as the colored bar's previous/new selection is recolored. Matched native ACTION4 and ACTION5 after bar selection were accepted by the official SDK in their own trials; none established SDK level3.

**Established for the tested source state:** All three previously color8 bars, as well as the initially selected color9 bar, are individually selectable/selected in original stage2 through proper native coordinate ACTION6, with consistent observable highlighted-bar selection. No source goal target or hidden mechanism has been inferred.

## Next bounded native experiment
Use the independently verified four-bar native click controls for a **prospectively bounded four-bar movement/commit study**, preserving true pre-ACTION5 bar positions, legal movement, complete returned native animation frames and the official SDK `levels_completed>=3` / WIN. Avoid assuming the stage1 three-bar alignment predicates transfer to this four-bar level; the middle and bottom bars begin near the right screen boundary and therefore require source-observed movement bounds before choosing large positive shifts. Preserve all source positive/negative evidence, true click colors, original raw NPZ/JSON and rights. **Game is verifiably at 2 of 6 levels, not solved.**
