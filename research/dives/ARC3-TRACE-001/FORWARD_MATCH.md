# ARC3-TRACE-001 — A/B-Constrained Forward Match

**Layer:** one layer above direct game interaction  
**Status:** candidate operational acceleration  
**Boundary:** this is an application of currently supported A/B constraints; it is **not** a new definition of A/B and does not resolve Axioms' open correspondence question.

## Why this exists

ARC-AGI-3 charges for environment actions while internal reasoning is effectively free with respect to RHAE.

A naive trace can therefore be correct but expensive:

```text
see unknown
→ probe
→ see another unknown
→ probe
→ repeat
```

The forward-match layer tries to replace unnecessary probes with supported candidate projections.

The Axioms evidence that motivates this is Experiment #2:

> a derived output may carry parent/source relations that make a later comparison admissible without carrying a schedule naming what to compare next.

The important shape is:

```text
do not carry "try B next"
carry the relation evidence that could make B admissible
```

## ARC3 mapping

A directly witnessed game transition is represented as:

```text
P0 --ACTION a--> P1
        |
        v
      Δ(P0,P1)
```

The delta is a derived relation object with provenance back to:

- pre-state / local context;
- chosen action;
- post-state / changed context;
- the exact cells/objects/regions used to identify the delta.

Now suppose another context `Q0` is related to `P0` by an already-supported correspondence `R`.

Examples of possible witnessed correspondences:

- translation / repeated spatial motif;
- same object role under a color or position mapping;
- repeated local topology;
- symmetric or copied region;
- same action affordance plus matching local neighborhood;
- a relation already preserved from an earlier level/state.

If the required parent relations correspond under `R`, we may generate a **forward candidate**:

```text
P0 --a--> P1
|          |
R          R?
v          v
Q0 --a--> Q1?
```

or, equivalently,

```text
observed ΔP
+ supported correspondence R
→ predicted ΔQ
```

The lower-right relation is **not admitted yet**. It is a prediction.

This preserves the Axioms distinction:

```text
recursive implementation / candidate propagation
!=
proof that the correspondence principle is universally valid
```

ARC3 itself becomes the witness surface.

## Forward-match contract

A forward candidate is allowed only when all of these are recoverable:

1. **source transition** — an actually observed action/effect pair;
2. **parent correspondence** — a supported relation connecting source context to candidate context;
3. **transformation rule** — how the observed delta is mapped through that correspondence;
4. **prediction** — exact observable state delta expected if the candidate is right;
5. **disconfirmation condition** — what observation would falsify it;
6. **provenance** — exact source transition and correspondence parents.

A forward candidate has status:

- `PREDICTED`
- `SUPPORTED`
- `FALSIFIED`
- `PARTIAL`
- `UNKNOWN`

`PREDICTED` is intentionally not `SUPPORTED`.

## One layer up: action selection

Do not ask only:

> Which action might work?

Ask:

> Which available action most efficiently separates the currently admissible forward candidates?

For each possible next action `a`:

1. project each current candidate model forward;
2. group candidates by the observable delta they predict;
3. prefer actions whose possible outcomes discriminate the most live candidate relations;
4. among equally informative actions, prefer the one that also has the strongest supported path toward the current inferred goal;
5. pay the live action only after this internal comparison.

Conceptually:

```text
witnessed relation graph
        ↓
forward candidate closure
        ↓
predicted outcome partitions
        ↓
choose one discriminating action
        ↓
live environment witness
        ↓
admit / falsify relations
        ↓
recurse
```

This is where speed may come from: **compute across possible next relations before spending an environment action.**

## What can be reused without another probe

If a relation has already been witnessed and the new context is supported as corresponding under the same parent relation, the system may carry the earlier effect forward as a prediction instead of rediscovering it from zero.

That can reduce repeated probing across:

- repeated objects;
- symmetric regions;
- later levels preserving earlier mechanics;
- copied motifs;
- equivalent action contexts.

The gain should be measured as environment actions avoided, not as subjective reasoning elegance.

## What may NOT be forward-matched

Do not project merely because two things look similar.

Forward matching stops at `UNKNOWN` when:

- the correspondence itself is only visual resemblance;
- one required parent relation is missing;
- a game-state change may have altered the mechanic;
- the action is available but its semantics are not yet witnessed;
- the candidate transformation cannot produce an exact observable prediction;
- competing correspondences cannot be distinguished.

## First ARC3 test

On the first official public environment:

1. record first-contact state and available actions;
2. take the minimum initial probe needed to create one witnessed transition;
3. preserve its derived delta and parents;
4. search the same frame/state for contexts supported as corresponding;
5. forward-project the effect into those contexts;
6. **before probing them**, record exact predictions;
7. choose the next live action that best discriminates those predictions;
8. score:
   - predictions made;
   - predictions supported/falsified;
   - live actions used;
   - repeated probes avoided;
   - whether outputs remained valid inputs to the same contract.

## Success criterion

This layer is useful only if it produces an observable reduction in action expenditure while preserving or improving correct relation admission.

The strongest result is not:

> A/B guessed the game.

It is:

> relations witnessed in one context generated falsifiable predictions in another context, those predictions were externally checked by the environment, and the same evidence contract recursively reused the result while spending fewer live actions.

That would be directly comparable to ARC3's efficiency boundary while remaining honest about what A/B evidence currently supports.
