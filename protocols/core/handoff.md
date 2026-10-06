# Core Protocol — Handoff

A handoff moves a **current referent and one required relation** across an execution boundary without silently changing what the work means or what counts as evidence.

The receiver may be a human, AI, program, tool, machine, organization, simulator, repository, or future session.

A handoff is the carrier. A task, job, command, prompt, work order, or simulator event is a projection/adaptation of that carrier.

## Required handoff contract

A handoff must preserve:

- **handoff id** — stable identity for this bounded movement;
- **current referent** — what the movement is actually about;
- **from / to actor** — the boundary being crossed;
- **required relation** — what the receiver is being asked to establish or move;
- **inputs** — admitted state/data entering the boundary;
- **expected output** — the shape needed back, without pretending it already exists;
- **required witnesses** — what must be supported before the movement can close;
- **admissible evidence** — what evidence kinds are allowed to support each witness;
- **dependencies** — prior handoffs that must close before this one can move;
- **boundaries** — claims or upgrades that are forbidden;
- **provenance** — parent handoffs / source path needed to recover why this handoff exists.

## Return contract

The receiver returns:

```text
result state
+
output
+
evidence
+
unresolved wall / note when present
```

A `COMPLETE` return is invalid unless every required witness is supported by an admitted evidence kind.

Simulation may satisfy a witness whose contract admits simulation evidence. It may not silently satisfy a witness requiring measurement, inspection, human confirmation, machine telemetry, or another stronger/different evidence kind.

## Event history

Live implementations should preserve handoff movement as append-only events and derive current state from those events.

Typical states:

```text
WAITING
READY
ACTIVE
COMPLETE
PARTIAL
BLOCKED
FAILED
UNKNOWN
```

A later correction or reopening adds a new event. It does not erase the earlier result.

## Projection rule

The outer carrier survives changes in recipient:

```text
handoff → human adapter      → task
handoff → AI adapter         → bounded context / request
handoff → program adapter    → job
handoff → machine adapter    → command / work order
handoff → simulator adapter  → simulated event
```

The projection may change. The referent, witness/evidence boundary, provenance, and required return may not silently change with it.

## Closure requirement

The returned result must remain valid input to the next handoff under an explicit evidence contract.

If a receiving layer genuinely requires a different witness contract, record that boundary rather than pretending the contracts are equivalent.

## Executable realization

The first executable realization is in [`runtime/`](../../runtime/README.md).

It pressure-tests the same handoff carrier across:
- James-style human task routing;
- Online School task routing;
- software jobs;
- simulated factory/machine commands.

The runtime is an implementation of this protocol. It is **not A/B itself**.
