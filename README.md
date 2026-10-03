# Language Network

Task/work reference repository for bounded external jobs and technical experiments.

## Review the jobs

**[Start with the Job Index →](JOBS.md)**

The job index is meant to be browsed. Click any job title to open its human-readable record. Each job record has **Previous / Job Index / Next** navigation so you can move through the queue in order.

- [Current task view](TASKS.md)
- [Full job ledger](JOBS.md)
- [Evidence/output index](OUTPUTS.md)
- [Scope rules](SCOPE.md)

## Canonical records

Each job is stored under `jobs/JOB-###_slug/` with a `job.json` record and a human-readable `JOB.md` summary. The JSON record tracks status, scope, acceptance conditions, evidence, submission state, payment state, and next action.

## Generated views

Run `python generate_outputs.py` to regenerate job, task, resume, portfolio, summary, and JSON snapshot views from the current `job.json` records.

## Repository snapshot

This import corresponds to the packaged v0.17 task-manager snapshot. Large generated binary artifacts are kept out of normal Git source control; see [BINARY_ARTIFACTS.md](BINARY_ARTIFACTS.md).
