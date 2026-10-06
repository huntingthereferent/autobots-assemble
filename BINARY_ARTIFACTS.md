# Large / Binary Artifact Policy

Git is the canonical source for protocols, state contracts, job records, code, tests, and lightweight evidence.

The frozen v0.17 package also contains Excel workbooks, PDFs, preview images, SQLite databases, bytecode, and large generated fixtures. The current GitHub write path is text-oriented, so those artifacts are not all duplicated into ordinary Git.

They are **not treated as nonexistent**.

## Frozen evidence bundle

- archive: \`ab_language_network_v0_17.zip\`
- files: 185
- binary files: 33
- SHA-256: \`21dda01da3c932d7ad32ab92e90ea4414669df296bac5af6fdced05c67189040\`

See \`evidence/archive/v0.17-summary.json\` and \`MIGRATION.md\`.

## Rule

If a current movement needs a binary artifact, retrieve that artifact from the frozen evidence bundle, verify it against the archive/provenance boundary, and then use it as evidence for the current referent.

Do not upgrade a job claim merely because an artifact filename is listed.
