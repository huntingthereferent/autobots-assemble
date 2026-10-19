# ARC-AGI-3 — original 48-law F3 investigation instructions

**Current mathematical referent:** the exact two-predecessor window family in [work/arc_like_maze/window_combined.py](../arc_like_maze/window_combined.py) and its [proved scope](../arc_like_maze/WINDOW_COMBINED.md). **Previous work on the nine-world phi family has been archived**, not reinterpreted as evidence for these forty-eight laws.

This is a **real native ARC game investigation**, not an ARC-inspired artificial game, a replacement bot, a canned route, or a proof that native ARC is the F3 construction. The objective remains eventual native game solving, but this checkpoint only establishes a mathematical source and falsifiable native relationship tests.

## Resume here

**Latest official original SP80 native experiment:** [three selectable bar placements and actual source SDK objective](runs/WINDOW48_SP80_BAR_PLACEMENTS_2026-10-19.md), [real original SDK GitHub Actions run #39299998030](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39299998030), [untouched original JSON + full returned 64×64 SDK NPZ source artifact #12210636667](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39299998030/artifacts/12210636667), SHA256 independently verified `607ee005475b299bd3cfda5f940ca14f743a1d9ea073b10d92aa554b76724b64`. **32 independently reset genuine SP80 stage1 games**, 16 predeclared concrete proper-coordinate click/bar-placement words each two copies, **446 genuine SDK action responses, 38 true coordinate-bearing ACTION6 clicks, and 3,270/3,270 independently reverified complete original returned-frame x/y+old/new native color differences** against the raw NPZ source images, zero mismatches; all real `levels_completed=1/6`, SDK `NOT_FINISHED`, ZERO level2 or WIN.

**Observed original-source bar placements, not inferred objectives:** actual stage1 source frame has native selected color9 x20–39,y36–39; native upper color8 x8–19,y16–19; lower color8 x28–39,y24–27. Proper source `ACTION6,data={"x":x,"y":y}` selects a bar, ACTION1/2/3/4 move it in already-observed four-cell increments, and ACTION5 yields full actual returned animation. This NEW source-native study deliberately moved lower→upper and upper→lower, and original first bar→both original unselected regions in two orderings, plus multiple selected bars on same observed y row and no-move controls. The actual before-click pixel and complete source frame record show all 32 trials finished; after ACTION5, the color9 highlight may jump to a different bar, so **pre-ACTION5 attempted geometry does NOT equal post-ACTION5 selected display**. Both unselected→other-region routes commonly end showing x20–39,y36–39 first source bar; one source first-to-lower control actually retained x28–47,y24–27 a 20×4 selection. ZERO authentic SDK level2. Visible bar overlap, source glyph color11 and ACTION5 animation pulse are NOT established game targets.

**Complementary original-native temporal research:** [matched-age 48-game study](runs/WINDOW48_SP80_MATCHED_GEOMETRY_2026-10-19.md), genuine 4,816/4,816 verified returned-frame effects, shows native selected-bar geometry under matched source movement suffix can produce ACTION5 **22,23,26,28 frames** at same source row63 timing; [exact interior 32-game study](runs/WINDOW48_SP80_EQUAL_INTERIOR_HISTORY_2026-10-19.md) has 3,340/3,340 native returned-frame effects, and 42/42 identical 22-frame ACTION5 at one byte-identical source interior across varying history/boundary. These results are bounded; the universal 22-frame template is FALSIFIED. Earlier last-frame-only native observations selected `obs.frame[-1]`, exact as final frame but NOT complete source animation. Original ACTION6 without `data={"x":x,"y":y}` was NOT an intended object-click control. Preserve all corrected source scope and negative evidence.

**On "continue":** stop selecting arbitrary bar color intersections as assumed goals. A genuine original SDK level0→level1 witness already exists and is especially useful: within real `454545` stage entry, ACTION5 on steps 2,4,6 returned **22,28,20 original frames**, with SDK levels `0,0,1` respectively; this is native source observation, not yet an identified objective. Prospectively compare FULL 20-frame authentic native level-advancing ACTION5 animation with 22/28-frame stage0 non-advancing and 22/23/26/28-frame native stage1 non-advancing, preserving all x/y native colors, SDK win/levels, actual pixel/click context and counterexamples. Determine whether any **observable preterminal state or returned-frame event** distinguishes true stage progress; no invented hidden mechanics. Original F3-48 source mathematical laws, canonical agent and owner rights unchanged, no cloned game, bots or claimed six-level win. Source SP80 still unsolved level1/6.

## Current native SP80 boundary — longer histories (Oct 18, 2026)

[Source-owned long-history and action-position evidence](runs/WINDOW48_SP80_NATIVE_LONG_HISTORY_2026-10-18.md) now bounds the previous 50/50 exact pre-color result. Eight longer words across 32 actual native resets / 356 actions yielded **56/66 exact ACTION4 full native changes**, despite all 2,078 observed native changed pixels and native before/after colors still being included: **72 extra source predictions** occurred. A separately predeclared streak-versus-position control (32 more resets, 348 native actions) gave **88/102 exact**, with **0/78 errors at word steps 1–6**, but **2/12** inaccurate at word step 7 and **12/12** inaccurate at step 8. This shows target pre-action pixel color alone is NOT sufficient; native action history/progress matters. All actual predictions and counterexamples, and interrupted native level-change trials, remain source-owned.

Independent three-reset native controls additionally verified the alternate public SP80 one-level word **5454545** at action seven (3/3), with prefix **545454** not advancing (0/3); this is ONE native game level, not a full game win. The two frozen native geometry variants remain indistinguishable. The original F3-48 mathematical A/B and canonical agent remain unchanged; native stage effects are **not an F3 generator or rooted conjugacy**.

## Source contract — do not silently switch back to nine laws

The original family is **48 DISTINCT concrete F3 transition laws** parametrized by:
- support k=0..3
- pulse e=0..1
- balanced edit t=0..1
- nonlinear shear chart c=0..2

At depth three the marked mathematical origin is (0,0,0), and the source transformations are

    A(u,v,z) = (u+1, v, z) mod 3
    B(u,v,z) = (u, v+u+1, z+q(u,v)) mod 3

    q(u,v) =
        [u=2 and v<k] + e[u=0,v=0]
        + t([u=1,v=0]-[u=1,v=1])
        + c((v+u+1)^2 - v^2)   mod 3

The canonical [single-file ARC SDK entry](agent/my_agent.py) duplicates these equations **because the official Kaggle build embeds one file**. The [source-conformance suite](../../network/tests/test_arc3_f3_agent.py) checks all 48 laws against original code for every one of 27 finite states and both A/B transformations, plus triangular inverses, rooted words, and origin-moving examples. Do not import local repository packages from the submission file.

### Critical equivalence distinction

- The 48 **concrete** transition laws form **14 full-state action-labeled conjugacy classes**.
- They form **16 origin-preserving conjugacy classes**, each containing three chart worlds.
- The extra mergers at support k=0/3, pulse e=1 between different balanced edits are **full-state but nonrooted**. The proved state map MOVES the origin; exact rooted collision words prevent it from being silently treated as rooted alignment.
- Source fixed-word invariants B, BBB, AABAB and ABABAB certify particular full-state distinctions, but a single native rooted trace CANNOT supply counts over every mathematical state. Never report full-state class membership on that evidence.

The source A has order three. Any proposed native generator must satisfy its applicable rooted state/word relationships. A failed raw-frame A^3 test rejects that **proposed direct native-to-source interpretation**, not the F3 law itself.

## Observation and admission

1. Preserve every native 64x64 original color. Never map ARC colors, pixels, or positions modulo three just to obtain a fit.
2. Treat native control IDs as interface affordances, **not mathematical action labels**. ACTION6 is a coordinate-parameterized action, not a missing pair of arrow keys. A pair of available simple controls may be used as an **explicit provisional falsification experiment**, never promoted to verified A/B automatically.
3. Predict source-law rooted equalities before applying a real native action. Distinct native full frames REFUTE a proposed equal endpoint in a direct state-preserving mapping. Matching visible frames never certify identical hidden states or a bijection.
4. On contradiction, preserve the exact source law indices, action words, frame hashes, and native action IDs. The canonical agent **stops at an evidence wall**; do not reset and retry the same excluded family, issue fabricated midpoint clicks, or switch to conventional ARC hints as if they originated in F3.
5. Mathematical source identities, 16 rooted classes, 14 full-state classes, native evidence, actual game wins, and competition scores remain separate claims.
6. The real native game operator and Work lane may record observations, but no new bot, auto-generated puzzle engine, or alternate task scheduler belongs in this experiment.

## First verified native 48-law checkpoint

[The 48-law restart native record](runs/WINDOW48_RESTART_2026-10-17.md) records new actual native tests: the first SK48 and LS20 runs each used six actions, zero levels, and reached an explicit rooted 48-law WALL under a **provisional** ACTION1=A and ACTION2=B mapping. FT09 exposed only coordinate-action ACTION6, so the native runner recorded its true available actions and reset frame and executed **zero** invented clicks. The [focused official native run](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39092926137) succeeded and preserves raw native frames. These are bounded falsifications of direct action-ID mappings, **not** successful source/native conjugacy or ARC solving.

## Current source-evidence boundary: 25-game A-cube screen

[Native Window48 A-cube preflight and rooted question plan](runs/WINDOW48_NATIVE_ROLE_PREFLIGHT_2026-10-17.md) now supersedes ad hoc direct control assignment as a useful new probe. From actual public game resets in 25 games, 75 distinct simple native control probes (225 native actions) yielded 74 direct raw-frame A-cube counterexamples and one trivial/degenerate visible return; NONE was an admissible strict nontrivial three-state orbit. Seven native game interfaces offered no eligible ACTION1..5. This only refutes the tested direct, rooted, full-visible-state assignments.

The source mathematical follow-up is SIX actual rooted collision/equality questions from [the original 48-law rooted plan](window48_rooted_questions.py), independently tested to distinguish all 16 marked classes across all 48 concrete laws while refusing to collapse full but nonrooted conjugacies. These are not native ARC observations, and all six remain mathematical-only until a candidate native transformation and observable state factor pass the source A-cube prerequisite. Never infer the 14 full-state class count from single-origin game frames.

## Reproduce

From repository root:

    python -m unittest -v network.tests.test_arc3_f3_agent

For historical reproducibility only:

    python -m unittest -v network.tests.test_arc3_nine_law_archive

For bounded **actual native ARC experiments** using the official ARC SDK + agent framework, run the existing [native smoke](native_smoke.py) through [GitHub Actions](../../.github/workflows/arc3-f3-native-smoke.yml). It records exact agent SHA-256, native frame hashes and arrays, provisional control pairing, surviving original 48 source law parameters, rooted class keys, and an explicit wall. FT09 (click-only) must not issue a fictitious A/B action.

[The Work lane](README.md) remains a source-bound observation and journal surface; it does not simulate game transitions.

## Preserve prior evidence

The [archived nine-law entry](archive/nine_law_agent_2026-10-17.py), [archived instructions](archive/NINE_LAW_AGENTS_2026-10-17.md), [archived Work README](archive/NINE_LAW_README_2026-10-17.md), and [nine-law archive tests](../../network/tests/test_arc3_nine_law_archive.py) preserve the entire earlier route. Its native records remain in [runs/](runs/), with explicit historical dates and **no claim** that they tested the original 48-window construction.

**Next admissible research movement:** investigate an explicitly observed, independently verified native action-role/state correspondence for the **48-law marked window**, using the rooted/full-state distinction. If native evidence supplies no such correspondence, return WALL rather than expanding a false family or claiming an ARC game win.

## Composite native Window48 A-cube boundary and independently reproduced level effect

[The current native composite report](runs/WINDOW48_NATIVE_COMPOSITES_SP80_2026-10-17.md) now rules out a strict period-three return on **complete visible frames and each of 16 exact native-color masks** for all **257 fully completed** ordered distinct two-simple-control macro trials among 25 public native game roots (258 candidates, 1,548 actual environment actions; one trial interrupted by a real level transition). No F3-48 generator or rooted class correspondence was proven, and the six source-certified rooted questions remain mathematical-only.

The separately rerun **SP80 native** experiment observed the action word 454545 advance actual levels_completed from 0 to 1 at action six in **2/2 independently reset trials**, while the official game state remained NOT_FINISHED. This is **native level progress, not a full win and not a mathematical F3 A cycle**; source A cubed returns to its original state, whereas this native sequence changed level. Preserve negative controls, action sequences, actual level counter and the distinction from F3. Do not import the discovered sequence as an unexplained universal game-solving policy.

## SP80 level-0 to level-1 native transfer boundary

[Actual SP80 stage-transfer experiment](runs/WINDOW48_SP80_STAGE_TRANSFER_2026-10-18.md) tested 11 predeclared level-1 suffixes, twice each, after independently observing the native level-0 six-action prefix 454545. **22/22** fresh resets reproduced level 0 -> 1; repeating 454545 on level 1 produced **0/2** level-2 advances. Native level-1 initial frames were identical in all 22 resets and differed from level-0 roots at **1,136 exact original color pixels**. Native ACTION4/ACTION5 pixel effects are stage-specific (upper-band motion in level 0 versus lower-band in level 1). Two ACTION5-only suffix trials were incomplete due to nonstandard native image frames; these are UNKNOWN.

This establishes a **real native non-transfer result and source-owned observed geometry**, NOT an F3-48 generator, a source action-role alignment, full native hidden-state isomorphism, or an entire game win. The original 48 mathematical laws and canonical MyAgent are unchanged. Do not assume the level-0 sequence is a reusable solver or fit arbitrary F3 coordinates to the measured pixels.

## Native SP80 spatial registration after stage transfer

[Held-out geometric observation](runs/WINDOW48_SP80_HELDOUT_GEOMETRY_2026-10-18.md): a **predeclared** eight-D4-symmetry and integer-shift registration was fitted to a single actual native stage-0 versus stage-1 ACTION4 change mask, then frozen for held-out ACTION4 changes and three real fresh SP80 resets (36 actual actions). A reflect_y+shift (8,-8) mapping and the simpler translation-only shift (8,20) both matched **32/33 target changed pixels** on training, and scored **0.96992 mean held-out F1**, with **0/6 exact held-out masks**. The two alternatives are NOT distinguishable by accuracy on this evidence. They give identical pixel predictions on two ACTION4 changes and differ by four predicted pixels on the third, without a score difference. Native ACTION5 mask controls had zero overlap (often with clipping).

This is a repeatable **partial observable alignment**, not a unique spatial symmetry, source F3 state map, rooted conjugacy, invertible full board action, or game win. In particular 34-versus-33 mask cardinality rules out a bijection between the two complete ACTION4 changed-pixel sets. Do not promote a fitted pixel translation or reflection to source mathematical A/B.

## Current stage-to-stage native color evidence and remaining WALL

[SP80 actual native color and boundary investigations](runs/WINDOW48_SP80_COLOR_BOUNDARY_2026-10-18.md) tested previously FROZEN stage-0 to stage-1 geometry in new real native action contexts. Across 28 clean resets/148 native actions, the frozen spatial mappings matched **704/704 exact original native from-color/to-color transition labels** at their 704 overlapping ACTION4 changed pixels. A separate source-recorded residual showed all 34 unpredicted stage-1 target changes were native **14 to 0**, on the bottom row y=63, while 44 source edge changes of the same color pair clipped.

That source observation fixed a bottom-edge action-position completion rule BEFORE five NEW context words were tested across 20 more native resets and 152 actual game actions. The rule plus either unchanged geometry mapping predicted all **1,070/1,070 actually observed ACTION4 color transitions** in 32 native action comparisons, but **only 18/32 complete effects were exact**, because 20 spurious 14-to-0 changes were predicted near the far right edge. Keep these false positives as source-owned evidence and a WALL against declaring an exact native state transform. Reflection and translation remain tied and cannot be uniquely identified here.

This is native empirical relation discovery **within public SP80**, NOT proof of F3-48 A/B roles, F3 color mapping, rooted/full-state mathematical conjugacy, closure of a factor, ARC game completion or an autonomous solving policy. The canonical agent and original mathematical laws stay unchanged.

## Historical checkpoint — pre-color transition witness (bounded by longer histories)

[Actual native pre-color occupancy test](runs/WINDOW48_SP80_NATIVE_OCCUPANCY_2026-10-18.md): Six previously untested public SP80 action contexts, 24 fresh native game resets and 216 real actions independently confirmed that a previously specified **target PRE-action native color** admission condition eliminates all 50 overpredicted stage-1 ACTION4 changes from the frozen geometry-plus-bottom-boundary models. Across 50 full ACTION4 effect comparisons, each frozen model predicted all 1,680 observed actual native before/after color changes, with **50/50 exact full transition maps, 0 false positives, 0 misses, 0 miscolored pixels**. All 50 rejected predictions expected native 14->0 where the actual *before* pixel was native color 12. The unshifted identity control stayed at 0/50 exact. Independent native CI and a before-state-only gate regression preserve the result.

This is a **conditional native transition relation only**: the projection takes BOTH an observed matching stage-0 native action effect and the real level-1 pre-action frame. It is NOT an action-selection algorithm, goal solver, validated 48-law F3 generator, hidden-state identity, globally invertible pixel conjugacy, or proof that either competing spatial map is uniquely true. F3 mathematics and canonical agent remain unchanged.
