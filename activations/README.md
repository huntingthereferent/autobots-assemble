# Activations

Activations are **named entrances into existing relational state**.

They sit between language decoding and the handoff runtime:

    surface expression
    → language decode / activation match
    → actor + current referent + projection + selectors
    → existing handoff state
    → human-facing projection

An activation is not a macro that invents work. It selects a known route through the ecosystem.

## Contract

Each activation records the explicit surface(s), actor/context, current referent entered, requested projection, selectors over live handoffs/state, source systems allowed to contribute, boundaries, and provenance for why the activation means what it means.

If the same surface means different things for different people, the actor/context disambiguates it.

## First activation — James / ohayo

    "ohayo"
    → James
    → current day
    → day attention
    → live handoffs assigned to James
      + explicit reminders due for James
      + Calendar relations applying to James today

The default projection is a **day-attention** view: live tasks/handoffs assigned to James plus explicit recurring reminders that are due for him. It remains a projection over existing state and does not invent obligations.

The same day-attention projection can be polled without speaking the activation word, which gives a notification/reminder surface something stable to check continuously. `ohayo` is the human-language entrance into that same state.

It does **not** manufacture an hourly calendar because James's current day-to-day contract is task-oriented: his timing is organized around the movement of the rest of the household/system.

The route is stored in registry.json.

## Relation to general language

General language decoding remains broader than activations.

    "continue"
    → MOVE.CONTINUE

    "ohayo" + actor=james
    → explicit activation route

A registered activation wins only when the actor+surface pair is explicit and unambiguous. Otherwise normal language interpretation continues.

## Relation to handoffs

Activations do not create a separate task model.

    handoffs across ecosystem
    → activation selectors
    → task projection

As school, companies, research, personal operations, software, or other systems emit handoffs for James, ohayo can see them without learning each subsystem's implementation.
