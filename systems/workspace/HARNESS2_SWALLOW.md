# Swallow Harness²: bounded contrastive probe lane

**Referent:** [google-research/harness2](https://github.com/google-research/harness2), public upstream at inspection on 2026-10-19. The upstream paper is [Harness²: Recursive Agent Harnessing for an Open World](https://arxiv.org/abs/2610.14224). This lane responds to that *actual* research object, not to a similarly named generic agent framework.

## What was inspected

Harness² refines a task's execution harness through Propose–Probe–Compose, then carries evidence-supported lessons into a separate improvement harness for subsequent tasks. It exposes eight configurable parts: system prompt, guardrails, memory, tool guidance, subagents, skills, scripts, and plugins. Its experiments include parallel and sequential refinement, candidate rollouts, composition, a run ledger, and a persistent per-domain library. It supports OpenCode and Codex with JobBench, LAB, and WorkBuddy-Bench.

Upstream is **Apache-2.0** and retains third-party license notices. Its authors report improvements on their published benchmark configurations; those are their findings, **not** independently reproduced A/B results. Their documentation also warns that executor network access is unrestricted and Codex runs without sandboxing; public benchmark grading material can be fetched accidentally. Do not inherit those operational defaults.

## What A/B already has

- `ProcessWorkstation`: unchanged source ownership, inspectable editions and branches with SHA-256 fingerprints.
- `WorkstationContinuationHarness`: native journal, explicit lane creation, witnessed branch/connection observations.
- `controls.promote_edition`: selection only after a COMPLETE native job on the exact edition, independently reverified.
- `PreferredEditions`: append-only local preferences, not automatic deployment or blanket scientific success.

These are the native capabilities; importing Google's separate runner, prompts, grading tools, or benchmark datasets would create a competing execution and evidence spine.

## First executable movement

`systems/workspace/contrastive_harness.py` adds a small, independent **pairwise probe intake**:

1. Choose a source-owned base and its changed child branch; declare which of the eight harness components was edited.
2. Produce TWO native job receipts externally on the **same task and exact input digest**. Record each job, edition fingerprint, result digest and witness locator. Intake never performs execution.
3. Independently reverify both receipts with an installed domain-native callback **on each invocation**. There is no permissive verifier.
4. Only then ask a **separate** domain-native comparator for an outcome and contrast witness. A changed result, a self-reported score or a shared witness is not evidence of improvement.
5. Append the bounded verdict as `WORKSTATION_HARNESS_CONTRAST` to the **existing** `RuntimeJournal` under the chosen coordination lane. Replaying the same record is idempotent; a changed source blocks the old receipt.
6. `pin_supported_candidate` requires explicit operator approval, **fresh verification**, and delegates to existing `controls.promote_edition` for a second source-owned native recheck. A supported comparison is **not** itself a promotion.

**State vocabulary:** `SUPPORTED` = an independently supplied improvement verdict on *one matching task*. `NO_PREFERENCE` = comparator did not support preference. `UNKNOWN` = native evidence missing. These words do not assert generalization, truth of an external benchmark, autonomous operation, or successful deployment.

This does **not** yet implement an AI proposer, automatic agent editing, recursive composition, task scheduling, full persistent cross-task optimization, remote network restrictions, or general native comparison workers. Those remain separate witness-requiring continuations. It deliberately leaves W13/game world, NIH, ARC and existing research lanes untouched.

## Rights and provenance

No Harness² source files, prompt strings, benchmark data, or dependencies are copied into this lane. The code is a new A/B implementation based on the described contrastive research relationship. The root A/B **All Rights Reserved** notice remains unchanged and does **not** purport to revoke or replace upstream Apache-2.0 rights. If actual upstream code is later incorporated, preserve the exact Apache license and any applicable NOTICE/third-party terms.

## Reproduce contract tests

```bash
python -m unittest -v network.tests.test_contrastive_harness
```

All witness callbacks in the included tests are explicit **fixtures**. They validate the behavior of the admission gate and journal, not that any real model or native domain experiment improved. An operational demonstration requires real executed base/candidate receipts and an independent native comparator bound to that domain.
