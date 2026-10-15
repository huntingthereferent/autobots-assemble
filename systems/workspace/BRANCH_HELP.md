# CP branch help — source-owned worker birth

**Referent:** one unfinished checkpoint can request help while preserving its existing source and native proof obligation. This is an extension of the existing Process Workstation, CoordinatorIndex and RuntimeJournal, not another scheduler.

When `GAME-W13-WORLDS` opens a need for a game-build worker, the opening remains `OPEN_UNSTAFFED` because no registered model-backed game-builder currently exists. The system **does not** pretend that an existing finite correspondence worker can implement a game engine.

When an opening requests a **registered finite required-edge prefilter**, `branch_help.py` can make an independent source-preserving `ProcessWorkstation.branch()`, call the existing `admit_finite` control exactly once, and append `HELP_ASSIGNED` to the same runtime journal as the unfinished CP. The native job stays READY until explicitly executed with `controls.run_job`, and then independently reverified through `controls.reverify_job`. `HELP_RETURNED` references the verified finite computation; it never marks the parent CP as witnessed. A future game-native adapter must separately consume relevant evidence to complete W13.

The parent need not be COMPLETE to open this bounded child: `HandoffRuntime.spawn()` intentionally requires a COMPLETE parent, so `branch_help` records a separate durable helper opening and assignment **without modifying the underlying handoff contract or forging a parent dependency**.

## Example — no workstation replacement

In a trusted, existing checkout, after `cp_motion admit-research` and a finite source edition `finite-correspondence-process/base` have been separately copied into `runtime/data/workstation`:

```bash
python -m systems.workspace.branch_help --data-dir runtime/data open \
  --lane game --slot cp-game-w13-worlds --key source-audit-1 \
  --capability game-engine-build --reason 'W13 needs a native game builder'
# This exposes OPEN_UNSTAFFED: game-building capability not registered.

python -m systems.workspace.branch_help --data-dir runtime/data open \
  --lane game --slot cp-game-w13-worlds --key finite-prefilter-check \
  --capability finite-required-edge-prefilter \
  --reason 'Run a bounded finite source correspondence preflight'
# For the second returned opening_id:
python -m systems.workspace.branch_help --data-dir runtime/data staff-finite \
  --opening-id ACTUAL_OPENING_ID --parent-version base --inputs-file finite-inputs.json
# The returned child job ID can be executed only through existing controls:
python -m systems.workspace.controls --data-dir runtime/data execute \
  --job-id ACTUAL_CHILD_JOB_ID --confirm-execute ACTUAL_CHILD_JOB_ID
python -m systems.workspace.branch_help --data-dir runtime/data return \
  --opening-id ACTUAL_OPENING_ID
python -m systems.workspace.branch_help --data-dir runtime/data status
```

`finite-inputs.json` must match the existing finite prefilter input schema. The helper's `NOT_CONTRADICTED` verdict **does not** prove an admitted edge or a game checkpoint. Never silently treat worker edition birth as model-agent activation or job completion.

The new helper operation is **invocation-driven**. Native source types and permissions must be explicitly registered to actually staff future GAME BUILD/WITNESS openings. No generic AI model invocation, automatic code generation, GitHub job execution, or autonomous multi-worker development loop is connected by this CP movement. The value is preserving a genuine, independently verified child relation before generalizing execution.

Reproduce with:

```bash
python -m unittest -v network.tests.test_branch_help
```