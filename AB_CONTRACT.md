# A/B Contract Boundary

## What A/B is

A/B is **language for recognizing, describing, and continuing relationships in movement**. The referent is the relationship through the step; it is not itself a theorem, equation, notation system, or a specific mathematical operation. See the [A/B Ground Record — Current Note (2026-10-11)](AB_Ground_Record_Current_Note_2026-10-11.md) for the language-first correction, the same-referent/other-side distinction, and the proposed two-step of material coupling.

Mathematics is a human formal language. Particular A/B-labeled generators, inverse constructions, and correspondence proofs in this repository are **formal mathematical representations** of specified relations, with their own state spaces, assumptions, witnesses, and scope. Do not mistake a result proved for a particular finite transformation family for a definition or universal proof of A/B.

This repository does **not** redefine A/B as a workflow engine, project manager, policy engine, state machine, job tracker, filesystem layout, or AI prompt.

## What “use A/B” means in this repository

Operational layers must respect these invariants:

1. **Current referent is primary.** Older layers are evidence only when the current relation actually reaches them.
2. **Movement requires a witness/evidence contract.** A relation is not admitted merely because it is convenient or plausible.
3. **Outputs remain admissible inputs.** A completed movement can be presented to the same contract on the next pass without changing the meaning of the contract.
4. **Walls are explicit.** Missing evidence, missing authority, inaccessible tools, unresolved correspondence, or incompatible contracts produce a wall rather than a fabricated bridge.
5. **UNKNOWN/PARTIAL are preserved.** Lack of evidence is not evidence of absence, and coverage is not automatically preservation.
6. **Provenance survives movement.** Source, witness, parent relation(s), and the reason for movement remain recoverable.
7. **No silent reorientation.** An implementation detail, old experiment, or prior conclusion cannot replace the current referent unless a supported movement reaches it.
8. **Another side, same referent.** A blocked relationship may be inspected from another vantage; this does not license a new referent or bypass the witness conditions.

## Operational movement shape

```text
CURRENT REFERENT
      +
ADMISSIBLE EVIDENCE
      +
WITNESS CONTRACT
      |
      v
MOVE / WALL / UNKNOWN / PARTIAL
      |
      v
OUTPUT RELATIONS + PROVENANCE + NEXT REFERENT
```

The protocol is an application boundary. It is **not A/B's language-level definition**, a universal mathematical result, or a verified physical two-step.

## Recursion test

A protocol is structurally acceptable only if its output can be used as input to another run of the same protocol shape without inventing a new evidence standard.

That is the practical closure test used throughout this repository.
