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

## Cross-platform movement reduction

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

## A branch can travel farther than intended

James names the larger conversational subject **Human Drift**. His [dated words](../HUMAN_DRIFT.md) show him changing examples across September–October to move around an assistant's misunderstanding. **Regrounding** is one response, and *surfing* was one example. The [regrounding record](../REGROUNDING.md) preserves the distinction: relate newly acquired observations to the earlier referent instead of deleting them. `BRANCH`, `REPLY`, `SILENCE` and `REOPEN` can document **specific platform-visible actions**. They do not, by themselves, prove how a person understood those actions or how far a conversation moved in their mind.

A quiet participant may have observed more than the platform shows. No reply can help or hurt; the `SILENCE` anchor only records the *lack of an expected return during a stated window*, not that person's intention, emotional response, or agreement. Regrounding is a human-language practice here, not a new platform event ID or an automated return.

**Time is not only event order.** A person may experience a pause immediately, and that experience may shift while the platform still records no reply. The `SILENCE` anchor describes a bounded observable absence; it cannot represent a continuous felt response or recover how that response changed. If the lived sequence matters, preserve the first contemporaneous account, later observations, and later recollection separately, when available. See [Human Drift — October 16](../HUMAN_DRIFT.md#october-16--silence-changes-with-time-even-without-words). This does not add a new movement type or claim another person's intention.

James's outward observations may intersect across many situations. This social-action bank is a narrow representation of witnessed interface mechanics, not a substitute for his description or for the [canonical language referent](../../LANGUAGE_REFERENT.md).
