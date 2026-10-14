# Correspondence Worker — explicit, source-pinned first job

This adapter makes **one** Finite Correspondence Process computation available through the existing `HandoffRuntime`, `RuntimeJournal`, and Process Workstation. It is not a new agent scheduler and does not redefine the research subject.

## What is actually connected

```text
source-owned finite modules (unchanged)
  → ProcessWorkstation.copy_source(...)       # selected version in private state
  → CorrespondenceWorkBridge.admit(...)       # explicit bounded handoff (READY)
  → CorrespondenceWorkBridge.execute(..., allow_local_execution=True)
  → local subprocess imports that exact selected edition
  → finite_required_edge_guard.preflight(...)
  → independent verifier recomputes finite mathematical verdicts
  → native HandoffRuntime RESULT + witness + durable journal
  → reverify(...) after RuntimeJournal restart
```

The first supported operation is **finite required-edge prefilter** under declared `Law` operators. Inputs are two F3 triples describing laws, a bounded set of candidate seed words, a required state and an A/B action. Output is one of `CONTRADICTED`, `NOT_CONTRADICTED`, or `UNDECIDED` per candidate. **`NOT_CONTRADICTED` is not evidence that an edge was admitted.** `COMPLETE` means the **prefilter computation** returned the independently replayed result, not that a mathematical correspondence or external task was solved.

The bridge does not have to duplicate the 281-file owner-backed CP-0030 archive to demonstrate this narrow operation. It uses the **actual two published standalone finite source modules** from [Finite Correspondence Research](../../work/arc_like_maze/chatbot/README.md) copied into a local, named edition. These standalone modules do not claim CP-0030's independent source-identity attestation or owner-backed route audit.

## Boundaries

- Copying or branching a worker creates **no** handoff. `admit` is explicit and `execute` requires `allow_local_execution=True`.
- The bridge binds job and reported result to the selected worker **version and full current source fingerprint**; editing files after admission invalidates execution and verification.
- The native verifier implements the finite transition and seed-consistency check independently of the **worker edition** and fails closed before a `RESULT` can enter the journal if the copied code returns a wrong verdict.
- A subprocess executes selected local Python. `-I` limits ordinary interpreter path injection but does **not** sandbox that Python source. Only deliberately selected/trusted local editions may execute. Do not expose this as an untrusted uploaded-code service.
- A PID is a local observed process marker, **not authentication of worker identity**. Native mathematical replay is not cryptographic or human-identity verification.
- An execution failure may leave the handoff `ACTIVE` after `STARTED`; it is not marked `COMPLETE`. Retrying requires an explicit recovery decision using the existing runtime, not an automatic duplicate.
- The bridge does not automatically integrate source branches into the research repository, create new CPs, change any other lane, register with `EcosystemService` on startup, operate physical devices, or launch an autonomous agent loop.
- The `RuntimeJournal` stores a durable exact handoff and result. `reverify` checks a restored `COMPLETE` against the **current selected local edition** without rerunning code. A missing or changed edition invalidates that check.
- Local journal writes and process-copy operations are not concurrent-multiprocess-safe or a security boundary. Run in an authorized local environment.

## Reproduction

From the repository root, with Python 3.12+:

```bash
python -m unittest -v network.tests.test_correspondence_worker_handoff
python -m runtime.examples.correspondence_worker
```

Both explicitly use locally copied source editions, not the original public source folder as writable workspace. The tests exercise the actual `HandoffRuntime` and its journal, native finite verifier, child subprocess, restart, independent branching, unsupported output, altered source, and refusal of implicit activation.

**Next movement:** expose this existing handoff and worker-edition state in the workspace GUI as a read-only process station. Broader goal-directed and owner-backed operations require separate adapters with their own native evidence contracts before being admitted.
