# Tracework: native evidence retention for this GitHub version

This public GitHub proof of concept retains **source pointers, native return receipts, and failure history**, but GitHub Actions download artifacts expire separately from Git commits. A run URL or copied numerical summary does **not** preserve the original witness bytes. This is an operating-boundary defect in the GitHub version, not a new mathematical conjecture.

## Native-witness preservation contract

For specifically approved public evidence workflows:

```text
native experiment + bounded source revision
  → original Actions run ID, attempt, source commit and conclusion
  → exact original artifact ZIP (never executed or extracted by the archivist)
  → bounded filename/size checks + SHA-256 of ZIP and every member
  → release assets: original ZIP + source-bound JSON manifest
  → read back release ZIP/manifest and verify hashes and source identity
  → recorded preserved copy OR visible failing archival workflow
```

An archival workflow succeeding is **not** evidence that the native experiment succeeded. Failed experiments retain `original_conclusion: failure`; a verified copy has `claim: copied original artifact; no new native execution or verification`. A run can be genuine while an attempted experiment does not reach WIN. Recording the negative result without altering it is the point of this interface.

### What this version implements

- [Source and artifact validation](../systems/workspace/github_native_evidence_archive.py) checks same-repository and source-owner provenance, exact workflow path/name, original source SHA, run attempt, conclusion, artifact ID, expiry status, and bounded ZIP member identities. No arbitrary archive content is executed.
- [Archive/reverification runner](../scripts/tracework_archive_native_evidence.sh) uses the original GitHub API to copy artifact bytes to a run+attempt-specific GitHub Release, then downloads the release and verifies its content again. No `--clobber` operation replaces historical evidence.
- [GitHub Actions retention workflow](../.github/workflows/tracework-durable-native-evidence.yml) starts after **approved source workflows** finish. A daily scheduled pass repairs missed eligible native runs; manual dispatch accepts an explicit run ID. The workflow's `contents: write` permission is scoped to this trusted archive job, not source-executing PR jobs.
- [Adversarial contract tests](../network/tests/test_github_native_evidence_archive.py) reject foreign workflow paths, forked sources, wrong actor, missing or expired artifacts, and altered ZIP members. They also keep terminal failed results marked as failures.

**Approved native workflows in this iteration:** original ARC SP80 level-4 entry, original ARC SP80 level-4 follow-up, original WORLD31 first conservative bound, and the W13 independent browser witness. Other workflows are **not silently considered archived**. A new source workflow must be explicitly evaluated for public release safety, input files, and output bounds before being added. Private operator journals use the separate encrypted owner-vault contract and must not be copied into public Releases.

### Backfill for the October 2026 artifacts

The recovery schedule explicitly includes the original run IDs:

| Evidence boundary | Run | Original Actions artifact expiry (GitHub-reported) |
| --- | ---: | --- |
| ARC 2/50 official level-4 returns | [39616395169](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39616395169) | November 4, 2026 |
| ARC 0/52 level-5/WIN follow-up | [39636174534](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39636174534) | November 4, 2026 |
| WORLD31 conditional analytical bound | [39531157339](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39531157339) | November 20, 2026 |
| W13 independent browser evidence | [39000587000](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39000587000) | November 16, 2026 |

The preservation workflow is **not active until this branch is merged into the default branch**. Immediately after merging, use **Actions → Tracework durable native evidence → Run workflow**, leaving run ID blank to reconcile the four historical runs plus recent approved workflows. Inspect the published Release assets and the Action's source-bound verification result. Daily runs are a second chance, not a reason to delay preserving an artifact about to expire.

## Admission and limits

Source code, a green job, an original witness, an independent verifier, and preservation of a witness are different achievements. The archive keeps the original workflow's conclusion and hashes; it does not substitute for the SDK/environment, replay all original actions, independently verify physics, or repair a lost native return.

GitHub Release assets remain subject to repository access, service behavior, and authorized administrative deletion. This is a **separately retained, checked copy**, not a mathematical guarantee of forever-available storage. For high-value research, maintain an additional off-GitHub backup and periodically compare digests. A missing or expired artifact must be reported as an unresolved evidence wall, never silently replaced with a new result.

This adapter belongs at the **GitHub/source provenance boundary** of [Tracework](../TRACEWORK.md), alongside the [source-owned evidence discipline](../protocols/core/provenance.md). It is not a new mathematical A/B operation, an additional worker, or a replacement for the domain-specific native evaluator.
