# NEURO — one public OpenNeuro metadata snapshot

**Purpose:** source admission only, not neuroscience experimentation. The [official OpenNeuro API examples](https://docs.openneuro.org/api.html) document dataset `ds000224`, snapshot `1.0.1`, and DOI `10.18112/openneuro.ds000224.v1.0.1`. This sample is the Midnight Scan Club (MSC) dataset.

The reader sends **one explicit GraphQL query** with a fixed `datasetId` and version tag, requesting only the public snapshot `id`, `tag`, `description.Name` and `description.DatasetDOI`. The bounded public endpoint is `https://openneuro.org/crn/graphql`. It accepts no arbitrary user query, uses no credential, follows no redirects, and does not request a file tree or any participant-level data. An exact response body SHA-256, timestamp, version and official DOI are retained as a **metadata witness**, or a source error is preserved as `SOURCE_WALL`.

The source family is presently recorded as `manual_review_required` in the 18-family catalog. A successful metadata response **does not automatically change** that restriction, does not activate a neuroscience experiment, and does not validate a research claim. Dataset-specific license, human-subject privacy/deidentification, population and BIDS attributes, plus the planned analytic method, must be reviewed before any dataset files can be admitted.

Offline: `python -m unittest discover -s research/studies/neuro_openneuro_ds000224 -p 'test_*.py' -v`. Default CLI: `UNOBSERVED`. Opt-in: `python research/studies/neuro_openneuro_ds000224/snapshot_metadata.py --live --output neuro-metadata.json`.

All status outputs set **`scientific_experiments_run=0`**, regardless of source success. Keep this within NEURO source intake until an actual participant-data handling and scientific-method review is complete.

## First verified public metadata witness — October 22, 2026

The [actual metadata-only run 39786532333](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39786532333) passed 12 offline controls and retrieved the exact public dataset snapshot identity and DOI. Its immutable [derived source receipt](observations/2026-10-22-run-39786532333.json) has a GraphQL response SHA-256 of `a7783177c3abf9d68dc9ff718bb86ee1ac9d6bb03e6fc0f282571ff7dc0c5b49`. This verifies **snapshot metadata**, not participant-record permissions, processing correctness or scientific results. The source family's existing manual human-data and ethics/rights gate is unchanged. Zero neuroimaging data files were requested or downloaded.
