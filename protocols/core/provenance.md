# Core Protocol — Provenance

Every meaningful movement must be reconstructable.

## Natural provenance

**Natural provenance is the preserved relational ancestry left behind as a current referent moves.**

It is not a separate history imposed after the fact. Movement itself produces the ancestry:

```text
current referent
→ supported relation changes
→ new current referent

behind the new current referent remain:
  source
  prior referent
  relation traversed
  evidence admitted
  transformation / decision
  result
  what survived
  what was rejected or invalidated
```

The current referent remains the front of movement. Prior state does not become current merely because it is remembered.

```text
FRONT
what is currently in relation
        ↓
next supported movement

BACK
reachable provenance explaining how the front was reached
```

A later movement may reach backward when the present relation makes earlier evidence relevant. Reaching backward does not restore the old state; it brings the relevant evidence forward for reconciliation with the present.

## Repository invariant

> **Local state, continuous provenance.**

Each layer keeps its own native model, language, boundaries, and state. Layers do not need one universal state schema in order to remain connected.

Continuity is preserved by relational ancestry:

```text
local state A
  └─ provenance edge
       ↓
artifact / handoff / evidence / transformation
       └─ provenance edge
            ↓
local state B
```

This allows unlike layers to remain locally correct while later traversal can reconstruct how a current relation crossed those layers.

Visual provenance, artifact provenance, runtime/handoff provenance, research/source provenance, external traversal traces, educational evidence, company/operating provenance, and future domain provenance are specializations of this same continuity rule.

External traversal is the case where the touched state remains outside Continuity. The local provenance edge preserves why the external thing was touched, what relation it added, and how movement continued without claiming ownership of the external state. See `traversal.md`.

They may carry different local fields. They must preserve enough ancestry to remain traceable.

## Preserve, when applicable

- current referent identifier;
- source URI/file/repository/tool/system;
- source timestamp or observation time;
- prior/parent referent, movement, artifact, evidence, or handoff identifier;
- relation traversed or claim supported;
- witness condition satisfied;
- evidence admitted and its depth;
- transformation / interpretation / decision performed;
- result or new referent produced;
- what remained valid through the movement;
- what was rejected, superseded, or invalidated;
- test / acceptance result;
- actor/tool/system that performed the movement;
- boundary or uncertainty that survived the movement.

Not every layer uses every field. Do not force a local system to adopt fields that have no meaning there.

When a durable machine-readable cross-layer edge is useful, use `provenance-link.schema.json`. It is a carrier for ancestry (`from → relation → to`), not a replacement for either layer's local state.

## Cross-layer continuity

When one layer emits something another layer consumes, preserve a traceable edge in both directions where practical:

```text
originating local object
→ emitted artifact / handoff / evidence reference
→ receiving local object
```

The receiving layer may translate the object into its own schema. Translation must not erase the originating reference or pretend the schemas are identical.

A current object should be able to answer, to the depth supported by available evidence:

```text
Where did this come from?
What changed?
What evidence supported that change?
What survived?
What would invalidate it?
What local object consumed or produced it next?
```

## State is not provenance

Current state answers:

> What is represented now?

Evidence answers:

> What supports or contradicts this relation?

Provenance answers:

> By what preserved relational path did the current representation become current?

Do not use provenance as a prediction that overrides present evidence.

Do not erase old evidence merely because the current state changed.

## Views

Generated summaries, dashboards, indexes, and other views are projections. They do not replace canonical evidence, local state, or provenance ancestry.

A view may collapse the trail for readability. The underlying trail must remain reconstructable.
