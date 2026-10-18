# ARC-AGI-3 — original 48-law F3 investigation instructions

**Current mathematical referent:** the exact two-predecessor window family in [work/arc_like_maze/window_combined.py](../arc_like_maze/window_combined.py) and its [proved scope](../arc_like_maze/WINDOW_COMBINED.md). **Previous work on the nine-world phi family has been archived**, not reinterpreted as evidence for these forty-eight laws.

This is a **real native ARC game investigation**, not an ARC-inspired artificial game, a replacement bot, a canned route, or a proof that native ARC is the F3 construction. The objective remains eventual native game solving, but this checkpoint only establishes a mathematical source and falsifiable native relationship tests.

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
