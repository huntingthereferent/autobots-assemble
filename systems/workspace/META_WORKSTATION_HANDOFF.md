# Current operation — one primary workstation

The active workstation is [huntingthereferent/autobots-assemble](https://github.com/huntingthereferent/autobots-assemble). Its GitHub Actions journal and primary work viewer are authoritative. The historical secondary mirror is inactive and must not receive routed work. Historical mirror details below are retained solely for provenance; the old routing and transfer instructions are **not operational**.

# Workstation — cross-repository handoff

This file contains cross-repository source handoff records and routing references, not a separate public viewer or research lane.

**Open the regular Execution viewer:** https://huntingthereferent.github.io/autobots-assemble/live/work.html

**Canonical placement registry:** https://github.com/huntingthereferent/autobots-assemble/blob/main/docs/live/meta-registry.json

## Nodes and original evidence

| Node | Source repository | Owned journal | Source-backed viewer |
| --- | --- | --- | --- |
| Primary workstation | [huntingthereferent/autobots-assemble](https://github.com/huntingthereferent/autobots-assemble) | [Primary GitHub Actions](https://github.com/huntingthereferent/autobots-assemble/actions) | [Primary work viewer](https://huntingthereferent.github.io/autobots-assemble/live/work.html) |
| Secondary workstation | [aeren-research/continuum-oscillator](https://github.com/aeren-research/continuum-oscillator) (public as of this check) | [Secondary GitHub Actions](https://github.com/aeren-research/continuum-oscillator/actions) | [Secondary work viewer](https://aeren-research.github.io/continuum-oscillator/live/work.html) (requires Pages enabled) |

The October 22 verified A source snapshot is `ef00d95d2c2335f9f63ef2b83c8bfa5152d94bd9`. All 2,183 blobs were matched on B: 1,942 source files retain their original paths, while 241 workflow definitions are saved without activation under `.ab-cluster/workflow-library/`. B's pre-migration source is preserved on `archive/pre-workstation-sync-2026-10-22`. These are source-copy facts, not evidence that B executes A's existing research lanes.

## On each operational handoff

1. Read the **current** primary workstation's canonical `docs/live/meta-registry.json`, then B's local copy. Use the A record for declared lane allocation; report any divergence. Do not replace a newer registry with an older copy.
2. Read recent Actions runs directly from **both linked GitHub accounts** and use the regular Execution viewer for combined-source observations. Treat unavailable API responses as unknown, not zero.
3. For each lane, separate **assigned node**, **eligible workflow**, **running job**, **queued job**, **finished workflow**, **native research evidence**, and **accepted handoff**. A workflow definition sitting in B's inactive library is not a running B lane.
4. When shifting work between workstations, record lane ID, source repo/ref, destination repo/ref, actual run URL, observation/witness, decision, and open limits. Do not overwrite prior source versions; do not automatically duplicate research.
5. Use the regular Execution viewer as the single public workstation display. Each repository's GitHub Actions journal remains its authoritative execution source. Never copy private logs or credentials into public records without explicit authorization.

## Current execution boundary

The regular Execution viewer is the **single public operational screen**, not an autonomous scheduler. Its combined observations are a summary; source-owned GitHub Actions journals remain the execution evidence. It displays GitHub workflows actually visible to its source; it does not create jobs, make a second run counter authoritative, automatically start work on B, or infer scientific validity from workflow success.

**B Pages setup:** B is now public; its GitHub Actions API can be read by the regular Execution viewer. Enable Pages for B under Settings → Pages → Deploy from branch `main`, folder `/docs`. The regular Execution viewer is the primary entry point; B keeps its own detailed work page and journal. If B becomes private again, its public telemetry access may stop.

## Scale-out rule

A and B exchange reproducible source observations; any expansion to C starts from a pinned verified A/B state, not from a guessed capacity limit. New accounts and workflows must be separately authorized. Preserve node identities, historical journals, and independently admitted lanes.

## Durable shared equilibrium journal

Original's observation worker in `.github/workflows/meta-workstation-observations.yml` captures real A and B queued/running workflow-run counts every 30 minutes when GitHub Actions scheduling executes. It writes only to the `meta-observations` branch (`history.json`), avoiding commits and CI loops on `main`. The regular Execution viewer reads these observations through its combined-source reader. Data gaps mean unavailable evidence; they are not interpolated. The chart reports workflow-run counts, not concurrent job slots or an engineered capacity guarantee. This is source data for the combined execution strip, not a second dashboard.

**Settings user action:** Enable GitHub Pages on second workstation's public repository (`main`/`docs`), if not already enabled. Check that Original's repository allows its Actions `GITHUB_TOKEN` to write to its `meta-observations` branch; no personal access token needs to be pasted into a chat or public source.

## During an active ChatGPT window — route before the next batch

Before admitting each new lane task, read the current `meta-observations/routing.json` on Original and the canonical `docs/live/meta-registry.json`. The observer runs on GitHub without any viewer being open. Its latest `signal` is calculated from three independently spaced A/B workload observations (at least ten minutes apart), rather than an assumed GitHub capacity. A routing record older than 90 minutes is stale.

If `lane_advice` marks `CANDIDATE_SWITCH`, inspect the target node's actual enabled workflow and current GitHub run state, preserve the source SHA, then place **only the next eligible task** there. Never interrupt or duplicate already-running work; never activate an inactive second workstation workflow just because A is queued. If advice is unavailable, uncertain, or no workflow is admitted on the other account, stay on the assigned node.

A ChatGPT window reads this source when invoked or prompted; different ChatGPT windows cannot wake each other or see one another's unsent work automatically. Coordination happens by writing and checking GitHub branches, Actions evidence, and recorded handoffs.

Routing source: https://github.com/huntingthereferent/autobots-assemble/blob/meta-observations/routing.json

The regular Execution viewer presents combined workflow, queue and equilibrium observations. Routing decisions remain in the source records, outside the visual summary.

**Renaming a workstation repository:** update the `repo` value in the canonical `docs/live/meta-registry.json` after the GitHub rename. The source registry is consumed by the collector and regular Execution viewer's combined-source reader. Recheck the scheduled collector and the renamed repository's own `work.html` source URL afterward; do not assume a changed owner/repo slug was automatically propagated everywhere. The observer and its recommendations run independently of any phone or computer browser tab.
