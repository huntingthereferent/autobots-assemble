# Continuity Engine — invariant intersections and alternating saturation

The next finite-mathematical integration after A-only, B-only, and full A/B witnesses.

**New proven observation:** A minimal A-invariant carrier (3 states) and a first-coordinate B-invariant fiber (81 states) have a singleton intersection in the declared F3^5 grammar. The intersection need not be invariant under either action. The generator-orbit closure operations do not generally commute: from `(0,0,0,0,0)` in the selected source law, A then B reaches 55 states while B then A reaches 81.

**New negative witness:** For the previously hard nonconjugate pair, all 243 starting states yield different unrooted three-stage A→B→A orbit-saturation size histograms. The first two stages match; the third proves full A/B nonconjugacy. This is a necessary invariant, never a positive equivalence test.

**Positive transport:** Under an independently verified full A/B conjugacy, the engine computes and verifies `H(A_carrier ∩ B_carrier) = H(A_carrier) ∩ H(B_carrier)` without presuming either transported carrier matches the original named target.

The existing `ContinuityEngine` admits this as a fourth distinct area, `finite_action/AB_saturation`. Existing A-only, B-only, full-A/B correspondence, cross-scope handoff, and board tests remain intact.

## Verification

- **84/84** local compatibility tests pass, including **19** new tests.
- **702 laws** checked; **18** three-step fingerprints (coarser than the previously classified **39** full conjugacy classes).
- **341,172** labeled-generator transitions independently crosschecked against direct finite-field equations; all 702 three-step histograms independently reconstructed.
- **No live GitHub edits** or board publication. The test harness is a reproduction of dependencies, **not** a test against the exact current GitHub modules.

See the [mathematical report](docs/A_B_INVARIANT_INTERSECTIONS_AND_SATURATION_REPORT.md) for exact scope, witness matrices, known limitations, and reproducibility.

```bash
python test_support/run_local_compatibility.py
PYTHONPATH="$PWD:$PWD/test_support/test_only_modules" python examples/build_verified_witnesses.py
PYTHONPATH="$PWD:$PWD/test_support/test_only_modules" python examples/reproduce_702_saturation_census.py
PYTHONPATH="$PWD:$PWD/test_support/test_only_modules" python examples/independent_action_crosscheck.py
```

Source files belong under `research/`; new tests are under `network/tests/`. No repository files were modified; this is an installable candidate archive, not an already-deployed engine.