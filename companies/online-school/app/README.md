# Online School HTTP Task Monitor

A deliberately small first online delivery surface for **Online School**.

It is a local HTTP website/API whose job is to carry the entire school schedule as tasks without forcing the schedule into a narrow UI.

## What it does

- loads the company schedule template;
- generates recurring school tasks for any weekday;
- preserves individual and shared task scopes;
- preserves planned minutes;
- applies dated weekly themes when available;
- allows arbitrary one-off tasks;
- marks tasks complete through the website;
- persists task state locally;
- exposes the same task state over HTTP/JSON.

## Run

```bash
cd companies/online-school/app
python server.py
```

Open:

```text
http://127.0.0.1:8030
```

Set `HOST` or `PORT` environment variables when needed.

## HTTP interface

```text
GET    /api/state
GET    /api/today?date=YYYY-MM-DD
GET    /api/tasks?date=&status=&learner=&kind=&scope=
POST   /api/generate
POST   /api/tasks
PATCH  /api/tasks/{id}
DELETE /api/tasks/{id}
```

Example generation request:

```json
{
  "start": "2026-10-05",
  "end": "2026-10-09"
}
```

Task records are intentionally extensible:

```json
{
  "date": "2026-10-05",
  "title": "mathematics",
  "learner_ids": ["track_a", "track_b"],
  "planned_minutes": 60,
  "status": "todo",
  "notes": "Whole, half, and quarter measurements",
  "meta": {
    "theme": "Recipes, kitchen safety, and measuring tools",
    "math_mode": "direct_lesson"
  }
}
```

Additional task kinds, categories, learners, notes, and `meta` values can be added without changing the outer task contract.

## Local state / privacy

Runtime state is written to:

`app/data/state.json`

That file is intentionally ignored by Git. The committed defaults use anonymous track IDs. Local display names can be changed in the runtime state without publishing them to the repository.

## Boundary

This is a task monitor / HTTP interface.

It is not yet:
- an LMS;
- a grading platform;
- a public enrollment system;
- an accredited school portal;
- a hosted multi-tenant service.

Those relations can open later if the company actually requires them.

## Shared handoff boundary

Online School keeps its own task schema.

`handoff_adapter.py` translates a school task into the shared runtime carrier without replacing the school's local model.

The current schedule explicitly marks the existing guided-reading block with `responsible_actor: james`. That means the generated school task can become a handoff assigned to James while learner identities remain anonymized in the public company layer.

A returned handoff state is translated back into a **school task patch**. The school remains responsible for applying/persisting its local state.

Task completion does not automatically establish learner mastery.
