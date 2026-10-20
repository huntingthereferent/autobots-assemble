# Continuity Engine — verified cross-scope B → full A/B handoff

**Research prototype, not a GitHub merge.**

This package adds `research/cross_scope_handoff.py` and
`research/scope_board_bridge.py` to the previous verified Continuity Engine
and finite full A/B correspondence integration.

### Result

For the exact same pair of five-coordinate `WindowProcess` laws:

- On `u=0`, restricted B: **three 27-cycles in each law**, verified **B-only conjugacy** on 81 states.
- On all `F3^5`, full labeled A/B: **no conjugacy**, all 243 target origins eliminated in 17 path-collision checks.
- Both remain simultaneously valid. The original B-only question is **never rewritten**.

### Scope contract

A cross-scope link proves **the same B-transitions restrict to the earlier
B-invariant carrier** in both laws (162 equations), not that an earlier
B-intertwiner extends to A/B. The child is a new question with its own
scope, witness and continuation history.

### Reproduction

In a repository checkout containing `work/arc_like_maze/window_two.py`,
`work/arc_like_maze/cyclic_action_engine.py`, and `runtime/research_board.py`,
copy the supplied `research` and `network/tests` files into their matching
paths and run:

```
python -m unittest network.tests.test_research_cross_scope_handoff network.tests.test_research_full_action_correspondence network.tests.test_research_continuity_engine network.tests.test_research_continuity_board_bridge -v
```

The included **test-only compatibility harness** runs without that checkout:

```
python test_support/run_local_compatibility.py
```

It uses a faithful finite-field arithmetic reproduction plus a small
contract-compatible **stub for the older B-only engine**, not the repository
implementation. All **47/47** tests in that harness passed. The previous
turn's exact-module 74-test success refers to an earlier baseline, not this
new cross-scope code; fresh repository verification remains open.

### Files

- `research/cross_scope_handoff.py`: replayed parent/child proof relationship
- `research/scope_board_bridge.py`: separate reviewable board checkpoint
- `network/tests/test_research_cross_scope_handoff.py`: 18 new regression tests
- `docs/CROSS_SCOPE_HANDOFF_REPORT.md`: mathematics, proof limits and evidence
- `examples/`: three replayable cross-scope handoff records and independent
  control summary (generated using the test-only B-only adapter)
- `test_support/`: isolated reproduction; does not replace repository sources

Nothing was committed or written to the user repository.