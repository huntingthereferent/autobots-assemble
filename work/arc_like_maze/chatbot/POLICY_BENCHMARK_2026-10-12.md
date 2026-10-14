# finite correspondence process policy benchmark — 2026-10-12

**Referent:** Does prioritizing already-witnessed rejected A/B-labeled transitions improve the next trial compared with fixed-order candidate search? Formal A and B are only particular finite transformations of 27 states, not a definition of A/B's language-level referent.

## Result: KEEP_FIXED_DEFAULT

Six explicitly selected finite old/new law and requested-goal fixtures, each run with fixed-order and conflict-guided trial selection under budgets 2, 3, and 4, for **18 paired comparisons / 36 completed local executions**. Each run used an independently pinned local snapshot and the same per-policy cap of 54 potential original and 54 potential changed A/B edge observations. Equal trial caps do not imply equal observed query counts.

| Measured comparison | Guided wins | Fixed wins | Ties |
|---|---:|---:|---:|
| Completed goals | 0 | 0 | 18 |
| Admitted edges in best fully replayed completed extension | 0 | 1 | 17 |
| Lower number of original + changed owner observations | 0 | 2 | 16 |

Cumulative per-run owner observations: **1,422 fixed; 1,426 guided**. These are sums over independent trial runs, not globally distinct observations. Guidance actually selected a conflict-targeted alternative in **12/18** comparisons, so it was not a no-op throughout.

Concrete controls:
- Original phi=(0,0,1), changed phi=(1,0,1), goals (0,1,0) and (0,1,1), trial cap 4: 2/2 goals for both, **42 fixed** vs **41 guided** admitted transitions; 108 observed owner transitions each.
- Original phi=(0,0,1), changed phi=(0,0,0), goals (0,1,1) and (0,2,0), caps 3 and 4: 2/2 goals and 13 admitted edges for both, but **44 fixed** vs **46 guided** observed transitions. Selected goal words coincide.

**Evidence:** The snapshot-backed local benchmark replayed every winning goal word and every admitted selected edge against independent finite law computations, also verifying partial pairing injectivity. It completed three separate budget segments. The combined and per-run machine-readable JSON are in the separate packaged correspondence process artifact `ab_chatbot_policy_benchmark_2026-10-12.zip` (SHA-256: `85bafe4f59d91b890453bcd468f4e538eb152640ecfe4a25d8ec598691385767`), 101 files, preserving all 91 predecessor files byte-for-byte. The full benchmarking implementation is in that package, not silently present in GitHub.

Local regression verification: 4 benchmark tests, 10 conflict-guidance, 25 post-extension portfolio, 12 seed-first extension, 15 union extension, 4 previous finite guidance = **70 passed across separately completed module runs**. A separate GitHub-file-style finite summary checker has **3 local tests** for row totals and independent replay of selected goal words. The larger historical suite and GitHub CI were not rerun/verified.

## Standalone GitHub checker

From this directory:

    python finite_policy_benchmark_record.py
    python -m unittest -q test_finite_policy_benchmark_record.py

This rechecks **recorded totals** and four finite goal-word outputs using `finite_goal_priority.py`; it does not rerun the full comparison or certify each benchmark observation. Do not promote a record checker into original execution evidence.

**Decision boundary:** Keep fixed candidate ordering as the implementation default. Conflict-guided selection remains available as an experimental alternative, including its replayable failure witnesses. This nonrandom six-fixture finite sample does not prove global ineffectiveness. Next warranted experiment is to use excluded edges to avoid incompatible candidates *before* paying more observation cost, then benchmark again on held-out finite goals with equally measured budgets.

This note does not change `state/current.json` or the separate Continuity default project.
