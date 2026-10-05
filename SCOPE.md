# Scope

Scope is controlled by the **current referent**, not by a permanent job/category boundary.

## Preferred referent

The canonical current routing pointer is [state/current.json](state/current.json).

A concrete work record may also preserve its own preferred referent.

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

## Legacy job records

`jobs/` remains a durable paid-work record set.

It is no longer the repository-wide scope model.
