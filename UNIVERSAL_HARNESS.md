# Universal harness — retention and regrounding

Design baseline, 2026-10-23. Not an executed REA benchmark.

The universal harness compares independently executed implementations on the same defined input and wall. Dual: original native operation and Tracework A/B observation. Triad: add an independently executing Tracework-native reconstruction. Reuse existing handoff, evidence, provenance and worker systems; do not create a parallel framework.

Every operation records source/revision, referent, input, state transitions, preserved relations, native evidence, exact walls, unresolved unknowns, counterexamples and the next discriminating test. Preserve earlier walls append-only. Unknown is not failure; repetition without new evidence is not progress.

After each trial reground to the original referent and last verified state. Retain only the evidence sufficient to specify inputs/outputs, transitions/invariants, dependencies and an independent distinguishing test for the operation. When sufficient, construct the missing native capability; when insufficient, test the blocking unknown. Remaining nonblocking unknowns stay open. Retention sufficiency does not establish correctness.

Anti-drift uses this same retention record: compare each proposed continuation against the retained referent, source, operation, authorization, witnesses, walls and unknowns. If changed without support, mark the difference and reground rather than silently substitute a new goal. Preserve useful verified findings from detours. Applies to AI correspondence, worker lanes, packaging, source analysis and other research contexts. This is a shared method, not a claim of universal proven capability.

Related: [Tracework](TRACEWORK.md), [Regrounding](language/REGROUNDING.md), [Human Drift](language/HUMAN_DRIFT.md), [Runtime](runtime/README.md).
