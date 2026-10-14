# Completed extension portfolio — 2026-10-12

## Current referent

Compare several independently completed rooted finite A/B extension results before choosing how to continue. A/B denotes the existing **bounded mathematical generators** here, not A/B's original language-level referent or any observed physical coupling.

## New local implementation

- `ab_chatbot_extension_portfolio.py` combines existing completed `BacktrackedGoalExtender` results; it does not rebuild the solver.
- Requires the same pinned source objects and roots; replays every candidate with a **zero-observation audit** before reuse.
- Exact nonempty powerset selection on **at most 8 supplied candidates**, scored by number of goals carried first, then admitted edges, paired states, fewer selected candidates.
- Shared state images must agree, target mapping remains injective, all admitted edges must agree. Any conflicting pair returns a replayable word-equality witness distinguishing the two finite systems.
- Preserves distinct goal images across alternative subsets with maximal goal coverage, even when those subsets cannot be merged.
- Does not mislabel incomplete, repinned, tampered, or remote-reported source evidence as locally witnessed completion.

## Verified finite example

Old `phi=(0,0,1)`, new `phi=(0,0,0)`, same root `(0,0,0)`.

| Independent completed candidate | Declared goal | Admitted paired states | Admitted edges |
|---|---|---:|---:|
| Candidate 0 | `(0,1,0)` | 9 | 15 |
| Candidate 1 | `(0,1,1)` | 9 | 12 |

The two full pairings cannot be joined; there is an exact target-image collision. The selected portfolio carries 1 of the 2 requested goals, with 2 compatible nonempty subsets (the two singletons). No claim is made that either original goal is globally unreachable or that no other correspondence could carry both.

Under identical laws `(0,0,1)` against `(0,0,1)`, compatible completed candidates each cover all 27 paired states and 54 edges; selection carries 2/2 goals and does not fabricate extra coverage from the redundant merge.

## Evidence and reproduction

Run from the extracted directory:

```sh
python -m unittest -q test_ab_chatbot_extension_portfolio
python run_extension_portfolio_demo.py
```

The 10 new focused tests passed (independent reference scoring across three rule pairs, replay checks, collision witness, compatible selection, no-new-read, stale-version, tampered edge, incomplete, remote status, invalid-input checks). The older `test_ab_chatbot_backtracked_extension` module passed 9 tests and `test_ab_chatbot_path_union` passed 15 tests in separate reruns. A combined regression attempt stalled; it is not counted as a full pass. The 330-test result belongs to the **preceding** unchanged version and is not relabeled as a new full-suite result.

## Wall and next referent

These completed extensions are chosen greedy partial extensions, not a global maximum, and the sample conflicts. A fuller agent must compare *different compatible seed unions before their greedy closure* if it wants to exploit relationships that finished individual extensions cannot join. That would require a separate experiment and new witnesses, not silent promotion of the current comparison.

The standalone GitHub research witnesses record this boundary; the full local integrated package remains a separate archive unless explicitly committed in full. GitHub's `state/current.json` belongs to a different current Continuity referent and remains unchanged.
