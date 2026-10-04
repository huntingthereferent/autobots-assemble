# Credibility Lens Contract

Credibility is a **read-only projection over Foundation records**.

It is not an editable score.

## Input

- Foundation records;
- requested filter or audience;
- optional field / realization / evidence-depth constraints.

## Possible views

- hardest demonstrated work;
- repeated closure across fields;
- external-review history;
- physical realization depth;
- software → hardware → physical-process crossings;
- measurement/inspection evidence;
- research reproduction evidence;
- paid acceptance evidence.

## Invariant

The lens may aggregate and compare, but it may not upgrade evidence.

```text
render(foundation, credibility_view)
→ claim + visible supporting records
```

If the supporting records do not justify a claim, the lens must weaken the claim or return UNKNOWN/PARTIAL.
