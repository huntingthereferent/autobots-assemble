# Online School Local Operating Surface

The first local HTTP website/API for **Online School**.

It began as a deliberately small task monitor. The home surface is now a learner-first education workspace around the shared kernel: current learner relations, observation/regrounding, today's educational movement, curriculum obligations, artifacts, and the underlying operating schedule remain distinct but connected. The shared education kernel still lives in `systems/education/`; this company consumes it rather than redefining it.

## What it does

- enters through a learner rather than through a gradebook or schedule;
- reads current learner relations from the shared Education Kernel;
- records observations and immediately regrounds the current learner relation while preserving prior relations as natural provenance;
- shows Missouri-aligned grade context as obligations without treating grade as learner state;
- projects today's individual and shared educational movement separately;
- connects learner context into Worksheet Studio and preserves worksheet provenance;
- keeps the full recurring schedule available as an operating layer rather than the learner path;
- preserves planned minutes, dated themes, arbitrary one-off activities, and local completion state;
- exposes the same school/kernel projection over HTTP/JSON.

## Run

```bash
cd companies/online-school/app
python server.py
```

Open:

```text
http://127.0.0.1:8030
```

Set `HOST` or `PORT` environment variables when needed. Set `ONLINE_SCHOOL_DATA_DIR` to run an isolated/private school state directory without touching the default `app/data/` store.

## HTTP interface

```text
GET    /api/state
GET    /api/school?date=YYYY-MM-DD
POST   /api/observations
GET    /api/today?date=YYYY-MM-DD
GET    /api/tasks?date=&status=&learner=&kind=&scope=
POST   /api/generate
POST   /api/tasks
PATCH  /api/tasks/{id}
DELETE /api/tasks/{id}

GET    /api/worksheets
GET    /api/worksheets/{id}
POST   /api/worksheets/generate
POST   /api/worksheets
DELETE /api/worksheets/{id}
```

## Visual provenance

This app has separate visual provenance for separate visual layers.

- `index.html` declares `education_workspace_v1`: learner first, current evidenced relation before obligations, schedule subordinate to educational state, no gradebook/gamification assumptions. Its local binding is `visual-provenance/education-workspace.json`.
- `worksheet.html` declares `notegpt_math_generator_v1`: the approved worksheet-generation visual witness derived from the useful grammar of the NoteGPT reference without copying its branding, proprietary assets, wording, or exact page composition. The original Worksheet Studio binding remains in `visual-provenance.json`.

The two surfaces are connected but intentionally do not share one visual template because they perform different relations.

## Worksheet Studio

`/worksheet.html` is the native printable worksheet authoring surface. It is not a separate product: saved worksheets live in Online School state and remain available to later school/runtime layers.

Current generation modes:

- math worksheet generation from a natural-language request, with grade/range inference, deterministic variants, worked answer explanations, and addition/subtraction/multiplication/division, fractions, decimals, percent, algebra, geometry, time, money, measurement, place value, comparison, patterns, and word problems;
- spelling with support / standard / challenge movements;
- vocabulary from term-definition pairs;
- reading + thinking from a supplied source passage;
- handwriting / copywork;
- fully custom question + answer rows.

Every generated question remains editable. The studio supports learner/subject/knowledge-goal context, answer keys, response-space editing, 1–3 column layouts, US Letter/A4 paper, saved worksheet reuse, and clean browser Print/PDF output. A seed + variant label make parallel or repeatable versions explicit rather than silently regenerating different work.

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

This is a local school operating / artifact interface.

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

The generic ecosystem orchestrator can register Online School through `systems.bindings.online_school_binding`. The binding consumes this app's own task provider / handoff adapter / patch path; the orchestrator does not absorb the school task schema.
