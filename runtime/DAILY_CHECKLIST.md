# Daily claim-verification tasks

Eight initial tasks are sourced from James's public portfolio: seven entries in
his claim-and-witness index plus the proposed new inverted A/B ARC solver.

- **Inventory:** [claim_checklist.json](claim_checklist.json)
- **Durable store:** [daily_checklist.py](daily_checklist.py)
- **Checklist interface:** [http/daily-checklist.html](http/daily-checklist.html)
- **Regression tests:** [test_daily_checklist.py](../network/tests/test_daily_checklist.py)

Start the existing local entrance with `python -m runtime.http_server`, then
open `http://127.0.0.1:8040/daily-checklist.html`.

Tasks remain unchecked indefinitely, including through restarts and calendar
changes. Once checked, they stay visible through the current
`America/Chicago` day, then disappear from the active projection on the next
day. The append-only task and completion history persists; no task is deleted.
Uncheck is permitted during the same calendar day. The system does **not**
automatically repopulate completed items on following days.

API (loopback only; this is a private local list):
- `GET /api/daily-checklist`
- `POST /api/daily-checklist` with `{"title":"..."}`
- `POST /api/daily-checklist/{id}/check` with `{"checked":true|false}`

Run tests with `python -m unittest network.tests.test_daily_checklist -v`.

**Boundary:** A checked item documents personal to-do disposition, not a
successful mathematical proof, completed research artifact, or native runtime
handoff. This does not change the original public claims or prior run data.

**Open integration gap:** The standalone checklist page is committed, but
the home-page `index.html` task panel has not yet been updated to include it.
Its existing native task and handoff widgets are unchanged.
