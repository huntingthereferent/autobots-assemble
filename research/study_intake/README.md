# Source-pinned study intake: first metadata witness

Study record: [OSC-2015](studies/OSC-2015.json) — *Estimating the reproducibility of psychological science*, DOI [10.1126/science.aac4716](https://doi.org/10.1126/science.aac4716), independently catalogued at [PubMed PMID 26315443](https://pubmed.ncbi.nlm.nih.gov/26315443/).

**Scope is strictly bibliographic identity.** The publication reports a large-scale psychology replication project; this folder does **not** rerun it, infer a replication success rate, ingest subject data, or evaluate its statistical conclusions. The publication's scientific claim stays NOT_REPRODUCED.

## Two independent public metadata services

- **Crossref** — retrieve the DOI's deposited work metadata. Docs: https://www.crossref.org/documentation/retrieve-metadata/rest-api/
- **OpenAlex** — retrieve the corresponding indexed work by its DOI. Docs: https://help.openalex.org/api/ and https://help.openalex.org/api/authentication/

Both records are separately timestamped and hashed as actually retrieved. The adapter compares normalized DOI, title and year against the pinned baseline; an agreement is a **metadata match**, not scientific validation. A source mismatch is retained rather than quietly reconciled away.

The client makes *at most two GET requests* to fixed HTTPS hostnames, with 15-second timeouts and a 2 MB response cap per source. It does not follow redirects, recurse, crawl citations, download PDFs or copy copyright abstracts. Crossref and OpenAlex metadata can change; the receipt records the actual observation time and exact body SHA-256. For ethical/privacy boundaries, only public bibliographic metadata is requested.

## Commands

Offline (default, no network):

    python research/study_intake/metadata_probe.py
    python -m unittest discover -s research/study_intake -p 'test_*.py' -v

A deliberate *bounded* metadata check (network required):

    python research/study_intake/metadata_probe.py --live --output study-metadata-receipt.json

A dedicated PR workflow runs offline negative-case tests and a single live two-source query with an archived GitHub Actions receipt. It does not commit the live record to the repo. If an API is unavailable, the receipt remains UNKNOWN and the live check fails distinctly; this is an access wall, not scientific refutation.

## Original analysis data: separate admission gate

The original project's [Center for Open Science analysis repository](https://github.com/CenterForOpenScience/rpp) identifies its data and scripts, and links an [OSF dataset](https://osf.io/fgjvw/). A commit-pinned potential source is registered as [OSC-2015-UPSTREAM-CANDIDATE](studies/OSC-2015-UPSTREAM-CANDIDATE.json). Its current status is DISCOVERED_NOT_ADMITTED: data content, rights, privacy, and exact relationship to the published analysis are not yet verified. The listed Git blob SHA does not replace that review.

## Test contract

| Field | Frozen meaning |
|---|---|
| Question | Can independently retrieved Crossref and OpenAlex records identify the exact same published study? |
| Independent evidence | Two observed source response hashes, timestamps and normalized metadata |
| Positive condition | Both records match DOI, title and year |
| Negative condition | Missing source, DOI/title/year contradiction, changed source record, parse error |
| Outside scope | Original paper's claims, replication outcomes, participant data, and significance calculations |
| Next boundary | Find original public study data with rights review, freeze it, and reproduce a *declared statistic* separately |

This is a source-intake test lane, not another generic category or claim that all scientific evidence is reducible to DOI metadata.
