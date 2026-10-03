# A/B Contract Boundary

## What A/B is

A/B is the recursively reusable mathematical operation. Its output must remain valid input to the same operation under the same witness/evidence contract.

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

The protocol is an application boundary. It is not the mathematical definition of A/B.

## Recursion test

A protocol is structurally acceptable only if its output can be used as input to another run of the same protocol shape without inventing a new evidence standard.

That is the practical closure test used throughout this repository.
