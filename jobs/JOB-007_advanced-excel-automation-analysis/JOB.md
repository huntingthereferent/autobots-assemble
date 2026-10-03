# JOB-007 — Advanced Excel Automation & Analysis

<!-- REVIEW_NAV_START -->
[← JOB-006 — One-Click Counter and Comparison Tool](../JOB-006_one-click-counter-comparison/JOB.md) · [Job Index](../../JOBS.md) · [JOB-008 — Customer Data Cleaning & Excel Automation →](../JOB-008_customer-data-cleaning-excel-automation/JOB.md)
<!-- REVIEW_NAV_END -->

## Identity

- **Source:** Freelancer
- **Project ID:** 40747173
- **Reward observed:** ₹750–1,250 INR / hour
- **Date added:** 2026-10-03
- **Work status:** blocked (tested_logic)
- **Submission:** not submitted
- **Payment:** not paid
- **Source URL:** https://www.freelancer.ph/projects/data-analysis/advanced-excel-automation-analysis

## Scope

- **📍 External Advanced Excel Automation & Analysis specification**
- Create a repeatable native-Excel/VBA one-click workflow that cleans same-structure raw files, removes duplicates, handles missing regression rows, normalizes formatting, runs a regression, outputs coefficients/R²/residuals, and rebuilds a dashboard with a residual plot.

## Acceptance

One macro-enabled .xlsm containing all cleaning/regression procedures; automatically refreshed dashboard; end-to-end execution under 30 seconds on about 20,000 rows; and successful tests on client unseen datasets.

## Current result

PROTOTYPE PASS — demo replay cleaned 245 raw rows to 233 usable rows, removed 5 duplicates and 7 incomplete regression rows, and independently reconciled R² 0.98953813 with coefficients 1.763978803 (MarketingSpend) and 0.812960824 (Visits). Final VBA execution/runtime and unseen-dataset acceptance remain pending.

## Blockers

- This environment does not execute desktop Excel VBA.
- Final .xlsm packaging requires desktop Excel macro import/save.
- The under-30-second criterion has not been measured in Excel.
- Client unseen datasets are not publicly supplied.

## Next movement

In desktop Microsoft Excel, import RegressionAutomation.bas into the demo workbook, save as .xlsm, run the 20,000-row benchmark fixture, verify elapsed time under 30 seconds, inspect the residual/dashboard output, then test against client unseen datasets when supplied.

<!-- REVIEW_NAV_START -->
[← JOB-006 — One-Click Counter and Comparison Tool](../JOB-006_one-click-counter-comparison/JOB.md) · [Job Index](../../JOBS.md) · [JOB-008 — Customer Data Cleaning & Excel Automation →](../JOB-008_customer-data-cleaning-excel-automation/JOB.md)
<!-- REVIEW_NAV_END -->
