# JOB-003 — Interactive Fuel Reporting App

## Identity

- **Source:** Freelancer
- **Prize observed:** $100
- **Date added:** 2026-10-03
- **Work status:** blocked (prototype tested)
- **Submission:** not submitted
- **Payment:** not paid
- **Source:** https://www.freelancer.com/contest/interactive-fuel-reporting-app-2739029

## Scope

- **📍 Preferred referent:** the external Interactive Fuel Reporting App specification.
- Import three files: monthly fuel statement, branch litres sheet, Cars+ billed export.
- Match/reconcile by branch.
- Flag litres not charged.
- Store data for branch drill-down.
- Show an on-screen branch report.
- Export each branch report to PDF.
- Final deliverable eventually requires a Windows application, source, stationery-matched PDF, and brief user guide.

## Current result

**Prototype PASS — 12/12 synthetic acceptance checks.**

The synthetic run produced:

| Branch | Statement | Tracked | Cars+ billed | Uncharged | Statement variance |
|---|---:|---:|---:|---:|---:|
| North | 2,000 L | 2,000 L | 1,850 L | 150 L | 0 L |
| South | 1,500 L | 1,500 L | 1,450 L | 50 L | 0 L |
| West | 1,200 L | 1,200 L | 950 L | 250 L | 0 L |

## Implemented

- dependency-light `.xlsx` table parser
- PDF statement text extraction
- alias-based branch/litres column recognition
- branch normalization and aggregation
- uncharged-litres calculation
- statement-vs-tracked variance
- SQLite result storage
- branch PDF generation
- basic Windows/Tkinter UI source
- phone-viewable HTML drill-down demo
- synthetic fixtures and automated acceptance test

## Not yet honestly complete

The public contest does not provide the client's real input files or stationery, so these remain external blockers:

1. validate parser mappings against the real statement/export shapes
2. confirm the uncharged-litre formula against the client's manual reconciliation
3. match their stationery exactly
4. add native drag-and-drop rather than file-picker only
5. compile/package a Windows `.exe` or installer

## Next movement

Obtain one real sample of each of the three inputs plus their stationery. Keep the external spec as 📍 while adapting only the parser/output edges required by those real files.
