# OECD SDMX — bounded source dataflow identity

## First independently verified OECD structure · October 22, 2026

[GitHub Actions 39831994691](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39831994691) passed both the synthetic offline source controls and the one fixed public dataflow request. The original OECD endpoint returned HTTP 200 and 7,967 SDMX XML bytes. The observed exact agency, flow and version matched, with all five structural predicates true. The source was discarded after hashing; SHA-256 `c5e17eb631f9eba763e6baf2fec612a7841642be84fd217ecb0ade2687416109`.

The append-only [source witness](observations/2026-10-22-run-39831994691.json) contains the source hash, UTC time and identity checks. It records **zero statistical rows, zero country values and no validated scientific result**. The OECD dataset-specific selection and data-use gate remains manual.


## Observed public dataflow identity, October 22, 2026

[Run 39831994691](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39831994691) completed both offline and public-source identity jobs successfully. The fixed OECD structure endpoint returned HTTP 200 and 7,967 bytes. Five dataflow/structure safety predicates were true; response SHA-256 `c5e17eb631f9eba763e6baf2fec612a7841642be84fd217ecb0ade2687416109`. The original XML was not stored. The verified [receipt](observations/2026-10-22-run-39831994691.json) records UTC time, source identifier, hash and zero statistical rows admitted.

A publisher's structure-only metadata response is not OECD data for a selected country, a license review, evidence for a scientific result, or authorization to republish underlying tables.


The [official OECD API guide](https://www.oecd.org/en/data/insights/data-explainers/2024/09/api.html) explains public SDMX **structural metadata** and separate statistical **data** endpoints. We use the [official Data Explorer flow example](https://data-explorer.oecd.org/vis?df%5Bag%5D=OECD.SDD.TPS&df%5Bid%5D=DSD_BOP%40DF_TIS&df%5Bvs%5D=1.0) for one fixed dataflow identity: agency `OECD.SDD.TPS`, ID `DSD_BOP@DF_TIS`, version `1.0`.

The independent [source reader](dataflow_identity.py) has a default **UNOBSERVED** mode and an explicit one-request `--live` mode. It requests only the published SDMX **structure** with the exact identity and the `references=none` option. One fixed HTTPS GET, strict redirect rejection, 15-second timeout, response ≤180 kB, XML DTD rejection, and verification of source-specific structural fields. The raw response is hashed and immediately discarded. The receipt contains UTC time, SHA-256, source identity flags and any failed predicate IDs; no XML is retained.

No `/data/` endpoint, country/indicator/time-period series, economic observation, source-rights authorization, or scientific result is included. If OECD changes the format, returns a rate-limit, or blocks the request, the result remains **SOURCE_WALL**, not an inferred negative research outcome. The original OECD manual data-selection and reuse gate remains intact for economics/sociology research contexts.

Offline synthetic tests:

    python -m unittest discover -s research/testing_lanes/oecd_public -p 'test_*.py' -v

Only after public source identity is verified and actual dataset rights/units agreed could a separate, independently frozen economic hypothesis be tested.
