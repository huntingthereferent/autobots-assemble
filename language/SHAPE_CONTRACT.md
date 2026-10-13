# Language-Neutral Shape Contract

A **shape** is a reusable movement/interaction handle recovered from a surface expression.

It is not a dictionary sense and not a claim that all utterances with similar wording are identical.

## Shape record

Each shape may carry:

- `id` — language-neutral handle such as `MOVE.CONTINUE`
- `canonical` — short English gloss for inspection
- `definition` — operational meaning
- `preserves` — what must remain stable across the movement
- `does_not_imply` — common over-interpretations to block
- `surfaces` — language/register realizations
- `ambiguity` — known alternate readings that require context
- pragmatic modifiers recovered from the actual utterance

## Decode contract

```text
surface
→ candidate shape(s)
→ referent/context check
→ selected shape OR unresolved alternatives
→ pragmatic modifiers
```

A decoder must be able to return multiple candidate shapes or UNKNOWN.

## Render contract

```text
shape + referent + pragmatics + target language/register
→ surface expression
```

Rendering must not silently strengthen certainty, approval, authority, urgency, or scope.

## Closure

The decoded output is valid input to the same language-neutral contract on the next interaction. The representation may change; the preserved movement/referent does not have to.

## Human language is larger than a shape ID

[Regrounding and surfing](REGROUNDING.md) describes the parent relationship. A shape ID is an **operational projection of a particular utterance**, not the identity of a person, the language referent as a whole, or the complete social consequence of speaking or remaining silent.

Retain the actual words and context when needed for later correction. Playfulness, swearing, softness, annoyance, timing, and other visible details may matter. An AI-authored paraphrase must not silently replace a direct quote. Interpretations should be revisable when another observation arrives.

James's conversational "swallowing" means taking observations in across settings; it does not automatically invoke `LAYER.ABSORB`. "Surfing" describes continuing while regrounding, not necessarily an executable `MOVE.CONTINUE` command. If intent or referent cannot be grounded, preserve the alternatives rather than forcing the nearest bank entry.

## Scope of closure

Re-entry applies to the **shape contract** when its declared requirements are met. It is not proof that a conversation has come back to the same meaning, that an unresolved relationship was preserved, or that the same wording remains correct forever. Reground against the active referent and any new correction before continuing.
