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
