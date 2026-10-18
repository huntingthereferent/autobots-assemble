# NIH P2 — exact historical version evidence

This is a follow-on to the public current-record posting-date source intake,
not a thirteenth native workstation job, NIH submission, or clinical benchmark.

## Source-owner research

The R package **ctrdata** (published source as of August 2026) implements
retrieval of version-specific ClinicalTrials.gov history responses. Its
`ctrLoadQueryIntoDbCtgov2.R` source shows two **site-internal endpoints**:

- `https://www.clinicaltrials.gov/api/int/studies/{NCT}?history=true`
  for the version index with `history.changes[].version` and `.date`;
- `https://www.clinicaltrials.gov/api/int/studies/{NCT}/history/{version}`
  for a specific response with `studyVersion` and `study` content.

Source: [ctrdata's published code](https://rdrr.io/cran/ctrdata/src/R/ctrLoadQueryIntoDbCtgov2.R),
the historical-import implementation around its history download block.
These are **undocumented site-internal routes**, not a promised supported API.
They may reject requests or change their response shape. Such a failure is
evidence that this attempt is unavailable, not evidence that a version exists.

## Experiment

For a bounded selected study ID, fetch the actual index; select earliest and
latest declared version numbers; then separately fetch **each exact source
version**. Fail unless both responses contain:

- the requested `studyVersion` index;
- the matching public NCT identifier **inside that version's contents**;
- a bounded nonempty `statusModule.overallStatus` string extracted *from that
  exact historical response*, not copied from a current public API result;
- the raw response's SHA-256, exact source URL, index submission date, and
  UTC retrieval time.

The output preserves only these minimal fields and their source-provenance
digests. Full study responses, contacts, diagnoses, outcomes and subjects are
not archived. CI separately exercises mock changes and negative controls, then
**must retrieve real version responses** to admit the source. No mock may be
treated as real source evidence.

## Important time distinction

The version index exposes **submission dates**. A submission date is *not*
the exact date a version became publicly posted or generally knowable.
Consequently, even successfully retrieved historical contents cannot yet
support a public-knowledge `known_at` claim at their submission timestamps.
The output sets the posting date to null and public availability to
`NOT_ESTABLISHED`.

A future external temporal benchmark requires independently established
**public posting/availability dates for each version**, or a separately
grounded observation-as-of snapshot. Only then can we align specific
historical content with its trustworthy knowledge cutoffs. The current study
API v2 is explicitly a **most-recent-version** source and is not used as a
historical record substitute.

See [issue #106](https://github.com/huntingthereferent/autobots-assemble/issues/106)
for the unresolved source-owner evidence and independent-oracle criteria.

## Actual live attempt and refusal (October 18, 2026 UTC)

[Independent GitHub CI run 39092821376](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39092821376)
passed the five local negative-control tests, then attempted to
retrieve the exact history index for `NCT03280849` from the internal
site endpoint. The server returned **HTTP 403 Forbidden**.

Therefore, the source is **UNAVAILABLE** from this GitHub runner.
No history index, historical version contents, historical source hashes,
or public posting times have been independently observed or admitted.
A subsequent test may capture a restricted `UNAVAILABLE` receipt
artifact while keeping the live-source gate **failed**.

The next possible source is a published CTTI/AACT archive or another
authenticated snapshot with exact source and capture version identifiers.
Do not attempt to bypass access restrictions or substitute modern
current-record data for actual history.

## Reproduction

```bash
python -m unittest -v network.tests.test_nih_historical_version_evidence
python -m systems.workspace.nih_historical_version_evidence \
  --output-dir /tmp/nih-p2-historical-source
```

The second command requires external network access to a site's
**undocumented** history routes. If it fails, report the specific unavailable
source boundary. Never fill in prior contents from the current record.
