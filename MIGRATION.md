# Migration — v0.17 task environment → A/B-constrained Continuity Layer

## Why the repository changed

The v0.17 package had already accumulated useful pieces of the intended system: preferred referents, append-only relations, output views, domain policies, jobs, tests, evidence, and generated task views. GitHub was initially populated as a thin job index, which hid too much of that shape.

The rebuild makes the **protocol/network layer primary** and keeps jobs as one application layer.

## Preserved

- all 21 canonical \`jobs/*/job.json\` records;
- all 21 human-readable \`JOB.md\` records;
- browse navigation between jobs;
- the frozen v0.17 archive as historical evidence;
- the archive SHA-256 and file-count boundary;
- old task/scope semantics as compatibility evidence;
- status integrity: tested ≠ submitted ≠ accepted ≠ paid.

## Added

- explicit A/B boundary document;
- AI entry protocol;
- reusable referent/evidence/movement/wall/handoff/provenance protocols;
- AI session and repository-write protocols;
- job-hunt, OSINT, and external bounded-work protocols;
- append-only relation runtime with evidence/parent provenance;
- protocol runtime with MOVE/WALL/UNKNOWN/PARTIAL states;
- adapter that projects existing job records into the same protocol contract without rewriting them;
- protocol-aware task view and work-state summary;
- closure/wall/unknown tests.

## Frozen archive boundary

The original package is:

\`ab_language_network_v0_17.zip\`

SHA-256:

\`21dda01da3c932d7ad32ab92e90ea4414669df296bac5af6fdced05c67189040\`

It contains 185 files: 152 text/source files and 33 binary files.

The frozen package remains evidence. It is not allowed to silently orient the active network.

## Remaining migration rule

When older source/artifacts are needed, recover them from the frozen package by relation from the current referent. Do not bulk-promote the archive back into the active layer merely because it exists.
