# Language-Neutral Shape Contract

A **shape** is a reusable movement/interaction handle recovered from a surface expression.

It is not a dictionary sense and not a claim that all utterances with similar wording are identical.

## Construction follows movement, not a fixed container

James's current working principle is that a finite representation should adapt
to the relations and decisions being constructed, rather than forcing those
decisions to fit an arbitrary fixed representation. This is a **design rule and
testable hypothesis**, not a proof that every finite construction succeeds.

In the periodic computational-world example, retain the toroidal family
`W_N = Z_N × Z_N` and allow the resolution `N` to grow as the represented
objects and relationships require. For integer `k >= 2`, the explicit
embedding `E_k(x,y) = (kx,ky) mod kN` preserves periodic coordinate
relationships at the scaled resolution. A one-cell movement becomes a
`k`-cell movement: the geometry changes scale, and motion must be compared
through the embedding rather than assumed identical.

The original objects, source identities, decisions and evidence remain
authoritative. A projection collision is not an identity or a discovered
relationship. A larger world alone does not prove relation preservation;
test the projection against the actual relations and trajectories.

Executable bounded example:
[`work/arc_like_maze/toroidal_projection.py`](../work/arc_like_maze/toroidal_projection.py).
This is one implementation of the principle, not a definition of the entire
language referent or James's experience.

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


**Source withdrawal boundary:** Do not republish, reconstruct, or attribute quotations removed from the current withdrawn public writing. Retain the distinction between an authorized quote, a technical example, and an AI paraphrase.
