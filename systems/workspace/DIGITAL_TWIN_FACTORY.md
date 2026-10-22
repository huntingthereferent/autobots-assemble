# Digital Twin Factory — workstation replication and capacity expansion

**Purpose:** one controller, multiple independently executing, source-pinned workstation twins. A twin is a Git repository and execution environment with the same core code/history as the controller at birth, not a newly invented research lane and not a replacement for any existing Desi repository.

## Ownership / first destination

- Controller: `huntingthereferent/autobots-assemble` (James GitHub connection).
- First permitted destination: `aeren-research/autobots-assemble-twin-01` (Desi GitHub connection).
- Do **not** overwrite `aeren-research/continuum-oscillator`, `meta-scanner`, `continuum-handoff-language`, or `continuity-fixer`; these are distinct research artifacts.
- A fresh destination repository must be owned by the account whose credentials provision it; existing connector read/write access does not authorize use of an unspecified personal access token.

## Factory loop

```text
observe ALL owner repositories and workflow states
  -> running + queued, account-level
  -> sustained saturation (3 observations spanning at least 120 seconds)
  -> qualify explicit next destination; never spawn on one noisy reading
  -> pin exact controller main SHA
  -> create NEW empty destination under provisioned owner's account
  -> disable all Actions on destination BEFORE pushing
  -> bare-clone controller branches/tags and reachable Git history
  -> push to destination; verify target main SHA equals pin
  -> record birth receipt (source, target, SHA, actions-disabled)
  -> audit workflow triggers; admit a limited explicit lane allowlist
  -> independent results returned with source SHA, twin ID, run URL and job ID
  -> if capacity again saturates AND previous twin is functioning, consider next twin
```

A twin is NOT the next slot in a loop of automatic account creation. Only existing authorized owners and explicitly allowed destination repositories may be considered. Do not grow just because the viewer shows 20/9000; it samples workflow history, not account-wide concurrency. Queued jobs can result from dependencies, limits, workflow-level concurrency groups, or pending checks rather than a need for another account.

## Implemented in this branch

`systems/workspace/digital_twin_factory.py`:
- `observe`: authenticated REST account-owner enumeration and totals for `in_progress` and `queued` in ALL repositories owned by that account, not the latest hundred runs of one repo. Reads `FACTORY_SOURCE_TOKEN` from environment; verifies the authenticated GitHub user.
- `decide`: read-only, three-sample admission requiring time separation, consistent owner and cap, saturated running jobs, and a nonempty queue.
- `birth`: exact-target-confirmed new repo provisioning via `gh` logged in as target owner; checks the pinned main SHA, disables target Actions, pushes all branches and tags with reachable history, re-reads destination main SHA. It refuses an existing target.
- `systems/workspace/digital_twin_controller.py`: connected one-shot cycle: observe, append a persistent sample, qualify, obtain source pin, birth exactly one authorized twin, write a local registry receipt, and refuse further births until aggregate multi-account capacity/readiness is implemented.\n- `network/tests/test_digital_twin_factory.py`: no-network tests of saturation, stale evidence, controller idempotence and fail-closed behavior.

```sh
# From the repo root; token belongs to the observed SOURCE GitHub user.
export FACTORY_SOURCE_TOKEN=...  # use a secure secret manager; never check tokens into git
python -m systems.workspace.digital_twin_factory observe --owner huntingthereferent >> capacity-samples.jsonl
# Repeat at intervals of >=60 seconds; snapshots must span >=120 seconds.
python -m systems.workspace.digital_twin_factory decide --snapshots capacity-samples.jsonl

# On trusted computer, gh MUST be logged into the DESTINATION account;
# target must not exist. Pin the current authoritative source main commit.
python -m systems.workspace.digital_twin_factory birth \
  --source huntingthereferent/autobots-assemble \
  --target aeren-research/autobots-assemble-twin-01 \
  --source-sha <40-hex-source-main-SHA> \
  --confirm aeren-research/autobots-assemble-twin-01
```

Provisioning does not move secrets, GitHub Actions run history, issue metadata, branch protection, or repository/Pages settings. `git clone --bare` copies all accessible branches, tags and the history reachable from them. Disabling Actions prevents accidental storm-triggering; enabling selected workflows is a separate audited operation.

## Run one connected cycle\n\nOn an authorized persistent host (not the read-only viewer), invoke this at intervals of at least one minute. `gh` must authenticate as `aeren-research`; the source read credential belongs to `huntingthereferent`. The first two calls only observe; a third saturated sample spanning at least two minutes may produce one twin. The registry prevents repeating that birth.\n\n```sh\npython -m systems.workspace.digital_twin_controller \\\n  --history runtime/data/factory-capacity.jsonl \\\n  --registry runtime/data/factory-twins.json \\\n  --confirm aeren-research/autobots-assemble-twin-01\n```\n\nNo scheduler has been connected and no new Desi destination exists yet. The provisioned twin deliberately starts with all Actions disabled.\n\n## Activation and limits still to build

- A scheduled invocation on an authorized persistent host, and a process lock for multiple competing controllers. The connected one-shot cycle and local persistence are implemented; the host/scheduler is not.
- Parent-child registry with independently verified twin readiness, assigned lanes, and work receipts. Each twin reports its own native results; the controller must verify returned refs rather than adopt claims.
- A minimal safe workflow allowlist for an initial worker lane; never enable hundreds of copied workflows by default.
- Account billing/usage clearance; private repositories may consume included minutes and require quota checks. Public standard GitHub-hosted actions minutes are free but still subject to concurrency limits.
- Repository creation uses `gh`, because the currently connected GitHub tool surface does **not** expose a create-repository action. Authentication and provisioning must be executed with authorized target-account credentials.

These items are explicitly **not yet live**. This branch contains a source-pinned provisioning mechanism and a connected single-twin cycle, not an activated autonomous twin network.
