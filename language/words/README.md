# Words Movement Layer

Words Movement is a reusable interaction layer for **how language moves between people over time**.

It does not decide what an utterance means. The existing language layer still handles pragmatic interpretation and language-neutral shape IDs.

This layer asks a narrower question:

```text
given a live social referent,
what movement happened around it?
```

The first bank was reduced from repeated interaction mechanics across high-movement text systems: feed replies/mentions/quotes, threaded comments, chat mentions/threads/reactions, public comment replies, and project discussions.

Platform-specific verbs collapse into a small movement vocabulary:

```text
OPEN     introduce a referent into a social surface
PING     direct attention toward a person/group
REPLY    return movement to the current referent
BRANCH   open a sub-referent while retaining the parent
ECHO     carry the referent into another audience/context
REACT    emit a low-cost signal without a full reply
HANDOFF  transfer the next movement to another actor/surface
RESOLVE  close the active social loop without erasing history
SILENCE  preserve the absence of expected return across a time window
REOPEN   return a quiet/resolved referent to active movement
```

## A/B reduction

The source platforms use different interface words, but the underlying relation often survives:

```text
reply / comment reply / thread reply
→ REPLY

mention / @mention / notify participant
→ PING

quote post / repost / crosspost / share as post
→ ECHO

thread / nested comment / discussion branch
→ BRANCH

reaction / emoji reaction / like-like acknowledgement
→ REACT
```

The bank stores the collapsed relation, not a platform imitation.

## Calendar boundary

Calendar owns time truth, not social intent.

A CalendarEvent may carry `movement_anchor` as a temporal/social hint:

```text
calendar relation
+
movement_anchor
→ pipe knows the expected movement shape
```

Examples:

```text
09:00 publish update      movement_anchor=OPEN
10:00 ask James           movement_anchor=PING
14:00 response window     movement_anchor=REPLY
17:00 no return observed  movement_anchor=SILENCE
tomorrow follow-up        movement_anchor=REOPEN
```

The anchor does **not** automatically create a task, infer urgency, or claim that the movement occurred. It labels the expected/observed movement relation so Day-to-Day, handoff pipes, simulations, or later projections can use the same vocabulary.

## Simulation

Each anchor records likely successor movements. These are **possibilities, not predictions**.

A pipe can traverse:

```text
OPEN → REPLY → BRANCH → REPLY → RESOLVE
OPEN → PING → SILENCE → REOPEN
OPEN → ECHO → REACT
HANDOFF → REPLY → RESOLVE
```

The same output anchor remains valid input to the same movement bank on the next step.
