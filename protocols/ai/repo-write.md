# AI Protocol — Repository Write

## Purpose

Prevent a write from destroying the relation/provenance structure the repository is meant to preserve.

Repository additions are also subject to `ai.james`. Cleanup/removal review is governed separately by `ai.purge`.

## Before writing

- identify the canonical record being changed;
- identify whether the write is source, evidence, generated view, protocol, or historical archive;
- for additions, honor James-only scope and a current explicit instruction to make the specific change; no special word is required;
- preserve the old evidence unless the file is explicitly generated/replaceable;
- do not move a claim to a stronger status without evidence.

## After writing

- record the resulting commit/artifact;
- update generated views only from canonical records;
- leave a next movement or explicit wall;
- validate links/tests relevant to the changed layer.

Large binaries may live outside ordinary Git when tooling requires it, but their hashes and provenance must remain represented in the repository.
