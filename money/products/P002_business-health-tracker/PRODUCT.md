# P002 — Business Health Check

**status:** working proof  
**goal lane:** money / products  
**source:** current external fixed-price opportunity  
**source URL:** https://www.upwork.com/freelance-jobs/apply/Build-Simple-Business-Health-Tracker-for-Small-Business-Owners-MVP_~022105798375613913020/  
**scan date:** 2026-10-05  
**listed budget:** $300 fixed  
**submission status:** not yet submitted

## Current referent

Build the bounded product described by the external brief: a mobile-first small-business health tracker that takes four groups of operating inputs, calculates business health measures, presents one clear dashboard, and can return one plain-English AI suggestion.

## External boundary traced

Required relations reached from the brief:

```text
initial investment
monthly running costs
unit cost + selling price
monthly sales
        |
        v
deterministic operating calculations
        |
        v
break-even + profit/loss + payback
        |
        v
simple status + "sell X more" number
        |
        v
one plain-English suggestion
```

Explicitly outside the requested MVP: accounts/login, payment processing, bank/accounting integrations, native mobile application, and complex charts/reports.

## Current realization

A working local MVP now exists under `app/`.

Implemented:

- four-step mobile-first input flow;
- deterministic profit/loss, contribution, break-even, remaining-sales, and payback calculations;
- green/yellow/red dashboard state;
- single plain-English next-move suggestion;
- OpenAI Responses API backend path when `OPENAI_API_KEY` is available;
- deterministic fallback so the product remains functional without an API key;
- source-only Python server with no third-party runtime dependency;
- calculation tests.

## Witness

Local verification on 2026-10-05:

- `node test.mjs` -> all calculation tests passed;
- `GET /` -> HTTP 200;
- `GET /logic.mjs` -> HTTP 200;
- `POST /api/insight` -> HTTP 200 with a valid fallback suggestion.

The OpenAI path is implemented but has not been live-tested here because no API key was supplied during this build.

## Next reached edges

- inspect the rendered product manually in-browser;
- if acceptable, create a client-facing proof/demo artifact;
- submit against the external opportunity while it remains open;
- live-test the OpenAI path with a project API key before final delivery;
- deploy only after the submission/client boundary requires it.
