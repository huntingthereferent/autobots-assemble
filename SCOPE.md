# Scope

Scope is controlled by the **current referent**, not by a permanent job/category boundary.

## Preferred referent

The authoritative current referent is the **user's explicit request in the active conversation**, interpreted with [ENTRY.md](ENTRY.md). Do not replace it with a historical repository pointer.

[state/current.json](state/current.json) is retained historical source evidence (`status: historical`), **not a current work queue or default next movement**. A source-specific work record may preserve its own preferred referent and its own historical next step, but neither can silently supersede the active request.

## Complete-stack ordering

For any active problem:

1. current referent;
2. relations actually required by that referent;
3. immediate supported movement;
4. dependency layers opened by that movement;
5. evidence / witness / placeholder state;
6. next valid movement;
7. older evidence only when reached.

## Scope expansion

Entering another field is **not scope drift** when the current problem actually depends on it.

Example:

```text
vehicle control problem
→ motor torque requirement
→ mechanics
→ electrical power requirement
→ electronics
→ heat rejection requirement
→ thermal/material layer
```

Those layers remain in scope because the referent reaches them.

Scope drift occurs when a branch is added only because it is interesting or available and does not support the current relation.

## Evidence boundary

Never hide a missing dependency by naming a stronger completion state.

Use an explicit wall or bounded placeholder when necessary.

## External job records

The old `jobs/` listing directory and income scoreboards were retired. They remain recoverable from Git history, not from the current work tree. Paid requests, experiments, mathematical investigations and source corrections are all *work*; admission, verification and continuation depend on native evidence rather than an income category. Do not regenerate deleted listings or overwrite [TASKS.md](TASKS.md) from historical files.
