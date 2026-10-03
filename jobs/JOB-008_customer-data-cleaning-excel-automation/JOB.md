# JOB-008 — Customer Data Cleaning & Excel Automation

## Identity

- **Source:** Freelancer
- **Project ID:** 40746761
- **Reward observed:** $8–15 USD / hour
- **Date added:** 2026-10-03
- **Work status:** blocked (tested)
- **Submission:** not submitted
- **Payment:** not paid
- **Source URL:** https://www.vn.freelancer.com/projects/data-analysis/customer-data-cleaning-excel-automation

## Scope

- **📍 External Customer Data Cleaning & Excel Automation specification**
- Clean a single customer workbook by retaining the first valid normalized duplicate, standardizing names/emails/city spellings, converting dates to real Excel dates displayed DD/MM/YYYY, preserving legitimate blanks, applying consistent types/formatting, and adding an audit summary.

## Acceptance

Final client workbook must be duplicate-free, consistently formatted, preserve legitimate blanks, contain clean headers, frozen panes and filters, and open flawlessly in standard Microsoft 365 Excel with an auditable transformation summary.

## Current result

PROTOTYPE PASS — specification-faithful dummy workbook reduced 33 rows to 30, removed 3 normalized duplicates, normalized 32 names and 32 emails, standardized 28 city values, converted 32 nonblank dates, and produced zero formula-error matches. Real client workbook remains required.

## Blockers

- Client customer workbook is not publicly supplied.
- Ambiguous/unknown city spelling variants require the actual dataset or client confirmation.

## Next movement

Obtain the client workbook, inspect its actual headers and ambiguous city/name variants, apply the demonstrated cleaning rules, audit the result, and return the final cleaned workbook.
