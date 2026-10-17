# Continuity Engine — A-invariant addition

Adds a separate **A-invariant watch** alongside the existing B-invariant Cyclic Action watch, together with A-to-full-A/B non-promoting handoff, explicit invariant-set transport for either generator, research-board staging, and replay validation.

## Verified local results

- **65/65** local compatibility tests passed (47 previous regression tests + 18 new A-invariant tests).
- A-invariant first-coordinate orbit: **3 states**, A is a 3-cycle; positive restricted A witness at power 3.
- Earlier B-invariant first-coordinate fiber: **81 states**, preserved separately under B.
- Full action: **243 states**; a pair can be A-only conjugate and B-only conjugate on their respective carriers yet **not** be full A/B conjugate.
- Negative A-to-full handoff verifies **6** restricted A transition equations; B-to-full verifies **162** restricted B transition equations.
- Under the tested positive full conjugacy, the named A carrier **does not** coincide with its transported image, while the named B fiber **does**.

The original B-only scope remains unchanged. No single-generator proof implies a full A/B result. `A` is identical across this WindowProcess family, so **A-only equality by itself provides no discrimination between different coupling laws.**

## Code

- `research/a_invariant_action.py`: native A generator invariant-carrier watch, explicit witness and replay.
- `research/continuity_engine.py`: admit A-only scope alongside B-only and full AB, preserving separate serialized questions.
- `research/cross_scope_handoff.py`: A or B parent → full A/B child; exact law pair and generator restriction proof.
- `research/invariant_transport.py`: verify `H(C)` invariant for either generator under already established full A/B conjugacy; exact transport replay.
- `research/continuity_board_bridge.py`, `research/scope_board_bridge.py`: board-candidate output with A/B scope integrity.
- `network/tests/test_research_a_invariant_action.py`: 18 new tests; existing 47 regression tests included.

## Run

```bash
python test_support/run_local_compatibility.py
```

The isolated local harness uses test-only reproductions of existing repository dependencies. See [the mathematical and verification report](docs/A_INVARIANT_EXTENSION_REPORT.md) for exact outcomes, limits, reproducibility, and compatibility instructions.

**GitHub/repository unchanged.** This is a download-ready integration candidate, not a deployed or autonomously running engine.