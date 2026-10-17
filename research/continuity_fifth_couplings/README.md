# Continuity Engine — all fifth-coordinate couplings

This is a **scoped finite mathematical research package**, not a replacement for
the existing Cyclic Action Engine's B-only research entry. The state space is
exactly \(\mathbb F_3^5\) with 243 states and \(3^9=19,683\) coupling laws.

It contains the native finite-field action (`core.py`), the four
linked orbit-incidence invariants, exact positive R/S transports, replayable
pairwise research records, and two independently motivated classification audits.

From the repository root:

```bash
python -m unittest network.tests.test_continuity_fifth_couplings -v
python -m research.continuity_fifth_couplings.verify
python -m research.continuity_fifth_couplings.verify_pairs
```

The full census is reproducible from \`verify.classify()\` (rather than a
checked-in multi-megabyte generated output). Rebuilding it runs all of the
declared finite-law enumeration. The included \`portable_pair_checks.json\`
records the previous independent pair-search check, whose wall time depends on
the execution machine.

The 1,098-class result holds only for the first four-coordinate rules fixed
in this grammar. It does not establish classification of all finite A/B actions,
arbitrary dimensions, or native ARC solving. UNKNOWN must not be upgraded to
conjugacy from fingerprint agreement alone.

See [the mathematical classification report](CLASSIFICATION_REPORT.md) and
the wider [collected experimental history](../continuity_engine/collected/README.md).
