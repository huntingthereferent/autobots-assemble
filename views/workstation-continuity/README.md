# Workstation continuity — native source for visuals

[← All views](../README.md) · [Process Workstation](../../systems/workspace/WORKSTATION.md) · [Native monitor](../../systems/workspace/monitor.py)

This is the **source → validate → render** adapter for the workstation that copies and branches process editions, records source edits, and passes admitted jobs to native controls. The rendering code is **not** an alternative workstation, a model-worker spawner, or a replacement for `RuntimeJournal`.

## What it draws

- Recorded editions, parent versions, and a count of actual added / modified / deleted source files, read from `ProcessWorkstation.inspect` through the existing `workstation_snapshot`.
- Native admitted job IDs and recorded status, with a conspicuous `recorded-not-reverified` distinction.
- An edition-to-parent edge **only if** the original parent edition exists in the source's current read-only snapshot.

No invented tasks, successful jobs, runtime health or cross-domain correspondence appears in the view. The source count and files come from the *actual edited editions* rather than graphical embellishment. The projected JSON deliberately omits source code, filenames, private paths, job inputs, output payloads, witness bodies and private runtime events.

## Generate on an authorized machine

From the research repository root, where the workstation already has private state:

```sh
python -m unittest discover -s views/workstation-continuity -p 'test_*.py' -v
python views/workstation-continuity/render.py \
  --data-dir runtime/data \
  --out-dir runtime/data/workstation-visual
```

This **reads** the original native monitor and journals. It neither admits nor executes worker tasks. The output is stored under private `runtime/data` and must be reviewed before any public use; the code does **not** upload or commit it. Running it with no native worker edition or journal fails instead of fabricating a dashboard.

## What still requires implementation

The current workstation supports explicit source copies, branches, native job admission and bounded, source-verified subprocess execution. An automatically running code-editing worker fleet is **not** demonstrated by the profile renderer. To make a rUv-like public visual driven by genuine edits, a separate approved export must securely publish a bounded snapshot after a verified worker execution, and the profile repository must regenerate from that exact source. This cannot be replaced with a fabricated worker graph or by guessing from GitHub commit counts.

The finite A/B mathematical frontier and the workshop's human-language referent stay distinct; they may be shown alongside native evidence, but a graph line never authenticates a cross-system relationship.
