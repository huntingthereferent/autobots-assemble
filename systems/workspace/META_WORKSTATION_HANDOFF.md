# Meta workstation — A / B handoff

This file is installed in **both** workstations. It is the cross-window reground point for the meta workstation, not a new research lane.

**Open the shared meta viewer:** https://huntingthereferent.github.io/autobots-assemble/live/meta.html

**Canonical placement registry:** https://github.com/huntingthereferent/autobots-assemble/blob/main/docs/live/meta-registry.json

## Nodes and original evidence

| Node | Source repository | Owned journal | Source-backed viewer |
| --- | --- | --- | --- |
| A / Original | [huntingthereferent/autobots-assemble](https://github.com/huntingthereferent/autobots-assemble) | [A GitHub Actions](https://github.com/huntingthereferent/autobots-assemble/actions) | [A work viewer](https://huntingthereferent.github.io/autobots-assemble/live/work.html) |
| B / Dessy | [aeren-research/continuum-oscillator](https://github.com/aeren-research/continuum-oscillator) (public as of this check) | [B GitHub Actions](https://github.com/aeren-research/continuum-oscillator/actions) | [B work viewer](https://aeren-research.github.io/continuum-oscillator/live/work.html) (requires Pages enabled) |

The October 22 verified A source snapshot is `ef00d95d2c2335f9f63ef2b83c8bfa5152d94bd9`. All 2,183 blobs were matched on B: 1,942 source files retain their original paths, while 241 workflow definitions are saved without activation under `.ab-cluster/workflow-library/`. B's pre-migration source is preserved on `archive/pre-workstation-sync-2026-10-22`. These are source-copy facts, not evidence that B executes A's existing research lanes.

## On every reground / new ChatGPT window

1. Read the **current** A canonical `docs/live/meta-registry.json`, then B's local copy. Use the A record for declared lane allocation; report any divergence. Do not replace a newer registry with an older copy.
2. Read recent Actions runs directly from **both linked GitHub accounts** and use the shared meta viewer for the two public feeds. Treat unavailable API responses as unknown, not zero.
3. For each lane, separate **assigned node**, **eligible workflow**, **running job**, **queued job**, **finished workflow**, **native research evidence**, and **accepted handoff**. A workflow definition sitting in B's inactive library is not a running B lane.
4. When shifting work A ↔ B, record lane ID, source repo/ref, destination repo/ref, actual run URL, observation/witness, decision, and open limits. Do not overwrite prior source versions; do not automatically duplicate research.
5. Use the shared meta viewer as the public, navigation-grade display. The private B GitHub Actions journal remains the authoritative source for B. Never copy private logs or credentials into A's public repository without explicit authorization.

## Current execution boundary

The meta workstation is the **default operational screen** for both nodes, not an autonomous scheduler. It shows a combined observed equilibrium timeline and both source-owned GitHub job journals; it is not the sole research proof. It displays GitHub workflows actually visible to its source; it does not create jobs, make a second run counter authoritative, automatically start work on B, or infer scientific validity from workflow success.

**B Pages setup:** B is now public; its GitHub Actions API is readable by the same meta viewer. Enable Pages for B under Settings → Pages → Deploy from branch `main`, folder `/docs`. The shared meta viewer is the primary entry point; B keeps its own detailed work page and journal. If B becomes private again, its public telemetry access may stop.

## Scale-out rule

A and B exchange reproducible source observations; any expansion to C starts from a pinned verified A/B state, not from a guessed capacity limit. New accounts and workflows must be separately authorized. Preserve node identities, historical journals, and independently admitted lanes.

## Durable shared equilibrium journal

Original's observation worker in `.github/workflows/meta-workstation-observations.yml` captures real A and B queued/running workflow-run counts every 30 minutes when GitHub Actions scheduling executes. It writes only to the `meta-observations` branch (`history.json`), avoiding commits and CI loops on `main`. The meta page shows that historical line plus live browser checks. Data gaps mean unavailable evidence; they are not interpolated. The chart reports workflow-run counts, not concurrent job slots or an engineered capacity guarantee. This is the default dashboard; each original viewer remains an inspection drilldown.

**Settings user action:** Enable GitHub Pages on Dessy's public repository (`main`/`docs`), if not already enabled. Check that Original's repository allows its Actions `GITHUB_TOKEN` to write to its `meta-observations` branch; no personal access token needs to be pasted into a chat or public source.
