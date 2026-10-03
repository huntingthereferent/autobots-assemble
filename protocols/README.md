# Protocol Network

Protocols are reusable operational contracts. They all share the same A/B-constrained outer shape:

**referent → evidence → witnesses → result → provenance → continuation**

A protocol may specialize the witness conditions, but it may not silently change the outer contract.

## Core protocols

- [\`core/referent.md\`](core/referent.md) — preserve and change the active referent.
- [\`core/evidence.md\`](core/evidence.md) — admit evidence and preserve uncertainty.
- [\`core/movement.md\`](core/movement.md) — make one supported movement.
- [\`core/wall.md\`](core/wall.md) — stop without fabricating an edge.
- [\`core/handoff.md\`](core/handoff.md) — move work between agents/tools while preserving the referent.
- [\`core/provenance.md\`](core/provenance.md) — retain source/witness/parent history.

## AI protocols

- [\`ai/session.md\`](ai/session.md) — enter and operate a session.
- [\`ai/repo-write.md\`](ai/repo-write.md) — mutate this repository without losing provenance.

## Work protocols

- [\`work/bounded-problem.md\`](work/bounded-problem.md) — externally supplied finite problems.
- [\`work/job-hunt.md\`](work/job-hunt.md) — discover and admit external work.
- [\`work/osint.md\`](work/osint.md) — public-source investigation.

Future domain protocols should compose these rather than replacing them.
