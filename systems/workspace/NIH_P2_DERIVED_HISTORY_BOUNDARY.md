# NIH P2 — independent derived history corpus, not a second snapshot

## Independent source owner

[TrialTrace](https://github.com/ByungwoongYoo/trialtrace), authored by
**Byungwoong Yoo**, publishes a frozen corpus of reconstructed
ClinicalTrials.gov record-history transitions. The exact pinned revision
is `65a61a680eaffa8ccd6c9eeae11f1079c8d0e22e` (September 14, 2026).

It contains four independently published source datasets with published
SHA-256 digests, 400 study anchors, 5,629 derived transitions and 6,029
claimed source-version receipts. The reduced provenance manifest records
a source version index, retrieval UTC, the upstream author's hash of a
canonical historical payload, and a public history-page URL.

This experiment downloads all **four complete source files**, compares
each SHA-256 against the pinned upstream published digest, and independently
checks corpus counts, trial identity joins, version counts and selected
derived status transitions. It selects `NCT04153409`, a study also
selected by the earlier verified 2023 AACT source experiment. This
common identifier **does not** by itself establish matching version
identity, status-at-a-given-time, or causal change.

## Attribution and licensing

The upstream **author-created derived data are CC BY 4.0**, not owned by
this repository. Attribution: **Byungwoong Yoo, TrialTrace**,
https://github.com/ByungwoongYoo/trialtrace ,
https://creativecommons.org/licenses/by/4.0/ .
No raw table is committed or redistributed by the working source lane.
The normalized minimal receipt includes upstream attribution and license.
No third-party data license changes this repository's own copyright or
control of its code.

[Upstream third-party boundary](https://github.com/ByungwoongYoo/trialtrace/blob/65a61a680eaffa8ccd6c9eeae11f1079c8d0e22e/THIRD_PARTY_DATA.md).

## What evidence is and is not available

The original raw ClinicalTrials.gov **historical record payloads are
not included** in TrialTrace's public GitHub repository. The manifest
contains upstream-computed payload digests, but those cannot be
independently reproduced from unavailable original source bytes.

Therefore:

- **Verified if CI passes:** provenance and integrity of a distinct
  third-party, author-derived frozen transition corpus, with exact
  public version links and recorded dates as claimed by the author.
- **Not independently verified:** authenticity of the historical
  ClinicalTrials.gov version contents, exact dates each amendment
  became publicly visible, or an independent adjudicated temporal
  ground truth.
- **Not a second dated original AACT snapshot:** this is a frozen
  reconstructed history corpus, not a second `studies.txt` extract.
- **Not an NIH checkpoint, submission or clinical conclusion:** all
  original twelve source-owned workstation jobs remain unchanged.

Derived `history_version_date` and a reconstructed posted-state flag
are retained **as upstream-derived assertions**. They must never be
used as authenticated `known_at` cutoffs until publication timing is
independently sourced.

The archive investigation in
[issue #106](https://github.com/huntingthereferent/autobots-assemble/issues/106)
remains open. The earlier directly verified
[2023 AACT dataset](https://github.com/huntingthereferent/autobots-assemble/pull/109)
is the historical *snapshot* witness. [PR #107](https://github.com/huntingthereferent/autobots-assemble/pull/107)
retains the site's HTTP-403-refused historical version endpoint.

## Reproduce

```bash
python -m unittest -v network.tests.test_nih_derived_history_receipt
python -m systems.workspace.nih_derived_history_receipt \
  --output-dir /tmp/nih-derived-history
```

The first command uses deliberately invalid local fixtures for negative
controls; it is not a verified external source read. The second
downloads pinned upstream files from GitHub and checks exact hashes.
A missing or altered file must fail closed. The resulting evidence is
a small report without raw third-party tables.
