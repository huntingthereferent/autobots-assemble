# Inverted A/B: existing agent construction-direction test

Date: 2026-10-08
Scope: local evidence experiments; GitHub/repository code unchanged.
Status: PROTOTYPE FEASIBILITY SUPPORTED, PRODUCTION INTEGRATION NOT DONE.

## Question

Can the existing A/B agent consume an inverse of a witnessed continuation
category, construct testable world alternatives, and return them to the
same ordinary A/B evaluator without promoting generated ideas into evidence?

## Tests run

Existing Continuity runtime suites:
- runtime.ab_information: 4/4 pass.
- runtime.ab_loop: 8/8 pass.
- runtime.agent_lineage: 10/10 pass.
- runtime.arc_native_observer: 2 pass, 1 skipped (3 cases).
- runtime.observed_evaluator: 14/14 pass.
- runtime.combined_evaluator: 3/3 pass.
- runtime.orchestrator: 6/6 pass.

New isolated tests outside repo:
- test_inverse_ab_agent_construction_2026_10_08.py:
  15/15 pass.

TOTAL unittest: 63 cases, 62 passed, 1 skipped, 0 failures.

Additional executable native integration probes:
- _tmp_inverse_ab_existing_agent_native_gate.py: PASS.
- _tmp_inverse_ab_native_phase_corrected_witness.py: PASS.

These native probes are separately counted, NOT silently added to unittest count.

## Construct direction

Use the same information-minimal A/B quotient q_W for witnessed states,
and its inverse F_W(c) = {o : q_W(o) = c}, preserving the distinct
original source histories (in ARC SK48, observed alternate histories
(2), (1,7), (4,7) were a supported finite-horizon source fiber).

Generate *candidates* from this inverse fiber. Do not label any new
candidate as a measured environment state before testing.

Proposed mathematics, NOT integrated runtime implementation:

    X_n --Q_W--> C_n
    C_n --Q_W^(-1) + project--> Xhat_(n+1)
    Xhat_(n+1) --native witness--> X_(n+1)
    X_(n+1) --existing A/B--> corrected C_(n+1)

A projection of child state into parent world may fail to commute
with a world action. The failure is itself evidence for a needed split.

## Nested-world mathematical test

Synthetic two-chamber model, state=(room,gate0,gate1).
"step" crosses the active chamber boundary only if that chamber's
gate is open. "toggle" flips the active chamber gate.

Four base configurations at room 0:
    room0 closed/gate1 closed
    room0 closed/gate1 open
    room0 open/gate1 closed
    room0 open/gate1 open

At one-step prediction horizon, A/B finds TWO continuation classes,
sufficiently identified by gate0 alone.

At two-step prediction horizon, there are THREE continuation classes:
    (0,0) => room 0 then room 0
    (0,1) => room 0 then room 0
    (1,0) => room 1 then room 1
    (1,1) => room 1 then room 2

Old relation subsets yield four proof blocks, too fine to exactly
represent the three-class continuation quotient; existing
runtime.synthesize_continuation_relation synthesized the necessary
three-class relation. Its inverse restores all four originals without
inventing a fourth class.

Thus gluing two chamber worlds exposes an interaction not predictable
from only the local first-chamber state. The parent abstraction that
keeps only room position fails; the fully sufficient control state
commutes with the rule under this finite model.

All math tests passed. This is a SYNTHETIC control world, not a
demonstration that ARC's original world uses these particular rules.

## Actual native ARC -> existing AgentLineage

Using real SK48 SDK frame transitions and one temporary
EcosystemService/AgentLineage with its existing witness evaluator:

1. Correct before/after native measurement and predicted outcome:
   COMPLETE, A/B=MOVE, one admitted witness. PASS.

2. Same native measurement with wrong predicted-after value:
   PARTIAL, prediction_matched=false, zero admitted witnesses. PASS.

3. Candidate with no registered native measurement:
   READY, zero admitted witnesses, no execution. PASS.

4. Known native Level2 ACTION2 alters continuation phase but returns
   the SAME public frame: frame-only ARC observer recorded UNKNOWN.
   This is an honest current observation limitation, not a solved
   movement. PASS expected boundary.

A separate two-run real SK48 continuation test measured suffix
ACTION1 x3 from Level2 root before vs after ACTION2.
The returned initial public state was exactly identical, but the
three-step public continuation differed, matching prior recorded
native witnesses. A local test observer provided independently
content-addressed native future traces to the SAME existing
EcosystemService/AgentLineage evaluator. It returned COMPLETE/MOVE,
with "public_state" preserved, "future_111" changed, and a real
measurement witness. PASS.

This only demonstrates that the existing evaluator can use such
witnesses if supplied. Production's ARCFrameObservationProvider
currently sees frames, not independently replayed continuation
signatures; its source code was NOT edited.

## Boundaries / what failed to carry forward automatically

- The original frame-only observer cannot attest a same-frame native
  phase difference. Extending the observation contract to include
  reliable action-history and/or earned continuation evidence is
  required to preserve that transition.
- The construction adapter tested here is LOCAL experimental code,
  not a registered production agent capability.
- This is not a new second agent or autonomous world generator.
- No human maze/game environment has been implemented.
- No cross-domain performance gains measured.
- The fractal embedding f_i(t)=(t+2i)/5 remains a chosen spatial
  projection; the native game only supports finite source-history
  equivalences under tested horizons, not the infinite geometry.
- The real native phase corrective test used two fresh replays and
  previously established suffix 111; it is repeatability evidence,
  not independent unknown-game discovery.
- Every constructed category and its proof must retain the W/horizon
  contract; an unseen continuation can split a prior category.

## Minimal integration recommendation (not executed)

1. Retain existing runtime.ab_information and AgentLineage.
2. Add opt-in construction projection that consumes
   ABInformationState plus witnessed source locators.
3. Give outputs PROPOSED status by default, never MOVE.
4. Send proposed transitions to the existing native observation
   provider and A/B evaluator.
5. Extend public observer contract to carry independently witnessed
   action-conditioned continuation distinctions (including
   same-visible-frame phase), not assumed "phase" metadata.
6. Promote on actual valid witness only; keep counterexamples as
   PARTIAL and unsupported candidates as READY/UNKNOWN.
7. Add cross-layer commuting-square tests before claiming world
   composition correctness.

Local evidence artifacts:
    test_inverse_ab_agent_construction_2026_10_08.py
    AB_INVERSE_AGENT_NATIVE_GATE_TEST_2026-10-08.json
    AB_INVERSE_AGENT_NATIVE_PHASE_CORRECTION_2026-10-08.json
    _tmp_inverse_ab_existing_agent_native_gate.py
    _tmp_inverse_ab_native_phase_corrected_witness.py

Bottom line: Existing agent can evaluate admitted inverse-generated
constructions and catch a missing nested-world distinction, while
currently unobserved construction and invisible phase boundaries
remain unpromoted. Production adapter still needs implementation.
