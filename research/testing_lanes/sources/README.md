# Research sources — individual admission records

The 18 source files in this directory are **separate source families**, not one bulk crawler and not scientific test results. Each file defines a current official documentation link, a candidate bounded metadata query (when appropriate), access and rights boundaries, and the exact evidence needed before a scientific claim can move. The baseline [registry](../registry.json) connects them to the 21 separately defined research test contexts.

## Source admission, first

Every source starts `DOCUMENTED_NOT_OBSERVED`. This means **official public documentation was located**, not that the external service returned usable study data. Actual one-source observations must carry a retrieval timestamp, response hash, endpoint and a source-specific structural check. They are separate immutable GitHub Actions receipts and never silently rewrite these versioned candidates.

| Source | Evidence family | Allowed first step |
|---|---|---|
| OpenAlex | scholarly work identity | one DOI work metadata query |
| Crossref | publisher-deposited DOI metadata | one DOI work query |
| OSF | project / preregistration metadata | bounded public node metadata query |
| Zenodo | archived publication / datasets | one published-record search result |
| OpenML | benchmark/dataset metadata | metadata of one named dataset |
| Hugging Face | dataset catalog | one limited dataset metadata result |
| PubMed | biomedical literature index | one exact PMID query |
| ClinicalTrials.gov | public trial records | one registry metadata query |
| PhysioNet | physiological data | manual dataset/access-classification gate |
| OpenNeuro | neuroimaging | manual snapshot/query/privacy gate |
| PubChem | molecular properties | one named CID property, no assays |
| NIST WebBook | reference chemistry | manual data-rights/conditions review |
| NASA Earthdata CMR | collection metadata | one bounded collection query |
| NOAA CDO | climate observations | token and station/dataset selection gate |
| GWOSC | gravitational-wave catalog | one bounded v2 event-catalog metadata page; event version still unselected |
| World Bank | historical indicators | one indicator, country, year query |
| OECD SDMX | structured statistics | select dataset-specific flow/query first |
| NVD | published CVE metadata | one exact CVE advisory query |

## One source per movement

Offline preflight (no network, no external subjects):

    python research/testing_lanes/source_admission.py check
    python research/testing_lanes/source_admission.py list
    python -m unittest discover -s research/testing_lanes -p 'test_*.py' -v

Only when its access boundary allows, inspect **one** source:

    python research/testing_lanes/source_admission.py probe crossref --output crossref-receipt.json

The source-observation workflow runs one public metadata source per job, **sequentially** (max-parallel 1). Provider outages, content type changes, API-key limits, and access denials are recorded as **source walls**, not suppressed or mistaken for scientific disproof. Five sources require a manual gate and cannot be probed by this runner. No data-download endpoint, patient-level record, protected/restricted dataset or network scanning is included.

## Admission distinction

Documentation reviewed → metadata observed → specific record identified and pinned → rights and ethics reviewed → scientific question/test bound → experiment measured → independently reproduced (when actually demonstrated).

This phase implements the first two stages only. A successful DOI metadata GET is not a study replication. A dataset index entry is not usable data. Clinical registry status is not treatment effectiveness. A computed molecular property is not a measured thermodynamic reference.

A future research lane must carry a source-specific record identifier, frozen version or retrieval hash, witness path, source conditions, uncertainty and independent counterexample before being promoted from candidate. A manual access wall remains an ordinary and valid outcome.

Existing ARC, WORLD, NIH, audio and other project tests remain authoritative only for their own evidence. The source registry does not overwrite or manufacture native observations.
