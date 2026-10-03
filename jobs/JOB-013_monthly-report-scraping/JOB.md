# JOB-013 — Automate Monthly Report Scraping

## Identity

- **Source:** Freelancer
- **Project ID:** 39782099
- **Reward observed:** $250–750 USD
- **Date added:** 2026-10-03
- **Work status:** blocked (bounded prototype complete)
- **Submission:** not submitted
- **Payment:** not paid
- **Source URL:** https://www.freelancer.com/projects/web-scraping/automate-monthly-report-scraping

## Scope

- **📍 External monthly Texas reporting automation specification**
- Combine monthly Excel production data with a Comptroller web-sourced monthly value, apply client-specified credit logic, support RRC/Comptroller reporting, and export two production columns to a QuickDecline/SQLite workflow.

## Acceptance

Working Excel automation, reproducible report-population logic, scraper behavior, SQLite handoff, and maintainable documentation; filing-specific outputs require validation against the client's real templates and rules.

## Current result

**PROTOTYPE PASS.** Official public source targets were mapped; a synthetic District 5/6 workbook, configurable credit arithmetic, two-column SQLite handoff, schedule-parser fixture, and automated parser/SQLite tests were built. The fixture tests pass.

## Evidence

- `TX_Monthly_Reporting_Automation_Prototype.xlsx`
- `quickdecline_prototype.db`
- `tx_reporting_pipeline.py`
- `test_tx_reporting_pipeline.py`
- `comptroller_schedule_fixture.html`
- `SOURCE_MAP.md`
- `acceptance_report.txt`
- `submission.txt`

## Blockers

- Client spreadsheet/template and exact fixed-credit rule are not public.
- Fillable PDF field IDs are not mapped.
- QuickDecline's actual SQLite schema / exact export columns are not public.
- Live scraper durability must be rechecked before production use.

## Next movement

Replace synthetic mappings with client data/schema, run a live source retrieval, populate the actual forms, and validate all totals before any filing use.
