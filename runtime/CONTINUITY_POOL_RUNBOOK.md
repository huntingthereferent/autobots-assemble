# Original Continuity agent queue — live integration

The original 2026-10-08 tasks are **Finish Continuity site**, **Find things
to swallow**, and **Visual provenance min/max**. Their assignee is
`continuity-agent-pool`. Their native seed definitions live at
`systems/personal_operations/task_seeds/continuity_agent_tasks.json`.

This queue is **not** the four `TASKS.md` repository work entries previously
reported by James's Ohayo activation. Both remain preserved independently.

At startup, with `CONTINUITY_AGENT_POOL=1` and loopback `HOST=127.0.0.1`,
the HTTP service now loads the exact original task seeds, idempotently admits
their Personal Operations handoffs into the durable shared runtime, seeds
one task agent whose owner is `continuity-agent-pool`, and runs the **already
implemented** recursive A/B loop over the three native entry-point contracts.

The resulting `CONTINUITY_POOL_AB` event contains real source paths and
SHA-256 witnesses, while the tasks and agent stay READY. Source-relation
MOVEs do **not** mean the site, expansion research, or visual min/max tasks
are finished. No model-backed software worker or autonomous code editing
is installed by this connection; the native A/B worker can compare grounded
source relations but cannot invent implementation or render/inspect a
desktop/mobile browser without a separate, witnessed tool actor.

The original E: task journal may be copied (after a backup) to the live data
directory as `personal_operations.jsonl` to preserve original task IDs.
Never merge or overwrite the old E: working tree. Source and state are
distinct; the original task journal remains evidence.

## Local read-only checks

- `GET http://127.0.0.1:18540/api/agent-pool` — original task IDs, native
  A/B observation, agent readiness, honest worker status.
- `GET http://127.0.0.1:18540/api/monitor?actor=continuity-agent-pool` —
  three native task handoffs and the pool's one root agent.
- `GET http://127.0.0.1:18540/api/monitor?actor=james` —
  separate repository-work lane.
- `http://127.0.0.1:18540/monitor.html` defaults to the original pool;
  `?actor=james` preserves the other scope.

Reboots and repeated pool initialization are idempotent. `READY` means the
system can receive more native movement, not that an always-on model actor
is running. Never claim autonomous website completion without actual
implementation, tests, visual witnesses and user-visible deployment.
