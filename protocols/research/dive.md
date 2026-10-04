# Research Protocol — Exploratory Dive

## Identity

- **Protocol ID:** `research.dive`
- **Layer:** research
- **Purpose:** support open-ended academic/technical exploration while preserving enough structure to revisit the path later.

## Entry referent

Unlike `research.source`, a dive may begin with a deliberately broad or random entry referent.

Examples:

- a field;
- a paper;
- a term;
- a surprising result;
- a cross-domain connection;
- “something interesting in X”;
- an academic rabbit hole with no fixed endpoint.

The entry referent is still recorded. “Random” means the branch selection may be exploratory; it does not mean provenance disappears.

## Goal

Default goal when none is supplied:

> discover interesting, supportable structure and preserve the branches worth returning to.

A user may replace this with a more specific goal at any time.

## Movement

```text
entry referent
    ↓
sample / discover
    ↓
interesting candidate
    ↓
research.source for bounded inspection
    ↓
claim / mechanism / connection / question
    ↓
KEEP / DROP / UNKNOWN / BRANCH
    ↓
continue, return, or checkpoint
```

### KEEP

The branch is interesting enough to preserve in the dive record.

### DROP

The branch is not useful for the current dive. Dropping from active carry does not erase its historical trace when already recorded.

### UNKNOWN

Something appears potentially important but the evidence cannot yet support a stronger relation.

### BRANCH

A new referent is worth following as a child branch.

## Evidence contract

Every durable factual finding should identify its source and distinguish:

- directly supported content;
- interpretation;
- analogy/connection;
- speculation;
- unresolved question.

Use `research.source` for the bounded source work inside the dive.

## Save/checkpoint contract

A dive should be saved when any of these are true:

- the user says to save/bank/log it;
- the session found a durable connection or question worth revisiting;
- the dive is about to pause or change field;
- a handoff to another session/AI would otherwise lose the path.

Saving produces:

- `dive.json` — canonical state/provenance record;
- `DIVE.md` — human-readable review lens;
- optional notes/artifacts/source files.

Saving does **not** mean the dive is finished.

## Output contract

A reviewable dive should expose:

- entry trigger/referent;
- field(s);
- why it became interesting;
- source map;
- supported findings;
- connections/analogies clearly labeled;
- unresolved questions;
- branches followed/dropped;
- next possible dives;
- status: `seed`, `active`, `paused`, or `closed`.

## Money boundary

Do not optimize the dive for monetization unless the user explicitly changes the goal.

If a possible paid application appears, record it as a possible handoff candidate. It does not become a job until the money/jobs lane admits it under its own contract.

## Closure

A saved dive is valid input to `research.dive` later. Resume from the recorded active/next referent without reconstructing the entire exploration from chat memory.
