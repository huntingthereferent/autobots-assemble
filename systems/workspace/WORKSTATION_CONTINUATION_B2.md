# Workstation continuation B2 — journal-backed movement

**Status:** source integration and targeted CI candidate on a review branch. This
is the workstation **as a continuation harness**, not a second scheduler and
not an assertion that general-purpose autonomous coding bots are running.

## Current movement

The existing `RuntimeJournal` owns the events; `HandoffRuntime` owns the
handoffs. No private competing persistence format or modifications to W12/W13
game rules were introduced.

1. Explicitly seed independently scoped lanes, for example A and B.
2. Append a source-referenced `WORKSTATION_MOVEMENT_OBSERVED` record on one
   of those lanes. Intake records an **unverified observation claim** only.
3. On an invoked `tick()`, an installed *domain-native*
   `verify_observation` callback must independently recheck every used
   observation. For two-lane relations, a separate `verify_connection`
   callback must authenticate the proposed join. Matching strings are NOT
   enough to connect.
4. The deterministic policy may propose a branch or connection. If there is
   no registered capable edition, the same journal records
   `WORKSTATION_HELP_OPEN`, with no new agent.
5. A proposal with a declared worker edition creates a new, recoverable
   **READY coordination lane**, with its parent(s), source observation IDs,
   and requested worker capability. That is **NOT a native worker admission
   or execution**. This small unit is what can move through the harness.
6. For a derived single-parent lane bound to an existing domain checkpoint,
   `admit_native_help(..., allow_native_admission=True)` calls the EXISTING
   `branch_help.open_and_staff_known` route. Its native verifier/controls
   still own source copying, job admission, execution, and return verification.
   If no capability adapter is installed, it stays `OPEN_UNSTAFFED`.

The journal is recovered from disk on every invoked pass. Identical intake
records, already-born proposals, source-native admissions, and retransmissions
do not create duplicate children. Existing parent lanes are never marked
COMPLETE or modified merely because a child/connection is opened.

## Example adapter shape

```python
from systems.workspace.workstation_harness import WorkstationContinuationHarness

# These callbacks MUST come from an independently implemented native domain
# verifier. A permissive lambda is NOT a production witness.
h = WorkstationContinuationHarness(
    data_dir="runtime/data",
    verify_observation=native_observation_verifier,
    verify_connection=native_cross_lane_join_verifier,
    worker_editions={"finite-required-edge-prefilter": "declared-source-edition"},
)
h.seed_lane("A", "independent starting work A")
h.seed_lane("B", "independent starting work B")
# A trusted producer may supply a native witness reference for later replay.
h.observe(lane_id="A", kind="BRANCH", relation="new observed direction",
          witness_ref="actual-native-witness-ref",
          capability="finite-required-edge-prefilter")
snapshot = h.inspect()  # read-only
movement = h.tick()      # explicit single continuation pass, no code execution
```

No native callback, native source locator, external model credentials, or
unrestricted worker is silently invented by this code. Worker edition labels
are candidate routing data; an actual source-owned admission still has to
happen through `branch_help` and native controls.

## Verified and unverified boundaries

- **Locally reproducible in CI:** shared `RuntimeJournal` projection,
  persisted branch/connection lane provenance, separate join witness gate,
  replay/duplicate resistance, unstaffed opening, and refusal of unsupported
  native game-builder capability.
- **Source-owned CP admission path:** the integration test creates a real
  private finite-worker edition, then uses `admit_native_help` to request
  native admission. The native job remains `READY`, not executed.
- **Not implemented:** automatically launching a coding model, autonomously
  editing the game, detecting actual A/B branch opportunities from arbitrary
  experience, proving general cross-system collisions, real parallel
  scheduling, or always-on monitoring without an invoked pass.
- **Important:** a test's synthetic witness callback verifies the adapter's
  guard behavior only. It does not substantiate an independent scientific,
  mathematical, or game witness.

## Regression commands

```bash
python -m pip install 'cryptography>=45,<47'
python -m unittest -v network.tests.test_workstation_harness
python -m unittest -v network.tests.test_agent_lineage network.tests.test_branch_help
```

CI: `.github/workflows/workstation-continuation-b2.yml`.

## Next single movement

Connect the actual game W13 native verifier (and later a genuine game-building
worker) as an observation provider and a capability adapter. Then test
`observe -> tick -> native admission -> execute using existing exact-ID controls
-> reverify -> next observed movement`, without making source-label similarity
or simulated evidence stand in for a real witness. Workstation continuation
should remain domain-agnostic; game-specific source and proof stay in game.
