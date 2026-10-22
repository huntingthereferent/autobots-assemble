# NOAA NCEI SSOD Version 2 · public dataset identity

A **separate source-only test** of NOAA's official [Synoptic Summary of the Day (SSOD), Version 2 dataset overview](https://www.ncei.noaa.gov/metadata/geoportal/rest/metadata/item/gov.noaa.ncdc:C01690/html). The NCEI catalog identifies `gov.noaa.ncdc:C01690` and `NCEI DSI 2076_02`. SSODv2 succeeds the earlier **GSOD** publication, which NOAA labels superseded for primary data use.

This sublane verifies only publisher, exact versioned dataset title, both identifiers, SSODv2 label and source lineage. It does **not** query weather measurements, station IDs, participant data, historical weather files, time series, CDO token-authenticated APIs, or observations.

The reader [catalog_identity.py](catalog_identity.py) defaults to **UNOBSERVED**. An explicit `--live` performs exactly one fixed, no-redirect HTTPS GET, limited to 500 kB and 15 seconds; it discards the HTML and returns only UTC retrieval time, SHA-256 of the source response and six yes/no publisher identity checks. Errors are explicit SOURCE_WALL states; rejected predicates are named but the original NOAA text is not persisted.

The separate workflow runs 12 offline positive/negative controls first and only then makes the fixed public metadata request. The original registry's NOAA CDO source remains under a manual token/station/data-rights gate. A successful public dataset listing is not a daily weather observation, climate inference or experiment. NOAA's catalog itself warns that data quality and lineage must be evaluated for intended uses, so an actual science lane would require station/date scope, units, version, license/attribution, independent comparison and failure criteria.

Offline validation:

    python -m unittest discover -s research/testing_lanes/noaa_public -p 'test_*.py' -v
