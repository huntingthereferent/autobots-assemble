# B3 — Native worker feedback into workstation continuation

**Current result:** B2 can open and preserve coordination lanes; B3 takes a
single such lane from an explicitly admitted source-owned native job to an
independently reverified return, then records that return against the exact
original lane in the existing `RuntimeJournal`.

This is a bounded, *invoked* worker movement, **not** a daemon, an AI coding
agent, or a new supervisor. It does not bypass the existing `HandoffRuntime`,
`branch_help`, or source-native verification controls.

## Native path

1. A/B starting lanes are seeded explicitly. A domain-native observation
   verifier authenticates a proposed branch before B2 records a derived lane.
2. A source-native worker is admitted through
   `WorkstationContinuationHarness.admit_native_help`. Only registered
   source-owned capabilities may be staffed. A real native job remains READY.
3. `WorkstationNativeFeedback.advance` **revalidates the initial branch
   observation** before executing. It requires an exact job ID and
   `allow_local_execution=True` supplied by a trusted caller.
4. The **existing** `systems.workspace.controls.run_job` executes the
   registered native subprocess and re-verifies it with its independent source
   verifier. B3 never executes arbitrary source itself.
5. The **existing** `systems.workspace.branch_help.verify_return` checks
   source edition, native status, result, and provenance again.
6. B3 saves one `WORKSTATION_NATIVE_RESULT_VERIFIED` on the same derived
   lane, identifying the exact opening/job, canonical result and evidence
   digests, and source edition fingerprint. The original A/B lanes remain.
7. Replaying the same invocation re-verifies the same job without executing
   the completed subprocess twice or duplicating the feedback event.
   Altered source/result evidence is rejected rather than rewritten.

## Actual repository integration verification

```bash
python -m pip install 'cryptography>=45,<47'
python -m unittest -v network.tests.test_workstation_harness \
  network.tests.test_workstation_native_feedback_integration
python -m unittest -v network.tests.test_agent_lineage \
  network.tests.test_branch_help
```

GitHub Actions run:
https://github.com/huntingthereferent/autobots-assemble/actions/runs/38840249673

- B2 + B3: **22/22** tests passed.
- Preexisting lineage and branch-help: **19/19** tests passed.
- These B3 tests use `ProcessWorkstation`, a real source-pinned finite
  correspondence worker edition, `HandoffRuntime`, `RuntimeJournal`,
  `controls.run_job`, and `branch_help.verify_return` on an ephemeral CI
  environment. No personal workstation or external equipment was touched.
- **The initial branch observation is a synthetic fixture.** The worker
  execution and source-native verification are genuine within that fixture,
  but this does NOT prove that a general-purpose agent discovers real
  branching opportunities independently.

## Boundaries that remain open

- The feedback event records a verified native *finite helper* return, NOT a
  new independently verified branch, relation collision, or downstream CP PASS.
- A separate domain-native provider must examine returned evidence and decide
  what (if anything) becomes the next admissible movement. No generic
  correspondence-to-game proof is inferred.
- Invocation is explicit; a running autonomous model-backed builder and an
  always-on scheduler are not installed.
- The W13 native game builder remains on its separate feature branch, with
  no claim of independent full W13 browser witness or finished game.
- Supporting concurrent process calls safely will require atomic admission/
  journal locking; idempotence across sequential calls is tested, not
  unrestricted parallel scheduling.

## Next movement

Allow the workstation's *next pass* to consume this verified return as a
source-backed observation only through a registered domain-native
`derive_next_relation` callback. Add failure, duplicate, counterexample, and
cross-domain refusal tests. The callback must never promote output similarity
to a valid two-lane connection without separate witness.
