# Reading guide — terms, claims, and evidence

This page explains the words used in the public project guide and ordinary READMEs. **It does not supersede** mathematical definitions, [the Language Referent evidence contract](../LANGUAGE_REFERENT_CONTRACT.md), [category rules](../CATEGORY_CONTRACT.md), the [entry protocol](../ENTRY.md), or source-specific research contracts.

## Use the specific word when possible

| Term | What it means in a particular record | Prefer in general introductions |
| --- | --- | --- |
| Referent | The subject or relationship currently being followed. Specific mathematical referents have their own exact definitions. | The actual problem or relationship, when that is clearer |
| A/B / Language Referent | Two names used for the same continuing inquiry. Local mathematical operators named A and B are separately defined inside their models. | Language Referent (earlier name: A/B) on first use |
| Finite / bounded | Restricted by an explicit state space, domain, time horizon, action count, evidence scope or other declared limit; not necessarily an informal synonym for small. | State the actual limit |
| Correspondence | A proposed relationship between specified records, states or objects, under stated evidence conditions. | State what corresponds to what |
| Handoff | A declared carrier for work, its requirements, receiving actor and evidence-bearing return. | Handoff, followed by what is passed and to whom |
| Native run | An execution of the named original SDK, implementation or worker, rather than a substituted demonstration. | Name the actual SDK/program and the run |
| Witness | Particular evidence supporting a particular relationship or outcome. | Observation, test result, source file or artifact, as applicable |
| Provenance | Recoverable source, version, ancestry and reason for a recorded result or change. | Source and history, when sufficient |
| Wall | A documented limit: missing evidence, unresolved dependency, lack of authority, inaccessible source or failed check. | Name the missing evidence or dependency |
| Movement | A source-recorded operation or supported step; not proof that the whole project advanced. | Describe the operation or change |
| Source-owned | A claim or result attributed to the system, file, team or authority that generated it. | Name the actual source and its responsibility |
| Projection / view | A presentation derived from recorded data; it is not the data's authority. | Read-only view, chart or index |
| Swallow | Historical internal shorthand used in some files for different source intake or reconstruction operations. It is not one technical guarantee. | Inspect, import, compare, reconstruct or adapt—whichever was actually done |

Retain exact words inside historical records, code identifiers, formal contracts and quotations that remain intentionally published. Do not silently rewrite evidence to make the past agree with current vocabulary.

## Claim types are not interchangeable

| Reported state | Safe interpretation |
| --- | --- |
| Designed or represented | A description, specification or model exists |
| Implemented | Source code or an artifact exists |
| Tested | The named checks executed at a recorded version; inspect their actual scope |
| Simulated | Behavior observed in the declared model or simulation |
| Native observed | Behavior returned by the named original implementation |
| Independently replayed / checked | A separate stated check was performed on the stated evidence |
| Published | Available at a stated location; not necessarily running or production-ready |
| Deployed / operating | A specifically identified live system was observed operating |
| Unknown / partial | The record does not establish the stronger claim |
| Historical / pinned | Preserved evidence or a possible return point, not automatic current work |

A run passing its tests does not prove an unrelated research claim. A content hash identifies bytes but does not by itself establish authorship. A simulation of a collision is not a physical impact. A saved game route is not necessarily independent discovery of the route.

## Project README pattern

Every active project overview should let a new reader answer these questions without reconstructing a long chronological record:

1. **Purpose:** What specific question, system or experience is this for?
2. **Implemented now:** What source or user-facing capability actually exists?
3. **Verified evidence:** What exact observation or check supports the summary, with a source link?
4. **Limits:** What has not been demonstrated?
5. **Next question or operation:** What remains to test or build, without pretending it is scheduled?
6. **Reproduce / inspect:** Where are the relevant source, commands, outputs and artifacts?

Put detailed dated evidence, previous states and counterexamples **below** that summary or in source-owned records. Don't delete old evidence to make a landing page shorter. Avoid calling a section “latest” unless it is maintained as new results arrive; otherwise give its date.

## Reader and implementation boundaries

The [public viewer](live/README.md) can show published source data and GitHub run records. The authorized local workstation can hold private process journals and editable source editions. The existence of a public page does not imply access to those local records, permission to execute workers, or continuous monitoring.

Personal public writing belongs in the [separate current writing archive](https://github.com/huntingthereferent/huntingthereferent/blob/main/writing/README.md). Retired or withdrawn personal quotations must not be reconstructed from older repository history into reader-facing summaries.

The [license](../LICENSE) reserves rights to the original material. Third-party source rights remain separate.
