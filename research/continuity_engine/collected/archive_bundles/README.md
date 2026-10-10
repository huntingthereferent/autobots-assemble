# Original research bundle preservation

This directory contains the **original ZIP artifacts**, kept verbatim as evidence alongside the separately imported plaintext scripts and reports.

- 15 Continuity/Cyclic research ZIP bundles; 1 separate factory bridge prototype retained as an adjacent artifact, **not** installed as Continuity Engine code.
- Total archive bytes: 780,414.
- Each archive Git blob SHA-1 was computed from the literal Git blob header and original bytes and verified against GitHub's response. SHA-256 records allow independent byte-for-byte audits.
- These archives include previous local iterations, bundled datasets and tests, and historical duplicates. **Archiving does not mean the contained modules are production-integrated or independently validated.**
- The existing Cyclic Action production implementation and frozen research board have not been replaced.

Run `python -m research.continuity_engine.collected.archive_sources` only if that specific runnable module exists; instead, use the existing documented `python research/continuity_archive_import.py --source <downloaded-zip-folder> --destination <separate-worktree> --stage` importer for safe, deliberate extraction.

Binary archive placement does **not** require all embedded files to become active Python modules. The extracted members should remain separately namespaced until compatibility with the current repository is verified.

See [MANIFEST.json](MANIFEST.json) for exact per-file sizes and hashes.
