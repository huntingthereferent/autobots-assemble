# Inspector Gadget — Audit-to-Action worker lane

**Worker name:** Inspector Gadget.

Purpose: turn neutral audit observations into retained, typed records and independently actionable follow-ups. This is a **pipeline**, not a new research verdict or a requirement to change working results.

## Contract

1. **Ingest** a neutral audit as JSON findings with unique `id`, `lane`, `observation`, `source`, and `kind`.
2. **Classify without rewriting the observation**: `verified_result` → preserve; `defect` → investigate; `candidate` → verify; `unknown` → observe; `external_boundary` → record boundary.
3. **Keep source ownership**: a source locator is not source authentication. The output marks it `unverified_locator` until another worker checks the exact revision and witness.
4. **Activation = movement**: the scheduled scan converts candidate workflow incidents into bounded per-incident `HandoffRuntime` source-observation jobs; four named workflows also have immediate cancellation-triggered movement. These jobs independently read the pinned GitHub run and preserve a native runtime journal. They **do not automatically edit sources, rerun research, or repair an owning lane**.
5. **Close the loop**: after independent verification, retain the original observation, test receipt, outcome, and next source-owned continuation. Do not silently delete negative findings or convert successes into problems.

## Current intake

`python systems/workspace/audit_to_action.py input.json output.json`

Test: `python -m unittest discover -s network/tests -p 'test_audit_to_action.py' -v`

## Audit seed — 2026-10-22

These are observations from the GitHub account audit, **not yet authenticated by this lane's own test run**.

| ID | Lane | Kind | Observation | Next check |
| --- | --- | --- | --- | --- |
| A2A-001 | Mathematics | verified_result | Engine 1 and Cyclic Action have source-defined finite constructions and focused tests | Pin exact source/test revisions and retain witnesses |
| A2A-002 | ARC | verified_result | Recent ARC direct-observation workflows reported success | Inspect native outcomes separately from workflow status |
| A2A-003 | CI | candidate | Multiple protocol-test runs were concurrently in progress and Pages/publish runs were cancelled | Measure redundant triggers, useful completions, and queue latency before changing concurrency |
| A2A-004 | Profile | candidate | Overlapping introductions may confuse navigation | Compare entry pages against a single canonical source map |
| A2A-005 | Viewer | candidate | Execution counts, verified findings and throughput can be conflated | Compare live counters to source-owned run API and saved evidence |
| A2A-006 | UI | unknown | Browser usability of Meow Lab, Pony Trail, Audio Intake, school and viewer was not verified in this audit | Run browser tests and direct interaction checks by page |
| A2A-007 | Research | verified_result | Independent source adapters, observations and tests exist across scientific lanes | Verify each source receipt independently |

Do not infer a failure from an untested item. Do not collapse independently verified results into a global pass/fail score.

## Automatic observation

- `.github/workflows/audit-to-action-cancellations.yml` responds to cancellations in four explicitly listed workflows.
- `.github/workflows/inspector-gadget-all-workflows.yml` performs a repository-wide scan hourly (and via manual dispatch), retaining a grouped incident report as an Actions artifact.
- The scanner currently examines at most the newest 1,000 completed workflow runs and filters a two-hour window. At high volume, older runs in that window may be missed; a durable cursor/pagination expansion is still needed.
- An explicit activation plan admits up to 200 source-observation jobs per scan, with a recorded overflow count; outstanding signals are **not** represented as already processed. Inspector's own runs do not recursively activate more Inspector jobs.
- Each real follow-up uses `systems/workspace/inspector_gadget_adapter.py` and the existing `HandoffRuntime` (CREATED → STARTED → RESULT). It independently queries the exact GitHub run and retains `inspector-gadget-handoff.json` and `inspector-gadget-runtime.jsonl` as Actions artifacts. `systems/workspace/inspections.py` renders those records with the registered `inspector-gadget-github-run-v1` adapter when its journal is loaded into the local workstation viewer.
- These are CI observations, **not** a complete observer for browser interaction, source-level mathematical errors, or every workstation layer. The observer activates source verification, not the owning research worker or automatic repair. A source-matched `COMPLETE` means only that the Inspector's source observation completed.

## Native Lane Continuation — scheduled execution of registered workers

The existing hourly Inspector Gadget workflow now includes a **Native Lane
Continuation** job. It schedules eligible registered, source-owned GitHub
Actions workers without replacing their implementations. It is a dispatcher, not a new research
worker, new comparison prompt, or claim that another ChatGPT window ran.

- `systems/workspace/inspector_gadget_workers.json` lists the verified existing
  workflow entry points: ARC native, NIH P2 synthetic benchmark, WORLD
  construction, workstation B7, mathematical Engine 1, finite CP30, Meow
  Lab, Pony Trail, Audio Intake, research-source preflights and ARC source observation.
- At each calendar tick it reads
  each registered native workflow's own GitHub run history, refuses to
  duplicate active jobs, honors each existing worker's minimum cadence
  and starts up to four due workers using GitHub's native
  `workflow_dispatch` API with Actions write permission scoped to the
  `native-lane-continuation` job. Remaining due lanes are eligible at later ticks.
- A machine-readable artifact records SELECTED, ALREADY_RUNNING, COOLDOWN,
  DISABLED and CAPACITY_WAIT states, plus confirmed dispatch acceptances or
  failures. Receipt is not scientific proof or a completed worker result.
- The NIH synthetic benchmark only gained a dispatch trigger; it still
  executes the pre-existing owner workflow and its original verifiers.
- The registry does not enable private W13 worker execution, cross-node B
  transfers, arbitrary code edits or human/source authentication bypasses.
  GitHub Actions can start existing workflow jobs, but it cannot type
  messages into separate ChatGPT conversations.

**Boundary:** A repeat of an unchanged fixed-input test is a native
revalidation, not a new scientific hypothesis. Genuine research continuation
requires each source-owning worker to emit a concrete next admissible job
or frontier; Inspector only fires the registered executable entry point.

## Calendar observations — direct GitHub sources

GitHub Actions runs `.github/workflows/inspector-gadget-all-workflows.yml` hourly, without requiring a ChatGPT window.

- The Inspector scanner reads the original repository's GitHub Actions run API directly and records source-linked findings.
- Its bounded scan covers up to the newest 1,000 completed runs and applies a two-hour discovery window. It does **not** recover historical unresolved walls outside that window without a separate source investigation.
- `inspector_gadget_adapter.py matrix` turns the visible findings into independently verified HandoffRuntime source checks. Inaccessible source data is not interpreted as proof that no failures occurred.
- Registered native worker dispatches use each owner's own GitHub Actions run history to prevent duplicate active work and enforce cadence. They do not depend on the former cross-repository Meta observation collector.
- Artifacts and owning research evidence remain separate from the status of the GitHub workflow itself.

## The actual wall — backward chase

The target is not a red counter or just a failed workflow. The wall is a concrete
**owning-workflow obligation**:

- Locate the original run, failing job and failed step when GitHub provides them.
  A cancellation is a separate supersession question, not a defect.
- Work backward from a potential exit: a later run of the *same workflow, branch
  and event* must execute the **same named job and step** successfully.
  An unrelated green run never clears the wall.
- Every real source-observation handoff uses `inspector_gadget_wall.py` to
  read failed job evidence, recent workflow history and, where present, the
  matching later passing job. The handoff saves its wall and next movement.
- The viewer shows the wall and failed step. A matched later step becomes
  `obligation_pass_observed`, **not** an automatic research verdict or repair.
  Independent verification by the owning lane remains required.
- The newest 100 workflow runs and 100 jobs bound each observation; this
  is not a complete history. The hourly scan does not retain a multi-day backlog after its discovery window expires. No automatic
  retry, source edits or authentication of external owner evidence occurs.

## Next implementation boundary

Next: persist and resume wall cases across scan cycles after the discovery window, with retry budgets and evidence-bound closure; durable pagination with a time cursor; an owning-lane registry for verified issue→follow-up-worker dispatch; capture native research and browser failures independently of CI; ingest retained Inspector runtime journals into the deployed audit viewer; and link verified later fixes back to source incidents. Keep the original audit snapshot immutable.
