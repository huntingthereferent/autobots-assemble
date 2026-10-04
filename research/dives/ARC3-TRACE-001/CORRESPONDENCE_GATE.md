# ARC3 Forward Matching — Correspondence Gate

## Purpose

Forward matching only accelerates ARC3 if it can reuse evidence without silently manufacturing correspondence.

The first cross-environment attempt exposed the required gate.

## Gate

Before projecting a witnessed relation from source context `P` into candidate context `Q`, require an explicit correspondence witness:

```text
source relation
+ correspondence(P,Q)
→ forward candidate in Q
```

Without `correspondence(P,Q)`:

```text
source relation
+ resemblance / shared label
→ WALL
```

## Three correspondence scopes

### 1. Same state / repeated local structure

Strongest early target.

Examples:

- repeated motif in one frame;
- symmetric lanes/regions;
- duplicated object neighborhoods;
- same controllable object translated to another position.

The action semantics are already local to the same game. Only the context relation must be earned.

### 2. Same environment / later state or level

Potentially reusable, but preservation must be checked.

A mechanic witnessed on level 1 may become a candidate on level 2 only if evidence supports that the relevant relation survived the level/state boundary.

### 3. Different environment

Weakest automatic carry.

The standardized ARC3 action IDs are interface labels, not semantic correspondence witnesses.

Across games, carry the **contract and relation representation**, not the action meaning.

## Speed consequence

The acceleration target is therefore:

```text
minimal local grounding
→ find repeated/symmetric corresponding contexts
→ forward-project already witnessed effects
→ spend live actions only on unresolved gates
```

not:

```text
learn ACTION3 in game A
→ assume ACTION3 means same thing in game B
```

## One-layer-up action selection

Each unresolved candidate relation has a set of possible observable outcomes.

Choose a live action that:

1. tests the largest number of unresolved gates;
2. preserves already-supported relations;
3. avoids repeating a primitive already witnessed in an equivalent context;
4. can produce an exact falsification signal.

This converts A/B forward matching into **witness compression**:

```text
many candidate edges
→ one discriminating environment action
→ many edges supported/rejected
```

The measurable gain is not “number of guesses.”

It is:

```text
relations resolved per environment action
```

while retaining provenance and the same evidence contract.
