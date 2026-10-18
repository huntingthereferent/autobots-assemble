# NIH P2: cross-source observation relations (not reconstructed history)

## Real sources and their independently verified origin

This experiment joins **two separately attributed external evidence categories**:

1. **Dated 2023 AACT third-party archive**: the [Zenodo deposit
   10.5281/zenodo.10058991](https://zenodo.org/records/10058991),
   with complete-file depositor MD5 and SHA-256 from [PR
   #109](https://github.com/huntingthereferent/autobots-assemble/pull/109).
   This is a frozen dataset observation, not a per-study historical version
   and not proof of an individual status amendment's public posting time.
   The experiment fetches the complete original archive again.
2. **Independent author-derived historical transitions**:
   [Byungwoong Yoo, TrialTrace](https://github.com/ByungwoongYoo/trialtrace)
   at exact source commit `65a61a680eaffa8ccd6c9eeae11f1079c8d0e22e`,
   under **CC BY 4.0** for the *author-created derived tables*
   ([license](https://creativecommons.org/licenses/by/4.0/)).
   [PR #115](https://github.com/huntingthereferent/autobots-assemble/pull/115)
   independently validated all four published source SHA-256 digests.
   TrialTrace does **not** distribute the original ClinicalTrials.gov
   historical responses; its version dates, posted flags and payload hashes
   must remain **upstream-derived** claims.

The AACT experiment separately retrieves the **current** official
ClinicalTrials.gov API v2 status as another observation at its own
retrieval time.

## What the relationship is

`NCT04153409` appears in both source families. For that same exact NCT
identifier, we compare the **spelling** of the 2023 archive's
`overall_status`, the current official API status, and the
before/after status values in TrialTrace's derived transitions.

A spelling match demonstrates **only a matching field value**. It does
**not** attach the 2023 snapshot to a specific TrialTrace version, prove
the version's posting date, decide that an underlying clinical status
changed on the upstream derived date, or provide a clinical inference.
Nonmatches likewise do not disprove the external source history.

The output deliberately sets:
- `historical_status_corresponds_to_unique_version: false`
- `historical_record_contents_independently_authenticated: false`
- `public_posting_time_of_change_known: false`
- `clinical_event_time_known: false`
- `two_independent_original_historical_snapshots_available: false`

It re-runs source verification on every live CI attempt: a pinned whole-file
AACT digest, distinct official current NCT response hash, and four pinned
third-party corpus hashes. Unit mocks are negative controls, **not**
independently admitted evidence.

## Research boundary

This produces a small attributed **cross-source observation relation**;
it is not a second dated original archival study snapshot and is not a
historical-content oracle for `NIH-P2-BENCHMARK`. No additional
source-owned native workstation job, claim of general biomedical
performance, patient data, clinical conclusion, or official NIH grant/
submission is created.

[Issue #106](https://github.com/huntingthereferent/autobots-assemble/issues/106)
remains open for an independently verifiable *second original archival
capture* or *actual version-specific historical record bytes and public
posting timestamps*. Without those, `known_at` for the disputed
historical transition cannot be established.

## Repeat

```bash
python -m unittest -v network.tests.test_nih_cross_source_relations
python -m systems.workspace.nih_cross_source_relations \
  --output-dir /tmp/nih-cross-source
```

The second command needs network access and downloads the complete verified
2023 archive. It preserves only the minimal receipts and relationship
report, not the full third-party tables or raw clinical records.
