# Trending source swallow → actual native A/B movement

Source inspection, 2026-10-19. Four cross-field references were compared to
the already implemented **A/B** native workstation and `witnessed_frontier.py`.
This is a *selected* swallow, not a claim to have implemented entire trending
repositories.

## What was missing, based on real source

A/B already had:
- registered finite worker editions and source SHA-256 pins;
- explicit native job admission/execution and independent replay;
- a multi-task Pareto-frontier comparator taking `Trial` receipts.

**The gap was between them:** the frontier's contract tests used only
synthetic callbacks. An admitted source-owned completed worker could not yet
be passed through that comparison without manually inventing/copying a
`Trial`, score, fingerprint and witness reference.

Examined trending repositories at their actual source:
- [pollen-robotics/microduck, `duck-control/src/safety.rs`](https://github.com/pollen-robotics/microduck/blob/main/duck-control/src/safety.rs) (Apache-2.0): only the authority that owns the hardware output handle may command the motors. Distinguish observer clients from output/actuator authority. **Retained boundary:** this new adapter never invokes `run_job` or bypasses `controls`. Existing exact-ID execution control remains separate.
- [dolthub/dolt, `go/libraries/doltcore/merge/merge.go`](https://github.com/dolthub/dolt/blob/main/go/libraries/doltcore/merge/merge.go) (Apache-2.0): schema and data conflicts are explicit before combining versioned states. **Retained boundary:** a fixed task's input digest/metric must match across source editions, otherwise refuse the comparison rather than silently selecting a winner.
- [gitleaks/gitleaks, `detect/baseline.go`](https://github.com/gitleaks/gitleaks/blob/master/detect/baseline.go) (MIT): an existing finding is compared against its concrete baseline identity before treating it as novel. **Retained boundary:** replay *the same exact* journaled job/source/result, never credit a reused job to another edition.
- [CliMA/Oceananigans.jl, `src/TimeSteppers/TimeSteppers.jl`](https://github.com/CliMA/Oceananigans.jl/blob/main/src/TimeSteppers/TimeSteppers.jl) (MIT): source-specific time-stepping state and restoration differ from generic orchestration. No numerical time step is justified for A/B finite prefilter, so **no import** into the workstation. Physics belongs to a separate experiment.

These are **bounded observations and design constraints**, not claims that
Dolt/Gitleaks/microduck source code was reused. The Python implementation
is original A/B and depends only on existing project modules.

## Implemented move

`systems/workspace/native_frontier.py` bridges the *actual* native finite
correspondence worker's recorded `COMPLETE` results into the existing
`witnessed_frontier` evaluator. The move is:

1. Select explicit, existing `(candidate, task_id, job_id)` locators.
2. Inspect exact native job metadata, edition/source pin, and journaled output.
   Reject READY, fabricated, foreign worker, missing, or changed-source jobs.
3. Reverify each job using the **existing native domain verifier**, without
   executing again. Independently recalculate the domain prefilter's verdicts
   from its original admitted input and compare to the retained native output.
4. Score only **decision coverage**: the number of native verdicts that are
   `CONTRADICTED` or `NOT_CONTRADICTED`. `UNDECIDED` contributes zero
   to this **descriptive** count. It is *not* a proof of true correspondence,
   quality, safe physical movement, or predictive accuracy.
5. Send the rechecked receipts through the existing bounded multi-task
   frontier; retain source provenance and multiple nondominated editions.
   Neither pin an edition nor construct/execute any new worker.

`score_witness` names the original job and a digest of the **recomputed
source-free finite oracle**; it is not an external independent human
attestation. Native verification and source check remain mandatory.
Scores measure only the exact declared task inputs and current source
editions.

## Reproduce actual workers

```bash
python -m unittest -v network.tests.test_native_frontier
```

The new tests use isolated temporary data, run *four real source-owned local
finite worker subprocesses* on two source editions and two exact tasks,
and then independently reverify their journal results. Additional negatives
check unexecuted READY jobs, changed native source, source/test input mismatch
and duplicate/native-invented jobs. They assert no new execution, journal
append or edition promotion takes place **during frontier evaluation**.

Use the read-only CLI for previously executed jobs:

```json
{
  "required_tasks": ["task-one", "task-two"],
  "cases": [
    {"candidate": "base", "task_id": "task-one", "job_id": "existing-native-job-1"},
    {"candidate": "base", "task_id": "task-two", "job_id": "existing-native-job-2"},
    {"candidate": "other", "task_id": "task-one", "job_id": "existing-native-job-3"},
    {"candidate": "other", "task_id": "task-two", "job_id": "existing-native-job-4"}
  ]
}
```

```bash
python -m systems.workspace.native_frontier --data-dir ./private \
  --manifest ./existing-native-cases.json
```

Jobs in that example are **placeholders**, not claimed existing IDs.
The CLI cannot run anything. It refuses unsupported domains rather than
pretending that all workers have the finite prefilter's measurement semantics.

## Not swallowed

No second agent harness, planner, robotics motor control, versioned SQL
database, secrets scanner, ocean solver, model trainer, new network access
or dependency. No source or license copied. The original owner-driven
research/workers, WORLD simulation, ARC and NIH lanes remain unchanged.

This is a real improvement in the **ability to compare already executed
native jobs**, not evidence that one research branch is scientifically
better than another.
