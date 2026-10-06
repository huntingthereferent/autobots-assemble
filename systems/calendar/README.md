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
