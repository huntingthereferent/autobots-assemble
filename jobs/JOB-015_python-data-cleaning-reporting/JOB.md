# JOB-015 — Python Data Cleaning & Reporting

<!-- REVIEW_NAV_START -->
[← JOB-014 — Data Engineer — Python / SQL / AWS](../JOB-014_python-sql-aws-data-engineer/JOB.md) · [Job Index](../../JOBS.md) · [JOB-019 — Browser Automation for Real Estate Data Migration →](../JOB-019_browser-automation-real-estate-migration/JOB.md)
<!-- REVIEW_NAV_END -->

- **Source:** https://www.freelancer.com/projects/pandas/python-data-cleaning-reporting
- **Project ID:** 40739384
- **Reward observed:** ₹100–400 INR / hour
- **Status:** blocked
- **Submission:** not_submitted

## Preferred referent

📍 External pandas/NumPy data-cleaning specification

## Boundary

Take a supplied raw dataset through reproducible cleaning/preprocessing with pandas/NumPy and SQL where useful, then deliver a clean dataset, documented script/notebook, and concise issue-resolution summary.

## Acceptance

Workflow runs end-to-end without manual intervention; all code blocks execute in under five minutes on a standard laptop; deliver clean CSV/database table, commented code, and Markdown/PDF summary.

## Current result

PROTOTYPE PASS — 51,000-row synthetic dirty fixture cleaned to 50,000 unique source records with explicit audit counters, CSV + SQLite outputs, automated tests, and 0.7601-second measured end-to-end runtime in this environment.

## Next movement

When the client dataset arrives, confirm the business rules for duplicate keys, missing values, date locale and outliers, run profiling first, then apply the demonstrated pipeline and time the complete real-data run.

## Blockers

- Client raw dataset is supplied only at kickoff.
- Client-specific rules for duplicates, missing values, locale and outliers are not public.

## Evidence

- `prototype/README.md`
- `prototype/cleaner.py`
- `prototype/generate_fixture.py`
- `prototype/fixtures/raw_dirty_data.csv`
- `prototype/output/cleaned_data.csv`
- `prototype/output/cleaned_data.sqlite`
- `prototype/output/audit.json`
- `prototype/output/cleaning_summary.md`
- `prototype/sql_checks.sql`
- `prototype/tests/test_cleaner.py`
- `submission.txt`
- `acceptance_report.txt`

<!-- REVIEW_NAV_START -->
[← JOB-014 — Data Engineer — Python / SQL / AWS](../JOB-014_python-sql-aws-data-engineer/JOB.md) · [Job Index](../../JOBS.md) · [JOB-019 — Browser Automation for Real Estate Data Migration →](../JOB-019_browser-automation-real-estate-migration/JOB.md)
<!-- REVIEW_NAV_END -->
