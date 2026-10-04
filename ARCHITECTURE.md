# Architecture — Shared Kernel, Separate Lanes

The repository has one shared operating kernel and two intentionally separate human-goal lanes.

```text
                         SHARED KERNEL
        A/B boundary · language · network · protocols · lenses
                    evidence · provenance · state
                              │
                 ┌────────────┴────────────┐
                 │                         │
          THEORY / RESEARCH            MONEY / JOBS
                 │                         │
          research/                    money/
          domains/                     jobs/
          papers/notes/dives           paid work / bids /
          experiments                  deliverables
```

## Why the split exists

Research and money can touch, but they do not have the same objective.

A research dive may be interesting with **no commercial use at all**. A job may be useful even if it contributes nothing to theory. Mixing the two causes accidental reorientation: curiosity starts being judged by whether it pays, or paid work starts being treated as evidence for theory merely because it used the same tools.

## Shared kernel

Both lanes may use the same:

- A/B witness/evidence boundary;
- language and operator phrases;
- handoff language;
- source research;
- generic relation network;
- provenance;
- output lenses;
- tool/session protocols.

Shared machinery does not collapse the goals.

## Theory / research lane

Primary question:

> What is interesting, true, structurally useful, unresolved, or worth following?

Typical outputs:

- research dives;
- theory notes;
- paper/source maps;
- experiments;
- domain dissections;
- unresolved questions;
- possible connections.

No requirement to monetize.

## Money / jobs lane

Primary question:

> What bounded external work can be completed, submitted, accepted, or paid?

Typical outputs:

- opportunities;
- job records;
- bids/proposals;
- deliverables;
- acceptance tests;
- submission/payment state.

No requirement to contribute to theory.

## Crossing the boundary

A crossing is an explicit handoff, never an automatic promotion.

Examples:

```text
research dive
→ "this might solve a paid problem"
→ HANDOFF.BOUNDARY
→ money/job candidate
```

or:

```text
job exposes a reusable structural pattern
→ HANDOFF.BOUNDARY
→ research/theory candidate
```

The source lane remains provenance. The receiving lane re-validates under its own goal and witness contract.
