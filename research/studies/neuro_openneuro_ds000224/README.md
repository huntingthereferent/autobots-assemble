# NEURO — one public OpenNeuro metadata snapshot

**Purpose:** source admission only, not neuroscience experimentation. The [official OpenNeuro API examples](https://docs.openneuro.org/api.html) document dataset `ds000224`, snapshot `1.0.1`, and DOI `10.18112/openneuro.ds000224.v1.0.1`. This sample is the Midnight Scan Club (MSC) dataset.

The reader sends **one explicit GraphQL query** with a fixed `datasetId` and version tag, requesting only the public snapshot `id`, `tag`, `description.Name` and `description.DatasetDOI`. The bounded public endpoint is `https://openneuro.org/crn/graphql`. It accepts no arbitrary user query, uses no credential, follows no redirects, and does not request a file tree or any participant-level data. An exact response body SHA-256, timestamp, version and official DOI are retained as a **metadata witness**, or a source error is preserved as `SOURCE_WALL`.

The source family is presently recorded as `manual_review_required` in the 18-family catalog. A successful metadata response **does not automatically change** that restriction, does not activate a neuroscience experiment, and does not validate a research claim. Dataset-specific license, human-subject privacy/deidentification, population and BIDS attributes, plus the planned analytic method, must be reviewed before any dataset files can be admitted.

Offline: `python -m unittest discover -s research/studies/neuro_openneuro_ds000224 -p 'test_*.py' -v`. Default CLI: `UNOBSERVED`. Opt-in: `python research/studies/neuro_openneuro_ds000224/snapshot_metadata.py --live --output neuro-metadata.json`.

All status outputs set **`scientific_experiments_run=0`**, regardless of source success. Keep this within NEURO source intake until an actual participant-data handling and scientific-method review is complete.
