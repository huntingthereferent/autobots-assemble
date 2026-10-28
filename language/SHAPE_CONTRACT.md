# Language-Neutral Shape Contract

A **shape** is a reusable movement/interaction handle recovered from a surface expression.

It is not a dictionary sense and not a claim that all utterances with similar wording are identical.


## Finite toroidal mapping of continuous movement

James describes continuity through moving toroidal geometry. In this repository, finite systems are bounded mathematical and computational representations used to map movement and its changing relationships. A finite map is not the entirety of continuity, and the existence of a toroidal display does not by itself establish that a system's transition rule models the intended relationships.

For the two-coordinate periodic model, let \(N\) be a positive integer and define

\[
W_N=(\mathbb{Z}/N\mathbb{Z})\times(\mathbb{Z}/N\mathbb{Z}).
\]

Each coordinate is an equivalence class of integers modulo \(N\). A discrete movement is a specified transition \(F_N:W_N\times U_N\to W_N\), where \(U_N\) is the set of admitted inputs or actions. The map \(F_N\) must be given and tested for each implementation; periodic coordinates alone do not define motion or determine which relationships are preserved.

For an integer \(k\geq 2\), the resolution-changing map

\[
E_{N,k}:W_N\longrightarrow W_{kN},\qquad E_{N,k}([x]_N,[y]_N)=([kx]_{kN},[ky]_{kN})
\]

is well-defined and injective. It preserves normalized coordinate locations: \(kx/(kN)=x/N\) and \(ky/(kN)=y/N\) for chosen representatives \(0\leq x,y<N\). It does **not** automatically preserve movement. For specified actions and corresponding inputs, transition compatibility is the separate condition

\[
E_{N,k}(F_N(w,u))=F_{kN}(E_{N,k}(w),\iota_{N,k}(u)),
\]

where \(\iota_{N,k}:U_N\to U_{kN}\) is an explicitly defined action correspondence. This equality must be checked, not presumed. In particular, a one-cell step at resolution \(N\) does not correspond to a one-cell step at resolution \(kN\) under \(E_{N,k}\).

The smooth two-dimensional torus \(\mathbb{T}^2=S^1\times S^1\) is a distinct mathematical object from the finite set \(W_N\). A toroidal embedding or rendering of finite coordinates is a projection of a chosen model, not proof of a continuous physical process. Other existing finite toroidal constructions, including the cubical three-torus, retain their own dimensions, transition rules, and proof obligations.

A changing relation must be specified separately, for example as \(R_n\subseteq W_N\times W_N\) at step \(n\). Whether the next relation \(R_{n+1}\) is induced by movement, observation, or an explicit update rule is an implementation question that requires a defined rule and evidence. The finite container's represented contents and relationships may change with movement; neither a fixed graph nor a visualization should silently be treated as the source of those changes.

**Research status:** These are precise definitions and test obligations for finite representations. They do not claim a universal proof of continuity, a completed moving-torus worker, or equivalence between the repository's different finite models.

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
