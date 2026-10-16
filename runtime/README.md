# Handoff Runtime

The runtime makes the repository's existing `core.handoff` contract executable.

It is deliberately small.

```text
world / human expression
        ↓
translation
        ↓
HANDOFF
        ↓
human / agent / program / machine / simulator
        ↓
result + evidence
        ↓
append-only event
        ↓
derived state
        ↓
next eligible handoff
```

[Continuous Handoff — observational determination](../language/handoff/CONTINUOUS_HANDOFF.md) extends the **explanation** of existing handoffs and preserved provenance; its [read-only example](examples/continuous_handoff/README.md) does not replace or mutate this runtime.

## Boundary

The runtime is **not the language referent**.

The [language referent](../LANGUAGE_REFERENT.md), historically called A/B, is the continuing inquiry, not an operation implemented by this runtime. The [evidence contract](../LANGUAGE_REFERENT_CONTRACT.md) governs specific bounded software movements. Mathematics is a human formal language within the same investigation.

The runtime is an implementation layer that carries bounded work between unlike actors while preserving:

- current referent;
- required relation;
- inputs;
- expected output;
- required witnesses;
- admissible evidence;
- dependencies;
- boundaries;
- provenance.

## Optional Correspondence Worker computation

The [Process Workstation adapter](../systems/workspace/CORRESPONDENCE_HANDOFF.md) uses this existing handoff runtime to carry **one explicit Finite Correspondence Process prefilter job**, with the selected worker edition's source fingerprint, local child-process execution, independent native replay, and restart re-verification. Neither the runtime's scheduler nor its event vocabulary is duplicated. This is a bounded computation, not an AI agent, CP-0030 owner identity, or a physical factory action.

## Durable vs live

The repository and runtime have different jobs.

```text
REPOSITORY
contracts / provenance / evidence / implementations / tests
        ↓
RUNTIME
live handoffs / events / current state / routing
        ↓
ADAPTERS
human / AI / software / machine / simulator
        ↓
PROJECTIONS
task / job / command / dashboard / language
```

A view can disappear and be regenerated. The handoff specification and append-only event history remain sufficient to recover why the current state exists.

## Common carrier

A handoff is not synonymous with a task.

```text
handoff → human projection      → task
handoff → program projection    → job
handoff → machine projection    → command
handoff → simulator projection  → simulated event
```

The receiving implementation may differ. The handoff/evidence boundary does not silently change.

## Event sourcing

`EventStore` preserves append-only events.

`HandoffRuntime.state(...)` derives current state from those events plus dependency state.

Supported live states:

- `WAITING`
- `READY`
- `ACTIVE`
- `COMPLETE`
- `PARTIAL`
- `BLOCKED`
- `FAILED`
- `UNKNOWN`

A handoff cannot become `COMPLETE` unless every required witness is returned using an admitted evidence kind.

## Files

- `handoff.py` — carrier, evidence, state, execution result, simulated actor
- `engine.py` — append-only event store and runtime
- `projections.py` — task/job/command projections
- `activation.py` — explicit actor+surface activation routes over existing handoff state
- `orchestrator.py` — generic system registration, routing, automatic execution, and result reconciliation
- `journal.py` — durable handoff-spec + event journal for restart recovery
- `trace.py` — append-only relational touch trail for external traversal; stores locators/relations/ancestry, not copied internet state
- `external_feed.py` — ephemeral read-through aggregation of live public feeds for frontage testing; external items are normalized in memory and not persisted
- `service.py` — persistent application service over existing system/runtime contracts
- `http_server.py` + `http/` — bounded HTTP/HTML entrance
- `handoff.schema.json` — external serialized handoff shape
- `examples/cross_layer.py` — same carrier across James/school/software/factory
- `examples/tiny_factory.py` — sequential simulated production run
- `examples/ohayo.py` — James `ohayo` activation over a mixed handoff set
- `examples/full_ecosystem.py` — Personal Operations + Online School + Factory under one orchestrator
- `examples/restart_recovery.py` — crash after runtime result, recover without duplicate execution

The examples are witnesses for the runtime shape, not claims about physical production.


## Swallow-first boundary adapter (opt-in)

`runtime/swallow_first.py` connects an explicit outward source search and
external referent-evidence comparison to the **existing handoff event stream**.
When supplied to `Orchestrator(..., boundary_resolver=...)`, UNKNOWN/BLOCKED
results are sent to the swallow-first boundary before origin reconciliation.

```text
UNKNOWN / BLOCKED
  -> registered swallow_agent searches external native sources
  -> bounded native witness locators (the source stays external)
  -> registered referent-evidence admission compares against exact wall
  -> evidence-valid worker COMPLETE -> atomic RESULT on SAME handoff -> MOVE
  -> else remaining reground agents -> SAME wall + appended search evidence
  -> explicit ready_for_james guard, never automatic human escalation
```

The journal preserves SWALLOW_ATTEMPT, REFERENCE_ADMITTED/REJECTED,
REGROUND_ATTEMPT and SWALLOW_UNRESOLVED events alongside the original RESULT.
A failed candidate never replaces the original wall. An empty/erroring search is
not proof of outward traversal. A saved attempt/admission is replayed on a
restart rather than silently repeated.

**Boundary:** This repository does not presently contain the named `ABLoop` or
`JamesABTaskBridge` from the separate work report. This adapter does **not**
implement referent comparison, external browsing, reference research, or automatic
James task escalation. Those are caller-supplied actors. Any future bridge must
check `ready_for_james(handoff_id)` and fail closed when no outward search is
recorded. Configurations that do not register this resolver retain existing
orchestrator behavior; they must not be described as swallow-first.

## Multi-system orchestration

`Orchestrator` sits above the shared runtime without owning any system's local state.

Each registered system exposes a small boundary:

```text
emit_ready()
→ zero or more SystemEmission records

reconcile(emission, returned_handoff_state)
→ mutate/reconcile only that system's local state
```

The orchestrator:

1. asks each system what is ready;
2. submits new handoffs to the shared runtime;
3. automatically executes handoffs when a registered executable actor exists;
4. leaves human/unconnected handoffs READY;
5. routes returned results back to the system that emitted them.

This means an automated factory can continue moving while human work remains visible in projections such as `ohayo`.

The demonstrated full ecosystem currently contains:

```text
Personal Operations
Online School
Factory System
        ↓
shared Orchestrator + HandoffRuntime
        ↓
human actors / simulated actors
        ↓
activation projections
```

The systems retain different local schemas. The shared boundary is the handoff.

This follows the repository provenance invariant: **local state, continuous provenance**. A handoff carries a traceable edge between systems; it does not require either system to surrender its local model. Returned results preserve enough ancestry for the receiving system to reconcile them against its own current state.


## Durable restart recovery

`RuntimeJournal` persists both:

- the immutable handoff specification;
- append-only runtime events.

A submission writes the specification together with its `CREATED` event. Recovery therefore restores **what the handoff means**, not merely its status history.

On restart:

```text
system-local log/state
+
runtime handoff specs/events
        ↓
reconstruct systems + HandoffRuntime
        ↓
systems re-emit same pending handoff IDs
        ↓
Orchestrator re-binds origin routing
        ↓
READY work remains READY
terminal runtime results reconcile without re-execution
        ↓
normal movement continues
```

The crash-recovery witness specifically covers a process dying after a factory result is durably `COMPLETE` but before the factory records reconciliation. The recovered orchestrator applies the existing result and does not execute that operation twice.


## HTTP entrance

`python -m runtime.http_server` starts the shared local entrance on:

`http://127.0.0.1:8040`

Environment:
- `HOST` — bind host, default `127.0.0.1`;
- `PORT` — bind port, default `8040`;
- `ECOSYSTEM_DATA_DIR` — private durable state directory, default `runtime/data/`.

Current API:

```text
GET  /api/research-board?checkpoint=<optional registered checkpoint> (read-only)
GET  /api/status
GET  /api/notes
POST /api/notes

GET  /api/plans
POST /api/plans

GET  /api/tasks
POST /api/tasks
POST /api/tasks/{task_id}/admit

GET  /api/reminders
POST /api/reminders
POST /api/reminders/{reminder_id}/ack

GET  /api/calendar
POST /api/calendar

GET  /api/traces?session_id=<optional session>
POST /api/traces
GET  /api/traces/{trace_id}/ancestry

GET  /api/live-feed?force=<optional 0|1>

GET  /api/attention?actor=james&at=<optional ISO datetime>

GET  /api/handoffs?actor=&status=
POST /api/handoffs/{handoff_id}/result

GET  /api/activate?surface=ohayo&actor=james
POST /api/ohayo (loopback-only; actor_id=james in JSON body)
GET  /api/agents?root=<lineage_id> (loopback-only)
POST /api/agents/activate (loopback-only)
POST /api/agents/<agent_id>/result (loopback-only)
```

The HTTP layer does not create a parallel model. It calls the existing Personal Operations, Calendar, Day-to-Day, activation, orchestrator, runtime, evidence, and recovery contracts.

The included dashboard exposes current Day-to-Day attention (live work, Calendar, explicit reminders), Notes, Plans, Tasks, and Live Handoffs while preserving their boundaries. The attention view refreshes quietly and `ohayo` enters that same state explicitly rather than creating a second model.

## Ohayo report-or-seed activation

The everyday Ohayo report now includes `agents`, `agent_summary`,
`agent_activity`, `agent_roots`, and `agent_note` alongside James's
admitted tasks, calendar, and reminders. `GET /api/activate` is still
read-only: it does not create work.

The explicit `POST /api/ohayo` checks current persisted lineages first. If
there is at least one existing James lineage, it only reports, even if all
agents have completed. If none exists but admitted handoffs assigned to James
are waiting, it creates exactly one READY root agent and records their native
handoff IDs/provenance as input. Otherwise it reports idle. Repeated calls and
service restarts do not create duplicates. Any configured referent evaluator can
advance this new agent; no evaluator means READY and no inferred task result.

This activation is not a background daemon or independently verified source
search. It does not reassign existing human tasks to an autonomous actor, or
convert unadmitted notes/plans into work. Loopback HTTP is not multi-user
authentication.

## Repository active-work → admitted handoffs (opt-in)

The project records already-active work in `TASKS.md`. The optional
`runtime/repository_tasks.py` adapter reads **only active `MOVE` rows**
in `## Active ALL WORK`, excluding pinned and frozen/evidence work.
This is a concrete source connection, not a general interpretation engine.

To enable it on the local HTTP runtime, set
`CONTINUITY_REPO_WORK_FILE` to the absolute path of your checked-out
`TASKS.md` before starting the process. Without that setting the source
remains disconnected and the ordinary local tasks continue to work.

`GET /api/connections` reports whether the source is configured and
available, active row counts, live handoff counts, and which evaluator,
closure verifier, Online School and Factory bindings are actually registered.
`GET /api/activate?surface=ohayo&actor=james` reports without changes.

On the explicit `POST /api/ohayo` activation, if James has no agent lineage:
the adapter admits each eligible recorded work row as a native handoff with
its original title, link, next movement and source provenance. The existing
Ohayo rule then seeds exactly **one** agent from those admitted handoffs.
Repeat requests and restarts preserve identity and do not duplicate work.

This admission is not execution, not a verified ARC solve, and not evidence
that every repository record belongs to one actor. This configured
repository-wide work lane is explicitly routed to James for the Ohayo
entry. Frozen, pinned and historical records do not become obligations.
New source rows appearing after the agent exists remain visible in the
read-only source count but are not silently admitted during agent reporting.

The front-page Ohayo button sends POST. Page load and passive refresh use
GET. The source code/runtime still needs to be updated on the actual machine
and the HTTP process restarted after GitHub changes; a GitHub commit alone
does not hot-reload a running Python process.

## Live read-only agent monitor

Open `http://127.0.0.1:<PORT>/monitor.html` from the authorized computer,
or use **Monitor** in the site navigation. This separate compact surface polls
`GET /api/monitor?actor=james` every 10 seconds **while the page is open**.
It does not call POST, trigger Ohayo, create tasks, spawn agents or interpret
a READY handoff as active execution.

The view distinguishes:
- task handoffs (READY/ACTIVE/COMPLETE/blocked etc.) and their native source;
- agent generations, birth reasons, loop OPEN/CLOSED and last saved event;
- recent append-only events with source witness references and timestamps;
- actual registered connections: repository work, durable journal, referent evaluator,
  closure verifier, autonomous worker, Online School and Factory;
- responding service versus failure to poll; a missed poll shows an offline
  warning and the last cached snapshot rather than silently displaying old data.

`GET /api/monitor` and monitor assets are loopback-only. This is deliberate:
the data is not exposed as a public unauthenticated dashboard. On a phone,
ask ChatGPT for the monitor report through its authorized Desktop Commander
connection rather than publishing the laptop's local port.

Status `reported_active` means a saved STARTED event, **not** independently
proven ongoing CPU activity; no heartbeat exists for the referent evaluator.
This is observation while connected, not automatic push notifications or
an always-on remote outage monitor. The monitor cannot keep the computer
awake or restart a stopped server.

## Research question board

The Research Questions link opens `/research-board.html`. Its read-only
`GET /api/research-board` response projects the checkpoint named in
`research/questions/index.json`. The returned snapshot is loaded from an
explicitly registered local file, never an arbitrary query-supplied path.

The original research questions are frozen in a separate checkpoint JSON.
A reconciliation pass must create a **new** checkpoint and advance the index;
it must not overwrite a frozen file, claim an answer without evidence and
scope, or turn an UNKNOWN into inferred equivalence. Checkpoints are
Git-versioned research outputs, not task state or a new evaluator.

[Record contract](../research/questions/README.md).

## Separate read-only workstation viewer

The reusable [Process Workstation](../systems/workspace/README.md) has a local viewer at `http://127.0.0.1:8051/workstation.html`. Run `python -m systems.workspace.view_server --data-dir runtime/data --port 8051` to start it explicitly. This small **HTTP reader**, not another execution runtime, reloads the same `RuntimeJournal` on each `GET /api/workstation`, displays source editions, admitted jobs, historical results and evidence, and exposes **no** job-execution or task-admission endpoint. It does not run automatically with `runtime.http_server` or seed any example tasks. Both services must use the same `ECOSYSTEM_DATA_DIR` if that default is overridden. This viewer is strictly local-only, not an authentication system.
