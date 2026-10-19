# Use the A/B tool in existing native workers

This branch connects the **real packaged A/B source/provenance tool** from the
Swallow Repo stack to the existing Continuity agent pool. It does not add a
new bot, a second scheduler, or another implementation of inverse F3 mathematics.

The source is the [A/B Swallow Repo tool](../tools/ab-provenance/README.md),
not a wrapper over the old finite correspondence process.
The A/B tool's tested initial domain is actual pinned REA JavaScript source
investigation. Its provenance graph and bounded backwards ancestry are
separate, read-only exported capabilities.

## Actual integration

`runtime/ab_tool_worker.py` imports **ab_prov.build_graph**, **graph_summary**
and **ab_prov.ancestry.ancestors** directly from the installable A/B package.
It reads only source references produced by the original native evaluator,
reopens each referenced repository file, checks its SHA-256, rejects unsafe
or missing files, and builds a scope-preserving A/B graph. References shared
between two bot tasks remain shared in the graph.

`ContinuityPoolEvaluator` now accepts optional `ab_tool`. It still performs
the existing native ABLoop and swallow-first search inside the original
AgentLineage.evaluate callback. The installed A/B tool attaches a namespaced
`ab_tool_worker` provenance graph to the **same** nonterminal observation.
It does not change the three task IDs, task state, worker admission, model
registration, or James's separate queue.

The adapter is reusable by other source-owning workers that have bounded,
already-recorded source-reference pairs. It is **not** a general algorithm
that discovers arbitrary source meaning.

## Native journal inspection across Workstation worker families

The same adapter exposes `ABToolWorkerBridge.inspect_native_journal(path, target=...)`.
A trusted local caller explicitly supplies an existing `RuntimeJournal` JSONL
path; the installed A/B package parses its original submissions, events,
evidence locators and event parent links. An exact event or source target can
be selected for bounded A/B ancestry inspection.

This **reads** existing job evidence without starting another agent, replaying
a verifier, changing an edition, or changing a journal. A typed provenance
projection is not fresh evidence of task success. Workstation jobs retain
their original native owner and their own separate verification gates.

## Start locally (explicit opt-in)

Install the actual tool from the adjacent Swallow Repo source, then start the
existing authorized local Continuity service with this additional capability:

```bash
python -m pip install ./tools/ab-provenance
CONTINUITY_AGENT_POOL=1 AB_TOOL_WORKERS=1 HOST=127.0.0.1 \
  python -m runtime.http_server
```

The service explicitly rejects the A/B tool worker flag when the native pool
isn't active. It does not enable remote execution or import private journals
into the public website. Previous recorded events remain historical; enabling
the adapter does **not** retroactively rewrite a past source evaluation.
An already-evaluated pool won't rerun merely because the integration changed.

## Evidence and rights boundaries

- Exact source digest equality establishes that bytes match the recorded
  source. It does not prove that the source implements or completes the task.
- The A/B graph marks these relations as **referenced**, never independently
  verified. Its ancestry does not manufacture missing evidence or closure.
- Missing, mutated, escaping or invalid source references leave `UNKNOWN`;
  the existing worker's stale source evidence is not retained.
- Source correction/experiments via `ab swallow repo` remain an **independent,
  explicit native source-edition operation** with upstream REA pinned source,
  upstream tests, original licenses, and separately admitted execution.
  Enabling the bot's source observer does **not** grant source-edit permissions.
- Original REA MIT files retain upstream terms; original A/B code remains
  under A/B's All Rights Reserved license. No upstream files or licenses are
  redistributed through this adapter.
- This is local opt-in integration, not a hosted subscription tenant boundary,
  an autonomous coding agent, or a claim of full REA product parity.

## Native regression

```bash
python -m pip install ./tools/ab-provenance
python -m unittest -v \
  network.tests.test_ab_tool_native_workers \
  network.tests.test_pool_evaluator \
  network.tests.test_continuity_pool_runtime \
  network.tests.test_combined_evaluator
```

The GitHub Action `ab-tool-native-workers.yml` checks the actual installed
package with the existing native Continuity workers. It does not execute the
REA source-changing experiment; the source-edition A/B tool has separate
native/source-parity CI.
