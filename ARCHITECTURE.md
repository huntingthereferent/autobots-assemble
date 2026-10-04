# Architecture — All Work Over Separate Axes

The repository has one shared operating kernel. **ALL WORK** is the literal superset of purposeful work across every field, medium, scale, and realization layer.

Do not confuse three different classification axes:

1. **Goal lane** — why the work is being done.
2. **Field / domain** — what kind of world or knowledge the work touches.
3. **Realization layer** — how far the work has moved from idea toward observed operation.

```text
                                ALL WORK
                                   │
                            SHARED KERNEL
             A/B · language · network · protocols · lenses
                    evidence · provenance · state
                                   │
             ┌─────────────────────┼─────────────────────┐
             │                     │                     │
      THEORY / RESEARCH        OPEN SOURCE          MONEY / JOBS
          goal lane              goal lane             goal lane
             │                     │                     │
             └─────────────────────┼─────────────────────┘
                                   │
                          work can touch ANY field
                                   │
      math · physics · biology · chemistry · software · electronics
       mechanical · fabrication · manufacturing · construction · ...
                                   │
                          and ANY realization layer
                                   │
       idea → research → model → simulation → design → implementation
         → physical build → measurement → inspection → validation
                           → deployed / operating
                                   │
                              FOUNDATION
                                   │
                         credibility lens(es)
```

## ALL WORK

“ALL WORK” is not shorthand for computer work, paid work, freelance work, research, or open source.

It means work in **all fields and all layers**.

Examples may include:

- proving or testing a mathematical relation;
- reading and connecting academic papers;
- fixing an upstream software bug;
- writing a paid spreadsheet automation;
- designing a circuit;
- building a controller;
- fabricating a mechanical part;
- measuring tolerances;
- testing a material or process;
- debugging a robot;
- validating a production step;
- designing or operating larger physical systems.

No field is privileged by the architecture.

## Axis 1 — Goal lane

The current goal determines the lane.

### Theory / Research

Primary question:

> What is interesting, true, structurally useful, unresolved, or worth following?

No requirement to monetize or contribute upstream.

### Open Source

Primary question:

> What public project can I contribute to under its upstream rules?

Payment may occur, but it is not assumed.

### Money / Jobs

Primary question:

> What bounded external work can be completed, submitted, accepted, or paid?

No requirement to contribute to theory.

### Why physical is not a goal lane

“Physical,” “software,” “mathematical,” and similar terms describe **what the work touches**, not why it is being done.

A physical build can be:

- research;
- open source;
- paid work;
- or another future goal lane.

Do not create a separate “physical” goal lane merely because the implementation leaves software.

## Axis 2 — Field / domain

Field labels are open-ended. Examples:

- mathematics;
- computer science / software;
- physics;
- chemistry;
- biology;
- electronics;
- electrical engineering;
- mechanical engineering;
- controls / robotics;
- materials;
- fabrication;
- manufacturing;
- construction / infrastructure;
- medicine / life science;
- finance / economics;
- and any future field reached by the current referent.

Cross-field work keeps each field's witness conditions rather than flattening them into one generic “hard problem.”

## Axis 3 — Realization layer

A useful generic ladder is:

```text
idea
→ research
→ model
→ simulation
→ design
→ implementation
→ physical build
→ measurement
→ inspection
→ external validation
→ deployed / operating
```

This is not a mandatory linear lifecycle. Work may skip layers, loop backward, or use field-specific layers.

The important rule is **do not upgrade the reached layer**.

Examples:

```text
designed ≠ simulated
simulated ≠ built
built ≠ measured
measured ≠ independently validated
validated prototype ≠ deployed system
```

The same applies in software and research:

```text
idea ≠ implementation
implementation ≠ tested
tested ≠ externally reviewed
paper read ≠ claim reproduced
model proposed ≠ empirical validation
```

## Foundation

Foundation is the preserved body of demonstrated work across lanes, fields, and realization layers.

It is **not** a résumé and **not** a self-declared credibility score.

A foundation record preserves what was actually reached:

- problem/referent;
- field(s);
- goal lane;
- constraints;
- uncertainty crossed;
- interfaces crossed;
- artifact/result;
- realization layer reached;
- evidence and tests;
- measurements/inspection when physical;
- external review/acceptance when present;
- failures/corrections;
- provenance.

The same work item remains in its original lane. Foundation references it rather than moving it.

## Credibility

Credibility is a **derived output lens over Foundation evidence**.

```text
many preserved work records
        ↓
filter by field / difficulty / evidence depth / realization layer
        ↓
credibility lens
```

The lens may show repeated closure across unlike problems, but it may not manufacture a stronger claim than the evidence supports.

One software merge, one measured physical build, one reproduced research result, and one externally accepted paid deliverable remain different kinds of evidence even when shown together.

## “Hard”

“Hard” is not a universal scalar and should not be reduced to code complexity.

Useful evidence dimensions include:

- number/severity of real constraints;
- uncertainty crossed;
- interfaces crossed;
- required precision/tolerance;
- scale;
- performance burden;
- consequences of error;
- validation burden;
- failed approaches/corrections;
- independence of external witness;
- distance from initial idea to observed result.

These dimensions may support later comparison lenses. They do not erase domain-specific difficulty.

## Crossing goal lanes

A goal-lane crossing is an explicit handoff: `HANDOFF.BOUNDARY`.

Examples:

```text
research result
→ useful upstream implementation
→ HANDOFF.BOUNDARY
→ open-source candidate
```

```text
open-source issue gains a bounty / paid contract
→ compensation becomes primary
→ HANDOFF.BOUNDARY
→ money/job candidate
```

```text
paid physical build exposes a novel mechanism
→ HANDOFF.BOUNDARY
→ research candidate
```

The source work remains provenance. The destination lane re-validates under its own goal and witness contract.
