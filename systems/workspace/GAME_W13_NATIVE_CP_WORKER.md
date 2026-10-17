# GAME-W13-WORLDS — source-owned finite CP-native worker

## Current referent

Continue the independently witnessed **WORLD W13 two-room playable game** into one actual Process Workstation job, without rewriting the original W12 source, changing the existing checkpoint graph, using CI as source-owner authorization, or inventing a new scheduler.

This movement adds the missing **CP-specific native worker adapter** for `GAME-W13-WORLDS`. The worker is bounded to the exact WORLD W13 Movement 01 path, not a general game generator or claim that all 2–4-world configurations have been witnessed.

## Exact contract and implementation

The existing CP policy requires:
- `checkpoint_contract = GAME-W13-WORLDS`
- `checkpoint_worker_role = game-build`
- `native_evidence_verifier = cp-checker:GAME-W13-WORLDS`
- a source-pinned existing workstation edition, an **immutable handoff** with the exact verifier/role, an actual `COMPLETE` native computation, and successful **fresh read-only native re-verification**.

The new source file `game_w13_worker_source/game_worlds_worker.py` is a finite **standalone copied subprocess**. Its only admissible request is `network/tests/fixtures/game_w13_native_cp_example.json`: two named WORLD rooms and `right, interact, advance, right, interact` under the byte-preserved original W12 SHA-256. It constructs a per-world receipt, before/action/after/verdict states, and the one explicit crossing. Its output and PID are candidate evidence, **not accepted as self-proof**.

`game_w13_native.py` is the **host** CP verifier. It checks the strict exact request and independently replays the copied source's receipt using the separately authored W13 WITNESS oracle and **original pinned W12 native transitions**, not BUILD's W13 receipt verifier or child-worker's claim.

`game_w13_native_bridge.py` uses the **existing** `ProcessWorkstation`, `HandoffRuntime`, `RuntimeJournal` and `EvidenceRecord`:
- `copy_game_source` requires explicit copy authorization and records source edition fingerprint.
- `admit` requires an explicit from-actor and produces a source-owned `READY` job and immutable `cp-checker:GAME-W13-WORLDS` handoff.
- `execute` refuses absent explicit authorization; runs the copied bounded local worker only for that job and verifies the output independently before `COMPLETE` is recorded.
- `reverify` checks the exact original source edition, immutable contract, evidence, output and W12 replay without rerunning any subprocess.

`controls.py` now routes `game-worlds-w13` through its **existing** prepare, exact-job-ID execution, observation, and read-only re-verification logic; this is a bounded worker addition, not a replacement of general workstation controls.

## Operator-run local workflow

This requires an operator-controlled checkout, a **private runtime directory outside the source repository**, and a trusted review of copied Python before running. CI examples are ephemeral isolated tests; **no user-owned external worker is admitted or executed by the GitHub PR**.

```bash
# Choose your own separate private runtime data location, exact edition and job ID.
python -m systems.workspace.cp_motion --data-dir /path/to/private-runtime admit-research
python -m systems.workspace.game_w13_native_cli --data-dir /path/to/private-runtime copy \
  --version w13-source-v1 --confirm-copy
python -m systems.workspace.game_w13_native_cli --data-dir /path/to/private-runtime prepare \
  --version w13-source-v1 --inputs-file network/tests/fixtures/game_w13_native_cp_example.json
python -m systems.workspace.game_w13_native_cli --data-dir /path/to/private-runtime admit \
  --version w13-source-v1 --inputs-file network/tests/fixtures/game_w13_native_cp_example.json \
  --job-id game-w13-001 --confirm-admit game-w13-001 --from-actor local-operator
python -m systems.workspace.coordinator_window --data-dir /path/to/private-runtime bind-job \
  --lane game --slot cp-game-w13-worlds --job-id game-w13-001 \
  --worker-id game-worlds-w13 --version w13-source-v1

# Execution remains separate, requiring EXACT confirmed native job ID.
python -m systems.workspace.coordinator_window --data-dir /path/to/private-runtime run-linked \
  --lane game --slot cp-game-w13-worlds --confirm-execute game-w13-001
python -m systems.workspace.cp_motion --data-dir /path/to/private-runtime handoff \
  --markdown --reverify
```

A copied Python source edition **is not OS-sandboxed**. Review the selected source and isolate your machine/environment before operator-authorized native execution.

## Verification and negative controls

`network/tests/test_game_w13_native_cp_worker.py` validates copied-source subprocess execution, independent original W12 replay, malformed source request rejection, forged child receipt rejection, changed source fingerprint failure, exact operator copy and execution confirmation, no result before admission, no CP advance before exact binding and read-only re-verification, idempotent completed job handling, crash/restart journal replay, and a negative fake `PASS` result.

The dedicated Actions workflow runs 21 finite game-native tests plus the original W12, W13 WITNESS and coordinator proof gates. All tests execute in temporary local test directories, not a user-owned Process Workstation.

Only after an explicitly admitted, COMPLETE, source-matching, correctly bound native job is freshly reverified will the **existing** CP planner mark `GAME-W13-WORLDS` as `WITNESSED` and open `GAME-NATIVE-VERIFIER` to future admission. This does **not** complete that next verifier CP, `GAME-WORKER-READY`, NIH Phase 2, deployed-browser origin, or an autonomous self-expanding worker network.

## Boundary for the next movement

The local finite CP adapter gives COORDINATOR a source-backed route to its **first game CP native witness** after explicit operator execution. The next distinct native boundary is `GAME-NATIVE-VERIFIER`, which must consume that exact source-owned W13 job rather than use GitHub browser CI as its parent authority.

**No external owner authenticated, no unattended job scheduled, no workstation journal or user-owned source state created by this repository change.**
