# NIH Phase 2 — two independently authenticated AACT source snapshots

**Source-owned comparison, not a clinical outcome and not a registry change-time oracle.**

## Why this experiment exists

[PR #109](https://github.com/huntingthereferent/autobots-assemble/pull/109) independently downloaded and verified a complete [October 31, 2023 Zenodo AACT `studies.txt` export](https://zenodo.org/records/10058991). [PR #138](https://github.com/huntingthereferent/autobots-assemble/pull/138) independently authenticated a second source: [Cathrine Axfors and Gustav Nilsonne, *Nordic trial reporting project*, Zenodo 10.5281/zenodo.10091147](https://zenodo.org/records/10091147), a complete 236 MB ZIP containing a `studies.txt` table described as reflecting **November 9, 2022**.

The 2022 archive was **retrieved by its original depositors November 27, 2022 and deposited on Zenodo November 9, 2023**. Those distinct dates are preserved. Neither the depositor's claimed dataset date nor Zenodo's deposit publication timestamp proves when a specific NCT study version first became publicly accessible on the primary registry.

## What is independently computed

This work runs the two **existing source-intake algorithms**: [original 2022 ZIP source](nih_aact_second_2022_archive.py), verified by published MD5 `1d4e6d141f40d300186fdd3d0a5980b1` and computed whole-file SHA-256 `d1d4fb04a121e03f2ac08bacef708a896f7240d5ff025104ed7512b60408d755`; and [original 2023 flat-file export](nih_aact_archival_source.py), verified by published MD5 `d043fb7704bcff8cfb5be95d4f5ced85` and whole-file SHA-256 `bed698312a04292fc31f7ea71130731acc9b57723399ab1b45c0f6d70a304d49`.

The two **complete sources** are re-downloaded and reverified on a new GitHub runner, before parsing only **two predeclared public study IDs**, `NCT03280849` and `NCT04153409`. The join records:

- Exact recorded `overall_status` in each independently dated archive.
- Whether those *recorded field spellings* are equal across the two archives.
- `last_update_posted_date` as recorded in each export, with separate value equality reporting (not relabeled as first posting of a particular historical version).
- The original source owners, deposit identifiers, stated collection date, actual deposit-publication date, and whole-file hash.
- The missing original-version evidence and fact that *equal endpoints do not exclude intervening changes*.

## What the verified previous CI receipts already showed

From [2022 source execution](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39160715819) and [2023 source execution](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39093391150), both selected archived statuses were `Completed` in both sources. This is a **negative endpoint-status result**, not evidence that there were no intervening registry versions, corrections, or administrative events. This new dedicated replay must complete independently before any pairwise output is called a new witnessed result.

## Scientific and rights boundaries

Two dated complete historical source exports are now verified, but source-owner claims about the collection dates are **not** independent original per-study posting timestamps. Neither source retains an authenticated sequence of all original per-study version contents. Equal archived statuses cannot establish that no intermediate update occurred. A recorded `last_update_posted_date` is metadata present in the snapshot, not verification of an exact source publication transaction or of an event in the clinical world.

The third-party datasets have their **own external ownership and reuse conditions**, which should be independently reviewed. Only selected minimal public study status metadata and whole-source hashes are placed in new research receipts. A/B's repository license and its original twelve source-owned workers are not changed. No clinical conclusions, production biomedical performance claims, official NIH entry, or new native workstation checkpoint are made.

[Issue #106](https://github.com/huntingthereferent/autobots-assemble/issues/106) should remain open for original study revision payloads plus independently authenticated per-version publication time, or an explicitly bounded alternative temporal evaluation question.

## Execute

```sh
python -m unittest -v network.tests.test_nih_p2_two_aact_snapshot_comparison
python -m systems.workspace.nih_p2_two_aact_snapshot_comparison \
  --output-dir /tmp/nih-p2-two-original-archives
```

The real experiment requires downloads of roughly **525 MB** and produces a small attributed JSON receipt. Negative controls alone do not establish live archival correctness.
