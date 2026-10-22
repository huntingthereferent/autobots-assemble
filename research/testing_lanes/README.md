# Research test lanes — candidate catalog (2026-10-22)

This registry extends the existing research goal lane with separately resumable **test contexts**. It does not assert that every study has been read, that a dataset has been imported, or that any experiment has passed. The sources are official discovery entry points, not downloaded studies.

The catalog is [registry.json](registry.json); [lane_registry.py](lane_registry.py) validates it and generates bounded, unobserved plans. The catalog currently has 21 candidate contexts and 18 documented source families. Every context has its own question, measurement, counterexample and candidate source list. No category is privileged.

The sibling question is **what test context is needed for the present referent?** A domain tag in this list is not a new foundation/capability or proof of a universal mechanism. When a real question crosses disciplines, the evidence stays attached to the same referent and can link multiple source contexts without duplicating the original witness.

## Why there are separate objects

- **Source index / bibliography:** where one might discover relevant research. A catalog listing alone is not evidence.
- **Study or protocol:** a specific dated record, registered design or published claim, pinned by stable ID and version.
- **Dataset / data release:** an actual input artifact with access conditions, schema, collection conditions and checksums.
- **Executable experiment:** a frozen code revision, environment, baseline, measured output and negative cases.
- **Witness:** actual observed result with exact scope; only this can advance the demonstrated depth.
- **Interpretation:** possible relationships that remain separate from the observation.

Do not infer that a paper's conclusion was reproduced because its metadata was indexed. A new result must preserve what would falsify the claim, not just report a favorable number.

## Admission process

1. Choose one registered testing context from the current research question; no automatic bulk harvest.
2. Identify a specific study or dataset; record DOI/registration/data ID, publisher/source, release/version, retrieval time UTC and original URL.
3. Check access conditions, copyright/license, ethics/privacy, credential requirements and whether data are experimental, observational or synthetic.
4. Freeze relevant claim, methods, expected observation, independent baseline and counterexample before running code.
5. Record code commit, inputs and outputs hashes, environment, sample selection, errors/uncertainty, negative cases and what remained unknowable.
6. Put full experiment results under the existing work/research paths where the actual work belongs. Put exploratory context in `research/dives/`; keep immutable question snapshots in `research/questions/`.
7. Promote a lane from `candidate` only with source-specific receipts; `tested` additionally requires an actual reproducible experiment and a linked witness. A catalog validator is **not** a scientific test.

Clinical-trial registration does not establish efficacy. A model trained or evaluated on public data does not establish validity in human subjects. Simulated movement is not hardware measurement. Observational correlation is not causation. Security exploration is restricted to authorized local/synthetic targets.

## Workstation interface

This is an offline, versioned adapter suitable for workstation handoff; it performs no network requests and never silently populates test outcomes.

```sh
python research/testing_lanes/lane_registry.py check
python research/testing_lanes/lane_registry.py list
python research/testing_lanes/lane_registry.py plan CLIN
python -m unittest discover -s research/testing_lanes -p 'test_*.py' -v
```

A generated plan has `status: UNOBSERVED`, blank source receipt slots and `UNKNOWN` experiment outcome. A later source-specific collector must implement the provider's documented API, respect access rights and rate limits, and produce a verifiable receipt. This PR does **not** build those collectors, schedule live fetches or claim external benchmark outcomes.

## Relationship to existing work

- Existing [research dives](../dives/) remain the home for source-driven investigation.
- Existing [question checkpoints](../questions/) remain the versioned question/answer boundary.
- ARC, NIH, WORLD, cat keyboard/audio, game worlds and other projects keep their own native experiments.
- A testing context can be used by one or several existing projects, without overwriting their records or equating their evidence.
- The existing category contract still governs decomposition: do not flatten goal, dependency, artifact type and witness depth into one hierarchy.

## Safe expansion

When introducing a source family, add its **official documentation**, scope, access boundary and relevant test context. When adding a new test context, include one concrete measurement and a real failure/counterexample condition. Keep rights unresolved until checked **for a specific record**. Do not upload protected human records, bypass access controls, or run third-party security tests.

This catalog intentionally has no claims of source data ingestion or scientific confirmation.
