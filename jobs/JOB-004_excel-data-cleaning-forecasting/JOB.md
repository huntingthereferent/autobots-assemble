# JOB-004 — Excel Data Cleaning & Forecasting Formulas

## Identity

- **Source:** Freelancer
- **Project ID:** 40747338
- **Budget observed:** ₹12,500–37,500 INR
- **Date added:** 2026-10-03
- **Work status:** ready to submit (tested)
- **Submission:** not submitted
- **Payment:** not paid
- **Source:** https://www.freelancer.ca/projects/data-analysis/excel-data-cleaning-forecasting-formulas

## Scope

- **📍 Preferred referent:** the external Excel Data Cleaning & Forecasting Formulas specification.
- Supply exactly four native Excel formula designs.
- Clean raw spreadsheet data by standardising text and isolating usable rows.
- Feed the cleaned series into a lightweight forecast.
- Explain each formula briefly.
- Provide a small dummy-data workbook with forecast values clearly visible.
- Keep the sheet readable and reusable for non-experts.

## Implemented

1. `CLEAN` + `TRIM` + `PROPER` text normalisation.
2. An `IF`/validation KEEP-DROP gate for valid date/text/value rows.
3. A `FILTER` spill returning the clean series.
4. `FORECAST.LINEAR` against the clean date/value series.

The workbook includes a Formula Guide, messy dummy data, visible KEEP/DROP decisions, the cleaned series, and three future monthly forecasts.

## Current result

**PASS — ready to submit.**

Independent replay produced:

| Forecast month | Expected value |
|---|---:|
| Jul-2026 | 2,146.77 |
| Aug-2026 | 2,211.93 |
| Sep-2026 | 2,277.08 |

The final workbook formula-error scan returned no `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?`, or `#N/A` matches.

## Limit

The public listing does not provide the client's real spreadsheet. The current artifact therefore satisfies the requested demo/dummy-data deliverable; exact client-column adaptation remains contingent on receiving the client's sheet.

## Next movement

Review the workbook and proposal text, then submit to Freelancer project 40747338. After submission/review, continue to the next queued task.
