# Protocol — Output Lens

A lens is a read-only projection of an already-frozen snapshot.

## Input

- frozen snapshot
- selected lens
- optional presentation parameters

## Invariant

```text
render(snapshot, lens) -> output
snapshot_before == snapshot_after
```

A lens may hide, reorder, aggregate, translate, summarize, or restyle information. It may **not** create relations, update provenance, resolve UNKNOWN, or change the current referent.

## Built-in lenses

- raw
- json
- english

Domain lenses can be added later if their projection rules remain read-only.
