# Checkpoint output contract — finite correspondence research

This contract applies **only** when the current referent is this finite correspondence research branch. It connects each completed CP to the branch's own [About Me](../ABOUT_ME.md) and [Provenance](../PROVENANCE.md). **Never write to James's personal GitHub profile.** Any user-facing application is separate from this branch's research identity.

The [Finite Correspondence Process](../PROCESS.md) names the bounded implementation; a Correspondence Worker is that process only when explicitly assigned work through an admitted boundary. Neither title changes existing CP identifiers, evidence standards, or this research branch's identity.

A CP is not a marketing summary or a request for proof of the complete language referent. Record the current observation, changed relations, what survives, the exact wall/unknown state, the actual tests, and the next supported movement. Distinguish the local integrated owner-backed implementation from standalone finite GitHub references.

## Harness exit sequence (required after a completed CP)

1. Complete the bounded work and run its tests; save runnable source and outputs. Preserve the prior CP's evidence.
2. Prepare a public CP JSON manifest matching [CP-0027.json](CP-0027.json) with the **next sequential number**. `summary`, `observation`, `preserved`, `boundary`, and `next` are short records, not a mandatory narrative. Only include facts actually witnessed in that CP.
3. Confirm the manifest contains no private names, private conversations, passwords, or credentials. The manifest, About Me, and provenance are **public**. Preserve private details somewhere else, if necessary.
4. Run this from the existing research directory (`work/arc_like_maze/chatbot`, retained for compatibility):

   ```sh
   python checkpoints/cp_record.py record /path/to/CP-0028.json
   python checkpoints/cp_record.py check
   python -m unittest -q checkpoints.test_cp_record
   ```

5. Commit **the manifest, research `ABOUT_ME.md`, research `PROVENANCE.md`, source/tests, and evidence record together**. If publishing via a different system or tool, apply the same updates to the canonical GitHub paths. Keep the integrated ZIP separately represented by its verified SHA-256; the hash is not a download link.
6. Read back the committed files and confirm the expected CP is at the top of About Me and in the provenance ledger. A failed update is an explicit `CP_WALL`; do not tell the user the CP was published.

`cp_record.py check` is wired into GitHub Actions for pushes/PRs touching this branch's files; it fails if a CP manifest is committed without updating both views. The automation **validates a submitted change**; it does not invent a CP, run external integrated observations, modify unrelated pages, or silently push to GitHub.

Use `python checkpoints/cp_record.py sync` only to reconstruct views from already recorded CP manifests after reviewing the diff. Do not edit old CP manifests to change history: add a new CP that records the correction. `record` refuses to overwrite or skip CP numbers, and refuses accidental same-number divergent output.

When a checkpoint is not complete, say PARTIAL/WALL and preserve the evidence; do not create a fictional completed CP. CP JSON `status` may be `partial`, `blocked`, or `witnessed` when the observed state genuinely warrants a record.
