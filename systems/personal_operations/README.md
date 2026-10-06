# Personal Operations

Personal Operations is the local note/task/plan system connected to the shared handoff runtime.

It deliberately keeps four things separate:

```text
NOTE
observation / remembered context
        ≠
PLAN
intended organization / possible sequence
        ≠
TASK
explicit executable work record
        ≠
HANDOFF
task admitted across a runtime boundary
```

## Movement

```text
note ──┐
       ├─ may inform → plan
       ├─ may inform → task
       └─ remains a note unless a supported movement changes it

plan ──→ may produce explicit tasks
task ──→ explicit admission → shared handoff
handoff result ──→ later reconciliation back into Personal Operations
```

Nothing automatically promotes itself merely because it exists.

## Why

A note-taking system should be able to remember:

> School printer paper is getting low.

without silently creating:

> James must buy printer paper today.

That task requires another supported movement.

Likewise, a plan can contain possible steps without those steps automatically appearing in a person's active queue.

## James / ohayo

James's `ohayo` activation does not read notes/plans directly.

It sees **live handoffs assigned to James**.

Therefore:

```text
Personal Operations task
→ explicit admit_task(...)
→ Handoff(to_actor="james")
→ runtime
→ ohayo selector
→ James task projection
```

Other systems can emit handoffs assigned to James too. The activation does not care whether they originated in Personal Operations, Online School, a company, software, or another system.

## Persistence

`PersonalOperationsStore(path)` writes append-only JSONL events when a path is supplied.

Private live data should remain outside Git. The repository contains the implementation/contracts/tests, not the household's private notes and task history.
