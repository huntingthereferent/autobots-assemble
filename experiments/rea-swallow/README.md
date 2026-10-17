# Swallow REA — first A/B real-source experiment

Original: [morluto/rea](https://github.com/morluto/rea), MIT license; complete git submodule pinned at `f0b9ef34c404c1c65f8167502db972b0bd708403` in `upstream/`.

This **actually changes REA source** in a temporary CI runner, not a drawing or JSON wrapper. The existing `ProcessWorkstation` copies a bounded upstream source slice into a `control` edition and branches an `experimental` edition. The first transformation replaces the indexed traversal of a growing queue with JavaScript's direct mutable-array iteration. The intended mathematical invariant is the same directed reachability closure and exact deterministic predecessor/edge behavior.

The pinned original and changed REA run the **same** upstream Vitest tests and an independent finite closure oracle across all 64 three-node directed loop-free graphs, 8 seed subsets, both seed orders, and 3 orientations = 3072 cases. Native run results, byte-for-byte comparison and source diff are published as GitHub Actions artifacts. No performance improvements or global mathematical equivalence are asserted without evidence.

The full original REA remains intact as the pinned submodule, because ProcessWorkstation's per-edition 2,000-file/50MB budget doesn't necessarily fit the whole repo. The selected source is what the workstation versions. `main` stays untouched; failed tests remain failures.
