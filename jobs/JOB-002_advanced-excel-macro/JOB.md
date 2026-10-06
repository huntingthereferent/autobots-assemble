# JOB-002 — Advanced Excel Macro Development

<!-- REVIEW_NAV_START -->
[← JOB-001 — 3×3 Grid Ratio Scanner](../JOB-001_grid-ratio-scanner/JOB.md) · [Job Index](../../JOBS.md) · [JOB-003 — Interactive Fuel Reporting App →](../JOB-003_fuel-reporting-app/JOB.md)
<!-- REVIEW_NAV_END -->

## Identity

- **Job ID:** JOB-002
- **Category:** external_bounded_problem
- **Source:** Freelancer
- **Source URL:** https://www.freelancer.com/contest/advanced-excel-macro-development-2733659
- **Reward observed:** $120
- **Date added:** 2026-10-03
- **Status:** ready_to_submit
- **Submission:** not_submitted

## Scope

- **📍 External Excel transformation specification**
- **Boundary:** Transform a supplied A:Z CSV into the requested 15-column output, derive coverage averages, calculate Premium from an editable Settings multiplier, and export the Data view as CSV.
- **Acceptance:** Every specified coverage code and required transformation checked independently.
- **Next movement:** When computer access is available, import CsvTransformer.bas into the workbook, save as .xlsm, review, and optionally submit.

## Result

PASS — 41/41 acceptance checks.

## Evidence / deliverables

- `ExcelMacro_Solution.xlsx`
- `CsvTransformer.bas`
- `sample_input.csv`
- `expected_output.csv`
- `acceptance_report.txt`
- `test_manifest.json`

## Notes

- Source column letters are treated as original A:Z positions so the specification remains internally consistent.
- The brief asks for both CSV and a second worksheet/formatting; the workbook preserves Settings/formatting and the macro exports Data as CSV.

## Referent order

1. 📍 External Excel transformation specification
2. Required output / acceptance condition
3. Current implementation
4. Test evidence
5. Submission state
6. Older/frozen evidence

<!-- REVIEW_NAV_START -->
[← JOB-001 — 3×3 Grid Ratio Scanner](../JOB-001_grid-ratio-scanner/JOB.md) · [Job Index](../../JOBS.md) · [JOB-003 — Interactive Fuel Reporting App →](../JOB-003_fuel-reporting-app/JOB.md)
<!-- REVIEW_NAV_END -->
