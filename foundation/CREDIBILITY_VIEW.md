# Credibility View Contract

Credibility is a **read-only projection over Foundation records**.

It is not an editable score and it does not select development.

## Input

- Foundation records;
- requested audience/filter;
- optional dependency-layer / realization-depth / evidence constraints.

## Possible views

- hardest demonstrated work;
- repeated closure across unlike problems;
- external-review history;
- physical realization depth;
- software ↔ hardware ↔ physical-process crossings;
- measurement/inspection evidence;
- research reproduction evidence;
- paid acceptance evidence.

## Invariant

A view may aggregate and compare, but it may not upgrade evidence.

```text
render(foundation, requested_view)
→ claim + visible supporting records
```

If the supporting records do not justify a claim, weaken the claim or return UNKNOWN/PARTIAL.
