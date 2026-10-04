# GEMS-001 — Official Rules Swallow

**Source document:** *Geologic Enhanced Mapping System (GEMS) Prize Official Rules*  
**Publisher:** National Laboratory of the Rockies (NLR)  
**Publication:** NLR/OT-6A50-96647  
**Year:** 2026  
**Length:** 19 pages  
**DOI:** 10.2172/3818146  
**Source PDF:** https://www.nlr.gov/docs/fy26osti/96647.pdf

## Swallow decision

This document does **not** define a new protocol or layer.

It is authoritative rule/evidence for the existing `GEMS-001` work referent, so it is absorbed into the challenge record under the existing work/evidence contract.

```text
official rules PDF
      ↓
eligibility / prize / data / submission constraints
      ↓
GEMS-001 evidence
```

Provenance remains attached to the NLR publication and official competition pages.

## Evidence state

**PARTIAL**, not COMPLETE.

The NLR publication record confirms the document identity and abstract, and the official DrivenData competition page exposes several rule excerpts. The direct 19-page PDF itself was not available for full-text rendering through the current retrieval path.

That means the following summary separates supported public rule text from items that still require direct PDF verification.

## Supported rule shape

### Purpose

The prize is intended to produce reproducible, robust, scalable models/algorithms that improve geologic fault identification from geophysical data, supporting geothermal and critical-mineral mapping/exploration.

### Administration / platform

- DOE Office of Geothermal sponsors the challenge.
- NLR administers/supports it.
- DrivenData hosts enrollment, data, submissions, scoring, and audit/performance assessment.

### Eligibility

Public official excerpts state:

- individuals: U.S. citizen or permanent resident;
- teams: captain must be U.S. citizen or permanent resident;
- private entities: incorporated in the U.S. and primary place of business in the U.S.;
- federal entities and federal employees: not eligible.

There is **no separate public professional/academic credential attached to “captain.”** The captain language is an eligibility/representation role.

### Certification

The DrivenData pre-registration form states that each competitor certifies eligibility and compliance with the rules, under penalty of perjury, and represents that submission information is truthful. False statements to the federal government can carry civil/criminal consequences.

Operational consequence:

> never represent an eligibility fact, source, result, authorship fact, or submission fact that we cannot support.

### Data

Official competition excerpts say:

- provided fault data may be used for training;
- evaluation uses a newly/private labeled fault set;
- external data is encouraged when the competitor/team has the necessary licenses.

Operational consequence:

- every external dataset needs retrievable provenance and a usable challenge license;
- do not silently pull in datasets whose terms are unclear.

### Prize

Total cash pool: **$300,000**.

Current official DrivenData structure:

- Initial Prize Round: five × $10,000 = $50,000;
- Final Prize Round: $100,000 / $70,000 / $40,000 / $25,000 / $15,000 = $250,000.

The same submission is scored first against a private expert-labeled test set, then against an expanded label set built through expert review of submissions.

The NLR abstract also describes the top five as eligible for the later prize pool based on contributions to new-fault discovery/corrections.

### Submission / evaluation

The rules abstract confirms that competitors submit fault-prediction results through DrivenData, which is also used to assess performance and audit submitted results.

Exact raster format and metric details live in the official problem/submission pages and are preserved separately in `GEMS.md` and `metric.py`.

## Still requiring direct PDF verification

Do **not** upgrade these from UNKNOWN/PARTIAL without the PDF text or enrolled rule page:

- exact intellectual-property language;
- exact winner documentation/payment/tax language;
- exact publicity/release language;
- exact team-member/ownership attribution provisions beyond the public captain requirement;
- exact disqualification/withdrawal/change-of-rules clauses;
- exact third-party service / generative-AI / gated-data-sharing restrictions, if any;
- any insurance, indemnity, export-control, sanctions, or conflict-of-interest clauses not exposed publicly.

## Current architectural effect

The rules tighten GEMS-001; they do not change A/B, ALL WORK, or the money/research lane boundary.

```text
GEMS work
├─ scientific/model witness
├─ competition metric witness
├─ eligibility witness
├─ license/provenance witness
└─ truthful-submission witness
```

Failure of one of those required competition witnesses can create a WALL even if the model itself is technically strong.

## Sources

- NLR publication record: https://research-hub.nlr.gov/en/publications/geologic-enhanced-mapping-system-gems-prize-official-rules/
- Official PDF: https://www.nlr.gov/docs/fy26osti/96647.pdf
- DOI: https://doi.org/10.2172/3818146
- DrivenData competition/rule excerpts: https://www.drivendata.org/competitions/306/competition-doe-gems/page/966/
- DrivenData problem/about: https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/
- HeroX official rules pointer: https://www.herox.com/GEMSPrize/resource/2274
