# Axioms

Axioms is the clean mathematical layer beneath Eggy.

It is not an Eggy rewrite and does not inherit Eggy's runtime architecture. Existing Eggy work is retained as an evidence bank: successful witnesses, counterexamples, failure modes, and regression cases may inform Axioms, but they do not define its shape.

## Current ground

Axioms begins with one object and one operation:

```
X --A/B--> X'
```

The first requirement is recursive closure:

```
X0 --A/B--> X1 --A/B--> X2
```

The second application must not require a human to choose a new middle comparison, WATCH, layer, placement, or interpretation.

The result of A/B must remain admissible to A/B under the same mathematical/evidentiary contract.

## Evidence discipline

Axioms must preserve the lessons already earned in Boundary Math and Eggy:

- unsupported movement is not promoted into movement;
- unmatched is not silently promoted into loss or gain;
- coverage is not automatically preservation;
- zero / no-boundary must be earned;
- missing evidence may remain UNKNOWN;
- UNKNOWN is not failure and must not be filled by invention;
- provenance and the support for a relation must survive any movement that depends on them.

## First milestone

Demonstrate, on a tiny bounded shape:

```
X1 = A/B(X0)
X2 = A/B(X1)
```

with no hidden human orientation between the two calls.

If this cannot be done, stop at the smallest missing relation or contract boundary. Do not add a higher-layer operator to force progress.

## Not yet in scope

No filesystem observer, PC security layer, TOP runtime, psi runtime, Meta layer, placement engine, autonomous agent, database, persistence framework, or Eggy compatibility layer is authorized yet.

Persistence and world adapters come only after recursive closure is demonstrated in memory.

## Repository governance

Repository maintenance and write-authority rules are defined separately in `REPO_PROTOCOLS.md`. They are operational controls and do not modify the A/B mathematical contract.
