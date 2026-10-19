# Harness² swallowed into the existing A/B workstation

Source inspected: [Google Research Harness²](https://github.com/google-research/harness2/tree/1cfe254e8d25b15f37048c3730134686abe60335), revision `1cfe254e8d25b15f37048c3730134686abe60335` (2026-10-14). Paper: [Harness²: Recursive Agent Harnessing for an Open World](https://arxiv.org/abs/2610.14224).

**What is useful:** the controlled task-level *propose → probe → compare/compose* loop, and retaining observed outcomes for later tasks. The model's weights are not the harness. A/B already has source editions, recorded worker movements, provenance and exact native verifiers; there is no need to import Google's runner, scheduler, agent prompts or benchmarks.

## One shared workstation, many AI clients

Harness², ChatGPT and other agents may all call the **same** workstation. A client is not the workstation. No particular AI model or personality becomes its runtime.

`systems/workspace/harness_client.py` is an in-process Python adapter to **existing** `branch_help`, `controls.run_job`, `verify_return` and `RuntimeJournal`. It provides:

- `request_worker`: open a bounded request, optionally admit an already-registered, source-pinned worker. Unregistered work stays `OPEN_UNSTAFFED`.
- `execute_worker`: run only the exact admitted job with explicit execution approval. A completed job is reverified without spawning a duplicate subprocess.
- `reverify_return`: replay the native evidence without executing again.

The recorded client ID is attribution, **not proof of caller identity or authorization**. The native controls retain all execution and source gates. The adapter does not run Harness² or call any AI model itself.

Example, assuming the existing coordinator checkpoint, registered finite worker edition and input file have already been prepared:

```python
from systems.workspace.harness_client import WorkstationClient
from systems.workspace.branch_help import CAP_FINITE

client = WorkstationClient("runtime/data", client_id="harness2")
request = client.request_worker(
    lane="game", slot="cp-game-w13-worlds",
    capability=CAP_FINITE, opening_key="experiment-01",
    reason="Bounded preflight for a harness experiment",
    parent_version="base", inputs_file="native-inputs.json",
    admit_registered=True,
)
if request["child"]:
    job_id = request["child"]["job_id"]
    result = client.execute_worker(
        opening_id=request["opening_id"],
        expected_job_id=job_id,
        allow_native_execution=True,
    )
    print(result["return"])
```

This **example** uses an existing finite worker, not a generic game builder or a claim that a Harness² benchmark was executed.

## Compare only what was actually tested

`systems/workspace/contrastive_harness.py` compares the baseline and a changed child source edition on the *same task and inputs*. It requires two distinct native job receipts, current source fingerprints, fresh independently checked native results, and a separate comparison witness. It records the scoped outcome on the original workstation lane.

For a **single controlled harness experiment**, keep model identity, execution mode and fixed agent profile consistent between base and candidate. **Different agents are all welcome as separate workstation clients.** Switching a model, tooling mode or agent configuration *inside one pairwise test* creates a confound; do not attribute the difference solely to the changed harness component. No special prohibition is imposed on client names (including Codex); A/B itself has no dependency on Codex and does not switch to it to build.

`pin_supported_candidate` passes a supported comparison through the workstation's **existing** explicit native edition-promotion gate. That gate currently supports only registered editions it can independently reverify. A comparison never selects, merges or deploys a candidate by itself.

## Boundaries

This lane does **not** implement Google's agent editor, learned proposer, model-backed executor, recursive self-modification, parallel scheduler or benchmark scoring. It adds only the worker client path and the bounded witnessed comparison that our workstation can already support. Existing W13/world, ARC, NIH and A/B source lanes remain untouched.

Upstream Harness² is Apache-2.0; third-party components have their own terms. No upstream code or third-party dependencies are copied. Original A/B code remains under the repository's current All Rights Reserved notice. The upstream paper's performance figures are not claims of tested A/B improvements.

## Reproduction

```bash
python -m unittest -v network.tests.test_harness_client network.tests.test_contrastive_harness
```

The harness-client tests use **actual registered native finite-worker execution and re-verification** against isolated temporary data. Contrast tests use declared synthetic comparator fixtures, proving the gate's behavior but **not** real AI/harness improvement. A model-backed paired trial and cross-task generalization remain unverified.
