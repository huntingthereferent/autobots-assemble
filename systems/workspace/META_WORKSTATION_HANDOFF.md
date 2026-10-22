# Meta workstation — A / B handoff

This file is installed in **both** workstations. It is the cross-window reground point for the meta workstation, not a new research lane.

**Open the shared meta viewer:** https://huntingthereferent.github.io/autobots-assemble/live/meta.html

**Canonical placement registry:** https://github.com/huntingthereferent/autobots-assemble/blob/main/docs/live/meta-registry.json

## Nodes and original evidence

| Node | Source repository | Owned journal | Source-backed viewer |
| --- | --- | --- | --- |
| A / Original | [huntingthereferent/autobots-assemble](https://github.com/huntingthereferent/autobots-assemble) | [A GitHub Actions](https://github.com/huntingthereferent/autobots-assemble/actions) | [A work viewer](https://huntingthereferent.github.io/autobots-assemble/live/work.html) |
| B / Dessy | [aeren-research/continuum-oscillator](https://github.com/aeren-research/continuum-oscillator) (private) | [B GitHub Actions](https://github.com/aeren-research/continuum-oscillator/actions) (login) | [B copied viewer source](https://github.com/aeren-research/continuum-oscillator/blob/main/docs/live/work.html) |

The October 22 verified A source snapshot is `ef00d95d2c2335f9f63ef2b83c8bfa5152d94bd9`. All 2,183 blobs were matched on B: 1,942 source files retain their original paths, while 241 workflow definitions are saved without activation under `.ab-cluster/workflow-library/`. B's pre-migration source is preserved on `archive/pre-workstation-sync-2026-10-22`. These are source-copy facts, not evidence that B executes A's existing research lanes.

## On every reground / new ChatGPT window

1. Read the **current** A canonical `docs/live/meta-registry.json`, then B's local copy. Use the A record for declared lane allocation; report any divergence. Do not replace a newer registry with an older copy.
2. Read recent Actions runs directly from **both linked GitHub accounts**, not only the public viewer. The browser can read A's public API; B is private and its live API requires an authorized GitHub connection. Do **not** report missing B API access as zero jobs.
3. For each lane, separate **assigned node**, **eligible workflow**, **running job**, **queued job**, **finished workflow**, **native research evidence**, and **accepted handoff**. A workflow definition sitting in B's inactive library is not a running B lane.
4. When shifting work A ↔ B, record lane ID, source repo/ref, destination repo/ref, actual run URL, observation/witness, decision, and open limits. Do not overwrite prior source versions; do not automatically duplicate research.
5. Use the shared meta viewer as the public, navigation-grade display. The private B GitHub Actions journal remains the authoritative source for B. Never copy private logs or credentials into A's public repository without explicit authorization.

## Current execution boundary

The meta workstation is a **source-owned coordination and observation page**, not an autonomous scheduler. It displays GitHub workflows actually visible to its source; it does not create jobs, make a second run counter authoritative, automatically start work on B, or infer scientific validity from workflow success.

**B Pages caveat:** B is private. A public GitHub Pages viewer cannot fetch private GitHub Actions or treat GitHub sign-in as an API token. Until an explicitly authorized read-only summary feed is added, the meta page shows B as **private / source not available**, with links to its real GitHub journal. The same meta page is copied into B's `docs/live/meta.html`, and both can open A's shared viewer.

## Scale-out rule

A and B exchange reproducible source observations; any expansion to C starts from a pinned verified A/B state, not from a guessed capacity limit. New accounts and workflows must be separately authorized. Preserve node identities, historical journals, and independently admitted lanes.
