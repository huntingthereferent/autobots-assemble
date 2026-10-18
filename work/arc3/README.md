# ARC-AGI-3 — 48-law native investigation lane

**Active checkpoint:** restart the real ARC investigation using the repository's already-proved **48-law two-predecessor F3 window family**, rather than the earlier nine-law phi worlds. The mathematical source is [window_combined.py](../arc_like_maze/window_combined.py) with [48-law proofs and counterexamples](../arc_like_maze/WINDOW_COMBINED.md). The active instructions are [AGENTS.md](AGENTS.md).

This is **one experimental ARC agent and the existing Work observation lane**. It is not a fabricated ARC engine, autonomous bot population, new scheduler, universal theory, or successful public/hidden competition entry.

## Active agent and mathematical scope

The [official single-file entry](agent/my_agent.py) contains the literal mathematical A/B transformations for all 4×2×2×3=**48 source laws** (support, pulse, balanced edit, nonlinear shear coefficient), source-conformance tested over all 27 depth-three states. It keeps the original **16 marked/rooted equivalence classes** distinct from **14 full-state conjugacy classes**, including explicitly nonrooted cases where the alignment moves the origin.

The executable investigates **necessary rooted word equalities** only after marking a pair of observed native simple controls as **provisional** mathematical generators. It records actual native pixel observations and may refute the entire proposed direct mapping. It does **not** promote native action IDs to proven F3 generators. For click-only games such as FT09, it does not fabricate ACTION6 coordinates. There is no demonstrated ARC puzzle-solving policy in this source.

### Reproducibility

    python -m unittest -v network.tests.test_arc3_f3_agent

The [focused mathematical CI](../../.github/workflows/arc3-f3-agent.yml) also tests the historical nine-law entry **against its archive only**, never against the new canonical agent.

The [official native test workflow](../../.github/workflows/arc3-f3-native-smoke.yml) exercises the same 48-law agent against public **SK48, LS20, and FT09** and uploads actual raw frames and rooted-law evidence. Actual outcomes must come from successful GitHub runs, not from mathematical unit tests alone.

## Workstation and native observation sources

- [work/arc3/lane.py](lane.py) preserves the existing read-only native trace-inspection and Work journal mechanism; it is not a native action actuator.
- [Official ARC operator shell](../../research/dives/ARC3-TRACE-001/direct_agent/operator_shell.py) exposes actual commands (show, info, act N, act 6 X Y), native frame hash and append-only observation log.
- [Operator manual](../../research/dives/ARC3-TRACE-001/direct_agent/OPERATOR.md) and [first-contact runbook](../../research/dives/ARC3-TRACE-001/direct_agent/RUNBOOK.md) keep manual, autonomous, development-tuned and hidden evaluations separate.
- [Source-owned native observation adapter](../../runtime/ARC_NATIVE_OBSERVATIONS.md) can report before/after effects without pretending to choose actions.

To inspect a native observation log from the operator shell, use:

    python -m work.arc3.lane inspect --trace runtime/data/arc3/native-session.jsonl

To record it into the already existing workstation journal:

    python -m work.arc3.lane record --journal runtime/data/workspace.jsonl --trace runtime/data/arc3/native-session.jsonl

These commands only work when a real operator-produced native trace exists. They do not generate observations or simulate ARC.

## What is preserved from the earlier nine-law route

The previous nine-world mathematical experiments and their native trials (including LS20 movement/trace, SK48 and FT09 comparisons) remain immutable historical evidence under [runs/](runs/). They were **not tests of the 48-law window**.

For unambiguous reproduction:
- [Previous agent](archive/nine_law_agent_2026-10-17.py)
- [Previous research instructions](archive/NINE_LAW_AGENTS_2026-10-17.md)
- [Previous full Work README](archive/NINE_LAW_README_2026-10-17.md)
- [Previous nine-law regression](../../network/tests/test_arc3_nine_law_archive.py)

The repository's independent [finite mathematical work](../arc_like_maze/README.md) remains distinct from native ARC evidence.

## Current boundary

**Established mathematically:** 48 source laws, 14 full-state and 16 rooted classes with exact source witnesses.

**Not yet established natively:** a verified mapping from ARC control actions/coordinates and observed game state to those source laws, any source-to-native conjugacy, an ARC win, or a competition score.

The next experiment must produce a **predeclared observable relation**, actually intervene in a native game, preserve counterexamples, and stop rather than asserting an unsupported equivalence. See [AGENTS.md](AGENTS.md) for the source/evidence contract.
