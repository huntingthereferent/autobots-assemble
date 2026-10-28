# Language-Neutral Shape Contract

A **shape** is a reusable movement/interaction handle recovered from a surface expression.

It is not a dictionary sense and not a claim that all utterances with similar wording are identical.


## A finite view of a moving world

James describes continuity using a **moving torus**: movement, changing relationships, and the changing container belong to one unfolding structure. This contract uses small, bounded computational worlds to examine parts of that movement. The model is not the whole of continuity.

A finite toroidal world can be pictured as a grid that wraps around. Move past its right edge and you return at the left; move past the top and you return at the bottom. Two coordinates locate each position.

Three things must be kept separate when checking an implementation:

- **Where something is:** its position in the current representation.
- **How it moves:** a specified rule that takes the present position and an admitted action or input to the next position.
- **How it relates:** which connections are present and how those connections change as movement and observations occur.

The wraparound grid specifies possible positions. **It does not, by itself, specify movement or relationships.** Each worker must define and test those rules.

## Growing the world without inventing continuity

A finite representation may need more room as its objects and relationships develop. Growing the grid changes its resolution, not the identity of the source objects.

For example:

1. Start with an **8-by-8 wraparound world**. An object is at position `(3, 5)`.
2. Double the resolution to a **16-by-16 world**. Keep the same object and place it at `(6, 10)`.
3. Its proportional location is unchanged. Every old position has one distinct corresponding position in the larger world.
4. A movement of **one cell** in the original world corresponds to **two cells** in the doubled world. Calling a one-cell move in both worlds "the same movement" would be a mistake.

This example works for any positive grid size multiplied by a whole-number growth factor of at least two: multiply both old coordinates by that factor, and enlarge both sides of the grid by the same factor.

**The essential movement test:** move in the smaller world and then scale the result. Separately, scale the starting position and apply the explicitly corresponding action in the larger world. The two results must agree. The implementation must say which actions correspond; the scaling rule alone does not decide that.

Preserving positions is not enough. Before claiming that a relationship or trajectory survived a change in resolution, compare it with the original source identities, decisions, and observed movements. A collision in a projection is not evidence that two things are the same or related.

## Relationships must have an actual update rule

At each step, the world may contain a different set of connections between objects. The next set must come from a defined process: movement, an observation, or an explicit relationship update. Record which process produced the change and what evidence supports it.

Do not silently substitute a fixed graph, a convenient layout, or an attractive visualization for those changing relationships. Nor should the representation force source decisions to fit an arbitrary fixed size.

A finite wraparound grid is not the same mathematical object as a smooth, continuous two-dimensional torus. Other finite toroidal constructions, including three-dimensional ones, have their own coordinates, movement rules, and validation requirements. A torus-shaped display alone proves nothing about physical continuity or about whether a worker follows the intended relationships.

**Research status:** These are definitions and checks for bounded models, not proof of universal continuity, a completed moving-torus worker, or equivalence among different models in this repository.

## Construction follows movement, not a fixed container

James's working principle is to let a finite representation adapt to the relations and decisions being constructed, rather than force those relations into a predetermined container. This remains a **design rule to test**, not a claim that every construction succeeds.

The executable example, [`work/arc_like_maze/toroidal_projection.py`](../work/arc_like_maze/toroidal_projection.py), grows a wraparound coordinate layout and checks that source identities and scaled positions remain intact. It does **not** establish that movement rules or source relationships are preserved; those require their own checks. It is one bounded implementation, not the complete language referent or a reproduction of James's experience.

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
