# Factory capacity observation — cross-repository scale entrance

This is a **read-only measurement instrument** for the existing A/B-led workstation factory. It does not add a second coordinator, replace the original research lanes, or redefine A/B. One node represents an independently observable source of work; it is not necessarily a GitHub account, an AI instance, or a scientific discipline.

The research goal is expandable source-backed investigation across scientific and other domains. No fixed count of GitHub accounts, programs, research contexts, or machines defines that scope. The 27-state finite A/B mathematical experiment and its 1–4 local processes, and the B1 workstation continuation's default 32-lane budget, are **individual bounded experiment/policy settings**; they are not a proven factory-wide limit.

## Native coordination: James typing `C` in ChatGPT windows

**The operator loop already exists.** James directs the continuation by typing `C` in ChatGPT windows. ChatGPT reads and works on the named research lanes through the available connected sources, carries back results and walls, and James can continue in that window or another. The operator's repeated `C` is a real human-supervised coordination and continuation mechanism, not a shorthand for a third compute node or a request for an unattended daemon.

```text
James types C in a ChatGPT window
  -> inspect existing lane referents, source revisions, and current evidence
  -> perform one permitted bounded next movement using connected tools
  -> preserve distinct source/worker identities and actual outcomes
  -> return what changed, what survived, the wall, and the next continuation
  -> James directs another C, possibly in a different window
```

This is **human-orchestrated, tool-mediated multi-window coordination**. It should not be misclassified as absent simply because no always-on machine-to-machine coordinator runs. Its actual behavior is supported by the operator's ChatGPT sessions, GitHub PRs and check runs; any claim that an exact return was retained in the native private journal still requires that journal's witness.

The separate [ChatGPT/workstation handoff proposal](https://github.com/huntingthereferent/autobots-assemble/pull/394) may be under review; do not replace or duplicate that protocol as a prerequisite to recognizing James's existing control loop. This document is a capacity instrument, not a new coordination authority.

The unsolved questions are **measured capacity, recoverability across context-window boundaries, exact cross-source evidence when needed, and maximum effective concurrency under the operator loop**. Automated provisioning of another node is optional future infrastructure, not a definition of whether James already coordinates the factory.

## What was confirmed at this entry

- Multiple GitHub execution identities may be observed through authorized, private connectors, but **this repository does not contain or use ChatGPT session credentials**.
- The original public repository has historical workflow records. Any additional private repository observations stay in private operator-held receipts. Historical activity is not proof that multiple systems currently interoperate as one factory.
- The source registry currently offers 21 candidate test contexts and 18 provider families. Those entries are **research opportunities**, not 21 completed studies or 18 imported datasets.
- The [A/B relational-cluster experiment](AB_RELATIONAL_CLUSTER.md) witnesses local, mathematical, relation-led expansion; it does not produce remote GitHub nodes.
- The [B1 workstation continuation](workstation_continuation.py) proposes source-witnessed lane births and connections; the receiving native worker controls evidence and admission. It does not automatically provision accounts or execute a global factory.
- The [workstation observer](research_observatory.py) indexes source records rather than equating inventory with native job evidence.

## First measurement: source-observed capacity

`factory_capacity_observer.py` consumes observations whose **in-progress and queued counts come from their separate GitHub Actions status-filtered API endpoints**. A latest-100-runs sample is **not** a live-capacity oracle. Store exact source references, local capture timestamps with offsets, and a separate record for each repository or verified compute node.

```json
{
  "schema": "ab-factory-capacity-observation/v1",
  "nodes": [
    {
      "node_id": "original-main",
      "provider": "github-actions",
      "observations": [
        {
          "captured_at": "2026-10-22T13:00:00-05:00",
          "active": 3,
          "queued": 2,
          "historical_total": 1200,
          "source_refs": {
            "active": "https://api.github.com/repos/OWNER/REPO/actions/runs?status=in_progress",
            "queued": "https://api.github.com/repos/OWNER/REPO/actions/runs?status=queued"
          }
        }
      ]
    }
  ]
}
```

**This JSON is a synthetic format example; none of the values are live evidence.** Save real observations to a **private** local JSON file if the sources include private repositories. Never commit tokens, private account run histories, unfiled invention details, or private handoff journals to the public repository.

Use a local Python 3.12+ environment:

```sh
python -m unittest -v network.tests.test_factory_capacity_observer
python -m systems.workspace.factory_capacity_observer --input /private/path/capacity.json
```

### How to interpret the result

| State | Supported meaning | Not supported |
| --- | --- | --- |
| `NO_QUEUE_OBSERVED` | Latest observed queued count was zero | No demand exists anywhere |
| `QUEUE_OBSERVED_NOT_SATURATION` | Fresh queue exists | Factory needs a new worker |
| `SUSTAINED_QUEUE_CAPACITY_UNKNOWN` | At least three queued observations over ten minutes | Provider limit or effective ceiling proven |
| `SCALE_REVIEW_CANDIDATE` | Repeated queue and active count at an **operator-declared** limit | Independent verification, authorization to create |
| `STALE` | Last observation older than 15 minutes | Any current execution state |

Node aggregation does not transfer evidence between nodes. Reported concurrency limits require independent confirmation. No output authorizes new accounts, runner provisioning, job execution, rewriting source ancestry or promotion of a science result.

## Factory-wide audit: what's built and what's open

| Layer | Existing ground | Next acceptance evidence |
| --- | --- | --- |
| Native source/language | Independent ARC, WORLD, NIH, research testing contexts | Source-versioned research inputs for each admitted topic |
| Local A/B movement | Mathematical cluster and bounded continuation harness | Independently verified source-specific transitions |
| Independent worker editions | Process Workstation source-pinned editions and native result verifier | Reproduction on actual separate execution identities |
| Human/ChatGPT window coordination | James's existing \`C\` continuation loop and source-backed GitHub work | Characterize reliable returns and capacity across windows without inventing unattended execution |
| Capacity observation | This read-only N-node adapter | Actual repeated, timestamped provider-filtered observations and independently supported effective limits |
| Node birth/return | B1 proposals, local copies and witnessed handoffs | Real cross-repo created node, operator-permitted admission, return witness and recovery test |
| Global scientific scope | 21 candidate contexts, 18 source families | Specific published studies/data records, valid rights, native independent tests |
| Factory-wide evidence | Separate source and runtime records | Cross-node lineage and negative tamper tests without collapsing native verdicts |

### Named walls

- **WALL-CAPACITY:** Effective GitHub runner and model-operation ceilings are not established by counts or public plans alone.
- **WALL-CROSS-ACCOUNT:** The existing human/ChatGPT coordination is real, but one exact machine-verifiable A → B native-journal relationship has not been established by this capacity observer.
- **WALL-PROVISION:** No validated capacity-triggered creation of a new independent execution node.
- **WALL-RETURN:** ChatGPT windows return work to James; the open issue is a *specific machine-verifiable native-journal return* from a remotely executing node, not the absence of the human control loop.
- **WALL-PLATFORM:** ChatGPT account/tool limits are externally enforced; adding GitHub repositories does not create persistent model agents.
- **WALL-GLOBAL-COVERAGE:** Candidate source families are not a verified representation of research across the planet.

The next technical measurement is **what the existing James–ChatGPT \`C\` loop can sustain across windows and repositories**. Where machine-verifiable cross-repository evidence matters, inspect an already-performed source-pinned authorized job and its independently checkable return before inventing new worker machinery. *Do not copy a public repo and label it a new worker until its separate execution, origin, and handoff are witnessed.*

We preserve prior proposals, tests, and successful limited operations. The native owner of each domain retains verdict authority. This instrument is intentionally evidence-only: `--input` reads one snapshot, and nothing in this module runs continuously or calls GitHub or ChatGPT on its own.
