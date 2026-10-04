# ALL WORK Scans

This directory stores dated snapshots from `work.all-work-scan`.

A scan is **not** a task queue and does not automatically activate a candidate. It preserves what surfaced, why it qualified, the source/status at scan time, and whether it had appeared before.

## Recurrence

Previously seen candidates are not hidden. If a candidate independently surfaces again, keep it in the new scan and mark it `REPEAT`.

That allows recurrence to become evidence instead of being lost to deduplication.

## Status labels

- `NEW` — not seen in an earlier saved scan.
- `REPEAT` — surfaced in a prior scan and surfaced again now.
- `CHANGED` — resurfaced but current availability/state materially changed.
- `WALL` — interesting work, but a current resource/eligibility/access wall blocks direct movement.
