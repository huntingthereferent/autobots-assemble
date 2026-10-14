# Source comparison and preferred worker editions

The Process Workstation preserves original sources and all previous working copies.
**A preferred edition is an explicit selection for future separately admitted work,**
not a software deployment, merge to the research, general worker upgrade, or
proof inherited from another source copy.

## Exact steps

1. Compare two working editions by the hashes of their **current files**:

   ```sh
   python -m systems.workspace.controls --data-dir runtime/data compare --worker finite-correspondence-process --left-version baseline-001 --right-version experiment-001
   ```

   The report distinguishes modified, added, removed and unchanged files and
   records both source fingerprints. It never reads or upgrades checkpoint test
   claims. A file may differ without its behavior differing, and vice versa.

2. Admit a **new bounded job on the exact candidate edition**, explicitly execute
   it through the existing native adapter, then reverify it. A different edition's
   result cannot support selection. In this first implementation, supported jobs
   are the finite required-edge prefilter and Factory machine-stage simulation.

3. Explicitly record the preferred version using its **entire current fingerprint**
   and exact supporting job. Example (replace placeholders with actual IDs and hash):

   ```sh
   python -m systems.workspace.controls --data-dir runtime/data promote --worker finite-correspondence-process --version experiment-001 --supporting-job NEW-COMPLETED-JOB --confirm-version experiment-001 --confirm-fingerprint FULL-64-CHAR-EDITION-SHA256 --actor local-operator
   ```

4. Inspect the local preference without running anything:

   ```sh
   python -m systems.workspace.controls --data-dir runtime/data preferred
   ```

The local ledger `runtime/data/preferred_editions.jsonl` is append-only, with
selection ancestry and supporting exact job IDs. An existing selection is not
overwritten; choosing another version appends a new event. Reading the ledger
checks its structure and parent links and fails on malformed history. It is not
cryptographic proof of local operator identity or concurrency-safe multiuser state.

## Native evidence boundary

At selection time, the original source-owned verifier rechecks the stored job
without executing the worker again. The job must be COMPLETE and pinned to
the **same worker ID, version and current source fingerprint**. Factory evidence
remains simulated; a finite prefilter verdict remains bounded to its one check.
The preference is scoped to the supporting job's required relation, not all
work that this worker might eventually do.

After selection, changing source makes the read-only projection report
`SOURCE_CHANGED`. It never silently selects a fallback or changes previously
admitted handoffs. Source trees, research history, CP evidence, and previously
completed jobs remain untouched. Existing job admission still requires an
explicit selected version; selection itself admits and executes **zero** jobs.
The browser remains GET-only and merely displays commands for local review.
