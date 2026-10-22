# Neuroscience / OpenNeuro public dataset identity probe

## Observed public source identity (October 22, 2026)

[Actual CI run 39782507005](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39782507005) passed both independent jobs: offline synthetic controls and one fixed, live public metadata query. The unmodified official OpenNeuro dataset/snapshot identity returned as `ds000224:1.0.1`, DOI `10.18112/openneuro.ds000224.v1.0.1`. The complete reply was 294 bytes and was recorded only through its SHA-256 hash `1cfc7ea2a470186ac613ebd8887ed6578bf0f1d83647a3979d3f500715f1f875`.

The append-only [verified public identity receipt](observations/2026-10-22-run-39782507005.json) preserves the exact URL, UTC observation time, source code revision, evidence boundaries and whether access succeeded. This does **not** establish rights for subject recordings, agreement of original findings, or permission to treat actual neuroimaging measurements as science evidence. This lane is now **PUBLIC_SNAPSHOT_METADATA_OBSERVED**; the parent NEURO lane still requires a separate per-study data/ethics gate.

The existing **NEURO** research lane remains behind the `openneuro` and `physionet` dataset-specific access and rights review gates. This independent sublane proposes a narrower question: **Can OpenNeuro's public GraphQL service resolve the dataset and exact, previously documented frozen snapshot identity?**

Source: [OpenNeuro official GraphQL API examples](https://docs.openneuro.org/api.html). Their example uses dataset `ds000224`, snapshot tag `1.0.1` and DOI `10.18112/openneuro.ds000224.v1.0.1`.

The [fixed-query script](snapshot_metadata.py) fetches only: dataset ID, dataset name, snapshot ID, snapshot tag, and public dataset DOI. It has no general GraphQL arguments, search filters, subject identifiers, file access, dataset downloading, or credentials. Request size 60 kB max, one fixed HTTPS POST, 15-second timeout, no redirect acceptance. The response is hashed, not archived; the derived receipt does not include any free-text original dataset description or people.

Source validation stops at either `PUBLIC_SNAPSHOT_METADATA_OBSERVED` or `SOURCE_WALL`. The source document, version and DOI must all match the frozen official example; API errors, missing snapshots and changed versions are preserved as failures or walls. These outcomes are **not** imaging data admission, a dataset license review, or scientific replication. They do **not** automatically promote the parent NEURO lane to research-ready.

Run the offline test suite with:

    python -m unittest discover -s research/testing_lanes/neuro_public -p "test_*.py" -v

No network is contacted by default:

    python research/testing_lanes/neuro_public/snapshot_metadata.py

The independent GitHub Actions workflow adds an explicit, single fixed public metadata request after offline tests pass. The CI artifact contains only the source hash, exact public dataset/snapshot identifier, retrieval timestamp, and access status; it contains **no image, recording, participant data, or source response body**.

Before any scientifically meaningful neurological analysis, choose the actual study question, confirm version and rights at record level, record ethics constraints, and devise counterexamples. PhysioNet's credentialed datasets remain completely excluded from this probe.
