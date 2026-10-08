# Online branch → live Continuity connection audit (2026-10-08)

## Verified before this patch

- GitHub `main` at `ae0b178` and the separate device worktree
  `C:\\Users\\teepa\\continuity-live` match.
- Desktop Commander has an online authorized Windows device.
- The newer local process uses `127.0.0.1:18540` and a **separate** append-only
  runtime journal at `C:\\Users\\teepa\\continuity-live-state`.
- `POST /api/ohayo` works and is idempotent. It reported 0 agents and
  0 admitted local handoffs at that point.
- The old `continuity-sync` checkout at `f6b9955` has local changes.
  Older processes on ports 8040 and 8041 are separate state and must not
  be silently overwritten or merged.

## Connection found missing

`TASKS.md` has existing active `MOVE` records, but the live runtime only
sees already-admitted local handoffs. Therefore Ohayo's local zero-task
report did **not** mean the repository had no active work.

The old portal Ohayo button also called the read-only GET rather than
the explicit report-or-seed POST. On-page activation could not seed an agent.

## Added connection

`runtime/repository_tasks.py` is an opt-in, source-linked adapter
from the active part of `TASKS.md` to the existing durable handoff carrier.
Frozen, pinned, unresolved historical and static evidence rows are excluded.
Every admitted handoff retains its source row, source link, recorded state
and next movement, with deterministic replay-safe identity.

`EcosystemService(repository_work_file=...)` and
`CONTINUITY_REPO_WORK_FILE` make the source available to Ohayo.
The activated POST admits source-backed work **only if no agent lineage
exists**, then seeds at most one task agent. The passive GET remains read-only.
The portal button now uses POST, while initial load remains GET.

`GET /api/connections` exposes observed registrations and missing
connections without mislabeling repository code as a running system.

## Still not connected by this patch

- An independently evidenced mathematical A/B evaluator, source research
  actor and closure-admission verifier; the current agent remains READY
  without an evaluator.
- A continuously scheduled agent worker. The HTTP process serves requests
  but does not autonomously run an unevidenced evaluator.
- Durable external Online School and Factory source state to the running
  service: adapters exist, but are not registered without native input
  providers. Examples are not production source evidence.
- A GitHub-to-device deployment scheduler. Fetching/starting the latest
  checkout was manual for this audit; a pushed commit does not hot-swap
  the already-running Python process.
- Automatic merging of older local service journals (8040 / 8041) into
  the isolated newer runtime; no provenance or owner mapping was supplied
  that would justify combining them.

## Verification contract

The focused test suite checks pure source parsing, source admission,
explicit Ohayo seed, GET non-mutation, restart idempotency, and separation
of pinned/frozen work. Verify the live `/api/connections` output and then
call `POST /api/ohayo` on the device after deployment.

## Live device verification after deployment

Updated worktree: `C:\\Users\\teepa\\continuity-live` at
`150724b`; old `continuity-sync` working copy and its local edits were
left untouched. The new runtime process uses
`127.0.0.1:18540`, with `CONTINUITY_REPO_WORK_FILE` set to the checked-out
`TASKS.md` and a separate durable data directory.

Observed `GET /api/connections`:
- `repository_work.configured=true`, `available=true`, 4 active rows;
- `handoff_runtime.durable=true`;
- `agents.ab_evaluator_connected=false`,
  `closure_admitter_connected=false`,
  `autonomous_worker_running=false`;
- `systems.online_school_registered=false` and
  `factory_registered=false`.

Observed `POST /api/ohayo`:
- first call admitted 4 existing work rows as native handoffs;
- one READY root agent was born for these references;
- second call admitted 0 and spawned 0;
- after process restart, the same 4 tasks and one root were recovered;
- post-restart Ohayo again admitted 0 and spawned 0.

The portal, JS, status, connections, handoffs, notes, tasks, calendar,
attention and read-only Ohayo HTTP routes each responded with HTTP 200.

Focused repository-connection tests: **8/8 passed on the authorized
computer**. JavaScript syntax validation also passed. GitHub Actions
reports the same two preexisting Online School suite failures; no
new errors were reported by the new tests.

This is a **connected source and live task-agent handoff**, not yet an
autonomous evaluator or autonomous worker. The local Python process remains
available while the host runs; automatic restart after computer reboot is
not established by this verification.
