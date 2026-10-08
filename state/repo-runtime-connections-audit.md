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
