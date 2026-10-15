# One-window CP automation — Complete Stack intake

**Date:** 2026-10-15. **Status:** scoped repository implementation; no native domain-specific CP adapters are implied by publication.

## Referent

Adding NIH's temporal KG challenge to James's existing Complete Stack creates an explicit dependency relation. This **immediately creates a CP frontier**, rather than waiting for humans to handwrite a new task schedule. Each CP declares a work boundary, a native worker role, required preceding CPs, and a proof condition. The next frontier derives from **reverified** native results; it never derives from 100% UI progress, a source checksum, or a finished but negative computation.

This is **checkpoint automation**, not a second execution scheduler and not autonomous general agents. `HandoffRuntime`, `RuntimeJournal`, Process Workstation editions, explicit admission/execution controls, and domain-native verifiers remain the source of truth. A coordinator observes which CP becomes admissible as evidence changes. Its status call does not execute anything.

## Dependency choices

- NIH Phase 1 scoping, ontology mapping, temporal reasoning, and a submission packet can advance independently of the game-engine completion. CP30 can contribute only within its actual finite correspondence/attestation scope; it does not natively build a biomedical ontology.
- Game WORLD/BUILD/WITNESS continue from W12 toward a verified multi-world engine and a source-pinned game worker adapter.
- Phase 2 **prototype work** may branch after Phase 1 temporal reasoning passes.
- Phase 2 **test execution through James's planned complete-stack infrastructure** requires the independently verified Phase 1 packet, a genuinely verified game worker adapter, and the prototype. This is **our architecture's prerequisite**, not an NIH rule.
- An NIH Phase 1 official award is required separately for formal NIH Phase 2 submission eligibility, not for conducting local Phase 2 experiments.

## CP proof admission — fail closed

A checkpoint can count as `WITNESSED` only if the existing workstation reports an actual job as `COMPLETE`, with `source_state=MATCHES_ADMISSION`, `verification=natively-reverified`, no missing witnesses/dependencies, and the immutable original native handoff declares an exact checkpoint contract and a distinct `cp-checker:<CP-ID>` verifier. That exact verifier must validate a `PASS` for the same checkpoint and declared worker role. The planner refuses any claimed higher CP whose preceding CPs are not witnessed, even if a worker returns a PASS-looking payload.

**Important:** Current CP30 and W12 modules do not implement these new named CP-specific native adapters. The original historical passes are carried as evidence, NOT promoted to fresh CP proofs. `ADMISSIBLE` means ready to formulate/admit a bounded job, not already working or complete. No live jobs are present in the example.

## Install into the *existing* repository

Use the files already installed in this repository. Do not replace `workstation.py`, `monitor.py`, `controls.py`, `runtime/engine.py`, `runtime/journal.py` or native domain verifiers:

```
systems/workspace/coordinator_window.py      # existing V1 coordinator overlay
systems/workspace/cp_motion.py                # new checkpoint frontiers
network/tests/test_coordinator_window.py      # original V1 regression
network/tests/test_cp_motion.py               # new negative controls
```

Run from the repository root:

```bash
python -m unittest -v network.tests.test_coordinator_window network.tests.test_cp_motion
python -m systems.workspace.cp_motion --data-dir runtime/data admit-research \
   --nih-contract-zip /path/to/nih_all_phases_harness.zip \
   --game-w12-zip /path/to/game_W12_receipt_candidate.zip \
   --correspondence-index /path/to/correspondence_CP30_index.json
python -m systems.workspace.cp_motion --data-dir runtime/data handoff --markdown \
   --artifact-dir /path/to/research-evidence
```

The `admit-research` step is idempotent and makes append-only planned checkpoint slots in the **existing coordinator index**. It pins the optional original archive identities. It starts zero workers and admits zero native jobs. The `handoff` step reads the existing workstation snapshot and shows the full CP graph, current frontier, and every registered worker slot in one report. `--reverify` runs the already existing per-job read-only native recheck for exactly linked `COMPLETE` jobs; no READY job is executed by it. To execute a native job, use the original workstation's explicit exact-job-ID admission/execution control, or the coordinator's existing `run-linked` control with exact confirmation. CP progression is then recalculated on the next status/handoff invocation.

This implementation is event-driven **when invoked**, not an always-running watcher. To have new CPs start automatically without an operator handoff, a future explicit admission policy, authenticated executor connection, and tested concurrency/recovery semantics would be needed. No such capability is claimed here.

## Status examples

| Situation | CP effect |
|---|---|
| Challenge is admitted, no CP-native jobs | `NIH-P1-SCOPE` and `GAME-W13-WORLDS` become `ADMISSIBLE` |
| A properly reverified scoped Phase 1 observation passes | Downstream ontology CP becomes `ADMISSIBLE` |
| Phase 1 packet verified, game engine unfinished | NIH Phase 2 testing remains `BLOCKED` |
| Game engine verified and Phase 2 prototype witnessed | NIH Phase 2 test CP can become `ADMISSIBLE` |
| Historical CP30 generic job returns `COMPLETE` | Does **not** witness biomedical CP |
| A future CP tries to skip its parents | Refused; existing parents remain unchanged |
| NIH Phase 1 winner claimed using local data | Not accepted; must be verified via external NIH authority |

The canonical `Complete Stack` and original A/B language investigation retain their own scope. The CP graph is one engineering application over that continuing relation, not its definition.

## Bind an admissible checkpoint to an admitted native job

Once the source-owned native adapter has **already admitted** an exact job in
`runtime/data/runtime.jsonl`, bind that job to the corresponding planned CP slot:

```bash
python -m systems.workspace.coordinator_window --data-dir runtime/data bind-job \
  --lane nih --slot cp-nih-p1-scope --job-id ACTUAL_JOB_ID \
  --worker-id ACTUAL_WORKER_ID --version ACTUAL_EDITION_ID
```

The binding is a new hash-linked event; the original planned event is retained
unchanged. The CLI refuses a nonexistent native job, edition mismatch,
non-planned slot, or a second binding. This prevents a permanently planned CP
slot from surviving after an exact worker has been assigned. A binding itself
is **not** execution or completion. An exact CP-native re-verification, and
witnessed predecessor checkpoints, are still required to advance the CP frontier.

A coordinator only admits CP proof from native jobs explicitly bound to that
coordinator window. Other jobs in the same workstation cannot advance it.

## Current evidence

- Focused unit scope: **42/42 locally passed** before repository installation;
  historical CP30 and game native suites not included in that count.
- The optional archives remain external/historical artifacts; this change does
  not publish ZIP payloads, patient information or simulated clinical claims.
- For live workstation status, run against the correct `runtime/data` folder on
  an authorized machine. No private workstation state is stored in GitHub.