# World continuity — observed public data

[![Latest world observations](latest.svg)](LATEST.md)

**[Open the readable source-linked view](LATEST.md)** · [Machine-readable state](latest.json) · [Poll history](checks.jsonl)

This is a **read-only GitHub presentation of the existing [multi-source public-data monitor](../../work/projects/public-data-monitor/README.md)**. It reuses its original USGS, GitHub, PyPI, source-identity, change-classification and GitHub↔PyPI matching functions. The view does **not** introduce a second ingestion engine or a new source of truth.

## Three existing live sources

The USGS rolling-hour earthquake feed supplies changing physical event observations. Its event IDs and source timestamps remain intact. The original GitHub adapter monitors `psf/requests`; the PyPI adapter monitors the `requests` package. Their relationship is assessed by the existing source-metadata matching rule and retains each piece of source evidence. We do not infer a USGS/software relationship simply from simultaneous activity.

The output is a small, source-linked starting point for looking at continuity through *change, recorded identity, temporal history, corrections and unresolved connections*, not a statement that all data describe one mechanism.

## The movement

```text
USGS rolling-hour JSON --- original adapter -----+
                                                   |
GitHub API ------------- original adapter --------+--> read-only public observations
                                                   |    - source identifiers
PyPI API --------------- original adapter --------+    - timestamps and historical polls
          |                                        |    - changes from prior observation
          +--- existing URL identity rule <-------+    - evidence for supported link
                                                             |
                                             GitHub SVG + JSON + Markdown
```

The existing platform also has PostgreSQL observation history, Celery scheduling, Prometheus instrumentation and Grafana dashboards. This view does **not** replace any of those. Instead, it makes a bounded public observation readable on GitHub, without requiring a constantly deployed public Grafana server.

- The [scheduled GitHub Actions workflow](../../.github/workflows/world-continuity.yml) requests source observations every six hours and whenever its source or workflow is updated; GitHub may delay scheduled runs. The first public view is not available until a workflow successfully fetches and commits its outputs.
- If fetching, validation, or unit tests fail, no new snapshot is committed. The last committed observation remains historical and **must not be mistaken for fresh data**.
- `checks.jsonl` retains a compact polling trail; `latest.json` keeps current source-bound records, with detailed changes evaluated through the existing native classifier. Each pushed Git commit also retains the previous version.
- USGS is a sliding **past-hour** feed; older events naturally leave the window. Their absence in a later poll is *not* a witnessed disappearance.
- The matching rule supports only a **declared metadata/URL relationship**, not an independent claim about source ownership.
- The output hash is a content fingerprint, not authenticated evidence.
- Prometheus stores numeric operational time series such as collection failures and run durations. The source-owned observations and relationships belong to the data monitor / observational layer, **not to high-cardinality Prometheus labels**.
- Real cross-source claims beyond the declared GitHub↔PyPI URL rule require a separately stated witness and cannot be inferred from visuals.

## Reproduce without inventing test data as live evidence

Run from the repository root with Python 3.12:

```sh
pip install -e work/projects/public-data-monitor
python -m unittest discover -s views/world-continuity -p "test_*.py" -v
python views/world-continuity/render.py --execute
```

Without `--execute`, the renderer does not poll sources or modify files. Tests run with fixtures only. GitHub source polling and the scheduled output are separate from those local tests.

**Evidence boundary:** a green test of this renderer does not attest to a fresh live fetch. Check the recorded timestamp, raw source URLs, GitHub Actions run, and source data for that.
