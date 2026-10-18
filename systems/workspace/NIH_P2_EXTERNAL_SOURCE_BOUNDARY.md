# NIH Phase 2 — first external source intake boundary

**Status: external-source intake experiment; not a scientific benchmark or a
new native workstation checkpoint.**

## The source

ClinicalTrials.gov, an official public registry maintained by the U.S.
National Library of Medicine, provides a [documented version 2 REST
API](https://clinicaltrials.gov/data-api) with dates for first posting, last
update posting, and (where available) first results posting. See the
[NLM API 2.0 notice](https://www.nlm.nih.gov/pubs/techbull/ma24/ma24_clinicaltrials_api.html)
and the [registry data-field description](https://clinicaltrials.gov/data-about-studies/csv-download).

The intake selects three identified **public study records**, fetches those
specific date fields directly from `clinicaltrials.gov`, checks the returned
NCT ID, validates full ISO dates and order, and records:

- the exact official API URL and JSON field path;
- UTC retrieval time (when this program witnessed today's public response);
- the SHA-256 of the actual retrieved response bytes;
- first posting, latest update posting, and optional first results posting;
- the as-of list of *those posting events only* at explicit date cutoffs.

**Raw records are not stored:** The archived receipts have posting dates and
source fingerprints only. Names, contacts, interventions, statuses, outcomes,
patient records and trial conclusions are not retained.

## What this does and does not mean

A study's first-posted date indicates when its registration was posted;
a last-update-posted date marks when an update was posted. Neither date tells
us what *other fields said* in a historical version. The current public
registry endpoint returns current record data; it is **not** sufficient to
recover historical recruitment status, protocol versions, or results text.
The experiment therefore never labels a current trial status as historically
knowable at the first-posted date.

The archived as-of event views concern **registry posting notices**. They are
not temporal query answers for medical evidence, and they are not a
historical validity-ground-truth benchmark. Public source events are distinct
from the original synthetic observations and cannot be silently mixed with
them.

## Evidence gate and next scientific decision

1. Exact external source response must be successfully retrieved and validated
   by an independent GitHub Actions run; local mock tests do not count.
2. Preserve the retrieval timestamp, API URL, chosen field path, extracted
   date, and raw response digest.
3. If the official response is unavailable, malformed, redirected outside
   its origin, or missing required dates, mark intake **not admitted**.
4. Before evaluating *historical record content*, obtain independently
   authenticated **versioned source snapshots** and distinguish posting date,
   clinical event date, effective date, and researcher observation time.
5. Only then develop an external-data benchmark with a truly independent
   oracle; do not score the same fixture-generating rule against itself.

The original twelve-job workstation and the already witnessed synthetic
`NIH-P2-BENCHMARK` remain unchanged. This task does not create a
thirteenth native worker, official NIH Phase 2 submission/award, broad
biomedical claim, or patient-data processing.

## Repeat the source check

```bash
python -m unittest -v network.tests.test_nih_external_registry_intake
python -m systems.workspace.nih_external_registry_intake \
  --output-dir /tmp/nih-public-registry
```

The second command requires live access to the documented official API.
Each run is a *new, date-stamped observation*, not a timeless immutable
record, and must be interpreted with its own saved digest.
