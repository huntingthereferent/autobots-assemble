# B6 — Preserve missing owner–candidate relation as a workstation wall

**Status:** source-bound wall handling on draft PR #25, not an independently
authenticated external owner integration.

## Recovered referent

B2–B4 can retain A/B lanes, execute a real bounded finite-worker subprocess,
independently replay the finite return, and preserve a justified owner-native
observation request. B5 can audit a live CP30 native route task in an
already-running trusted owner process. But these are **not equivalent
relations**. In particular:

- CP30's owner pin and route audit cover that specific route/task, not an
  arbitrary finite prefilter candidate.
- The B5 tests use synthetic CP30 owner objects and a fixture-only
  `verify_candidate_binding` callback. These tests do not independently
  establish a candidate-to-CP30 source relationship.
- No separately enrolled real-world external owner or independently
  authenticated candidate alignment is presently attached to B5. Therefore
  **there is no basis to create a new worker or connecting bot** merely
  from the successful local audit.

## B6 movement

`OwnerCandidateWall` makes the missing relation durable in the *existing*
`RuntimeJournal`:

1. Freshly reverify the B2 original observation, B3 native job, B4 derived
   relation and B5 live CP30 task audit.
2. Verify the exact B5 recorded task's job ID, candidate index, route,
   route fingerprint, native-local evidence digest and finite-source edition.
3. Preserve `WORKSTATION_OWNER_CANDIDATE_BINDING_WALL` with
   `INDEPENDENT_OWNER_CANDIDATE_BINDING_UNAVAILABLE`. This is a reason for
   **not** admitting a new independent relation.
4. Repeat the native checks on replay; do not duplicate the wall.
5. Reject withdrawn owner pins, withdrawn parent witnesses, absent B5 returns,
   or source differences. Leave existing A/B and child lanes unchanged.

The recorded wall is recoverable and actionable when an authorized source
provider becomes available. It is not a permanent rejection of the design.

## Exact unresolved boundary

A genuinely source-owning process must supply owner-held live CP30 objects
**and** an independently supported, exact alignment between the finite
candidate and the selected native task. A local audit, matching word, Python
boolean, fixture label, GitHub link or matching hash alone cannot do this.
Until that source exists, do not claim a complete finite candidate edge,
cross-lane collision, owner identity, executable bot, or W13 game PASS.

## Regression verification

The source-native CP30 reconstruction workflow now includes
`network.tests.test_workstation_owner_source_wall`, exercising real native
local audit logic over controlled fixtures, with explicit negative cases
for revoked ownership, withdrawn B2 witness, missing B5 return, and repeated
recovery without duplicate events. None of these tests enrolls an external
source owner.

No autonomous always-running model-backed worker, cross-lane connection
authority, or concurrent-writer lock is added by B6. The workstation remains
an invocation-driven harness.
