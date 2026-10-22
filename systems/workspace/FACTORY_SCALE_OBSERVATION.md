# Factory capacity observation — cross-repository scale entrance

This is a **read-only measurement instrument** for the existing A/B-led workstation factory. It does not add a second coordinator, replace the original research lanes, or redefine A/B. One node represents an independently observable source of work; it is not necessarily a GitHub account, an AI instance, or a scientific discipline.

The research goal is expandable source-backed investigation across scientific and other domains. No fixed count of GitHub accounts, programs, research contexts, or machines defines that scope. The 27-state finite A/B mathematical experiment and its 1–4 local processes, and the B1 workstation continuation's default 32-lane budget, are **individual bounded experiment/policy settings**; they are not a proven factory-wide limit.

## What was confirmed at this entry

- GitHub has two connected account identities available to the ChatGPT session, but **this repository does not contain or use ChatGPT session credentials**.
- The original public repository and the separate account's `continuum-oscillator` repository have historical workflow records. Historical activity is not proof that both systems are currently interoperating as one factory.
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
| Two GitHub identities | Existing connected accounts; historical workflow runs | Exact cross-repository handoff with both original source identities |
| Capacity observation | This read-only N-node adapter | Actual repeated, timestamped provider-filtered observations and independently supported effective limits |
| Node birth/return | B1 proposals, local copies and witnessed handoffs | Real cross-repo created node, operator-permitted admission, return witness and recovery test |
| Global scientific scope | 21 candidate contexts, 18 source families | Specific published studies/data records, valid rights, native independent tests |
| Factory-wide evidence | Separate source and runtime records | Cross-node lineage and negative tamper tests without collapsing native verdicts |

### Named walls

- **WALL-CAPACITY:** Effective GitHub runner and model-operation ceilings are not established by counts or public plans alone.
- **WALL-CROSS-ACCOUNT:** Current observed activity is not a verified source-preserving A → B handoff.
- **WALL-PROVISION:** No validated capacity-triggered creation of a new independent execution node.
- **WALL-RETURN:** No evidenced A/B return from a freshly provisioned remote node into the originating research lane.
- **WALL-PLATFORM:** ChatGPT account/tool limits are externally enforced; adding GitHub repositories does not create persistent model agents.
- **WALL-GLOBAL-COVERAGE:** Candidate source families are not a verified representation of research across the planet.

The next real experiment is **one source-pinned, authorized cross-repository job** with an independently checkable acceptance receipt and a verified return to the originating lane. *Do not copy a public repo and label it a new worker until its separate execution, origin, and handoff are witnessed.*

We preserve prior proposals, tests, and successful limited operations. The native owner of each domain retains verdict authority. This instrument is intentionally evidence-only: `--input` reads one snapshot, and nothing in this module runs continuously or calls GitHub or ChatGPT on its own.
