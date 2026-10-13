# Protocol Network

Protocols are reusable operational contracts. They share a referent-preserving evidence contract (formerly labeled A/B-constrained):

**referent → evidence → witnesses → result → provenance → continuation**

A protocol may specialize the witness conditions, but it may not silently change the outer contract.

## Core protocols

- [`core/referent.md`](core/referent.md) — preserve and change the active referent.
- [`core/evidence.md`](core/evidence.md) — admit evidence and preserve uncertainty.
- [`core/movement.md`](core/movement.md) — make one supported movement.
- [`core/wall.md`](core/wall.md) — stop without fabricating an edge.
- [`core/handoff.md`](core/handoff.md) — move work between agents/tools while preserving the referent.
- [`core/provenance.md`](core/provenance.md) — preserve natural provenance: local state stays local while relational ancestry remains continuously traceable across layers.
- [`core/provenance-link.schema.json`](core/provenance-link.schema.json) — optional machine-readable `from → relation → to` ancestry edge for connecting unlike local layers without flattening them.

## AI protocols

- [`ai/session.md`](ai/session.md) — enter and operate a session.
- [`ai/repo-write.md`](ai/repo-write.md) — mutate this repository without losing provenance.
- [`ai/purge.md`](ai/purge.md) — neutral one-item-at-a-time repository cleanup review.
- [`ai/james.md`](ai/james.md) — gate repository additions by James-confirmed speaker identity without inferring identity from style or topic.

## Research protocols

- [`research/source.md`](research/source.md) — discover, inspect, compare, and resolve external sources around a bounded referent.

**OSINT is swallowed here.** It does not need a separate witness contract. “OSINT” remains useful vocabulary for public/open-source investigation, but operationally it is one surface/domain label for source research.

## Work protocols

- [`work/bounded-problem.md`](work/bounded-problem.md) — externally supplied finite problems.
- [`work/job-hunt.md`](work/job-hunt.md) — discover and admit external work; uses `research.source` for public-source retrieval.

## Language protocols

- `language.decode`
- `language.render`

Read-only projections are generated through `views/` and source-specific generators; they no longer require a separate output-lens protocol.

Future domain protocols should compose existing contracts rather than duplicating a child protocol whose witness contract is already represented one layer up.
