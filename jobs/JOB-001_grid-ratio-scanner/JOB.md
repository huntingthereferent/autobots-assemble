# JOB-001 — 3×3 Grid Ratio Scanner

## Identity

- **Job ID:** JOB-001
- **Category:** external_bounded_problem
- **Source:** Freelancer
- **Source URL:** https://www.freelancer.com/contest/times-grid-ratio-scanner-2753812
- **Reward observed:** $100
- **Date added:** 2026-10-03
- **Status:** tested
- **Submission:** not_submitted

## Scope

- **📍 External 3×3 Grid Ratio Scanner specification**
- **Boundary:** Rolling last 16 supplied tokens; ignore P in counting; compare A–F+digit tokens against X; update numeric percentages and live graphic after every movement.
- **Acceptance:** Local regression suite plus independent 22-movement replay.
- **Next movement:** Keep as benchmark/reference; only reopen for submission if a matching opportunity is available.

## Result

PASS — 5/5 automated tests; 22/22 independent movement checks.

## Evidence / deliverables

- `grid_ratio_scanner.py`
- `grid_ratio_demo.py`
- `grid_ratio_scanner.html`
- `test_grid_ratio_scanner.py`
- `contest_acceptance_report.txt`

## Notes

- The requester said they would use a scripted sequence, but the private sequence was not published.
- Our independent replay tests equivalent stated behavior rather than claiming access to the hidden sequence.

## Referent order

1. 📍 External 3×3 Grid Ratio Scanner specification
2. Required output / acceptance condition
3. Current implementation
4. Test evidence
5. Submission state
6. Older/frozen evidence
