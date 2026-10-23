# Calendar

Calendar owns time relations, not work.

It can preserve appointments, deadlines, routines, milestones, birthdays, school windows, and other dated/recurring relations without converting them into tasks.

Day-to-Day consumes Calendar as one input when deciding what deserves a person's attention now.

```text
Calendar = time truth
Day-to-Day = attention projection
Activation = entrance into that projection
```

Calendar does not infer obligations and does not own source-system state.

## Online School weekly planning

Online School may project a bounded one-week itinerary into Calendar after placement or a weekly retest establishes the learner's current position.

```text
placement / retest evidence
→ one school week
→ dated calendar relations
→ day-to-day attention
→ Friday retest
→ next week may be generated
```

Calendar preserves the dated relations only. Education remains the authority for why a movement exists and what evidence changes it. Future school weeks are not materialized before the current week's retest closes.

## Movement anchors

Calendar events may carry a `movement_anchor` from `language/words/movement_anchors.json`.

The anchor describes the social/word movement associated with a time relation, for example `OPEN`, `PING`, `REPLY`, `SILENCE`, or `REOPEN`.

```text
Calendar = when
movement anchor = what kind of social movement is expected/observed
Day-to-Day / pipes = decide whether and how to project it
```

The calendar does not infer that the movement occurred and does not convert an anchor into an obligation. A pipe may use the anchor to simulate or route expected movement while preserving the calendar as time truth.


## Daily ChatGPT correspondence (read-only Calendar REOPEN)

[Daily Correspondence](../../docs/live/daily-correspondence.html) projects one dated, source-pinned handoff prompt from the existing recurring Calendar relation into the workstation. The source adapter is [daily_correspondence.py](daily_correspondence.py) and its independent schedule is [.github/workflows/daily-correspondence.yml](../../.github/workflows/daily-correspondence.yml).

- Calendar owns **when**: daily `REOPEN` is an attention trigger, not permission to start workers.
- Workspace owns **lane return points**: optional private journal may be read only by an authorized local run; the public scheduled renderer deliberately does not have it.
- Research sources own **what is known**: the published historical index is explicitly labeled historical until reverified. Daily differences are differences between published index snapshots, never inferred completions.
- Public workflow status is a separately labeled newest-100 GitHub Actions observation, not the full execution state or scientific evidence.
- The result is a dated, copyable ChatGPT prompt. GitHub cannot inject a message into a personal ChatGPT conversation; the user must bring the prompt into a conversation, or a separately authorized ChatGPT schedule must run its own source checks.
- The read-only public file is `docs/live/data/daily-correspondence.json`; the scheduled workflow only writes this data file and preserves an Actions artifact. Failed publication does not silently advance the day.

Local reproduction: `python -m unittest -v network.tests.test_daily_correspondence`. With a known full source revision, invoke `python -m systems.calendar.daily_correspondence --revision <sha> --output /private/daily-correspondence.json`. A private workspace journal can be provided explicitly with `--workspace-journal`, but it must never be published to the public page.
