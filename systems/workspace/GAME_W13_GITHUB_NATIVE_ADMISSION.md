# GAME W13 — GitHub-hosted native admission

**Boundary:** GitHub PR/push checks test the implementation. They do **not** admit a source-owned user job or witness the live checkpoint. This separate workflow can run one explicitly authorized finite `GAME-W13-WORLDS` job on a GitHub-hosted Ubuntu runner, without Dessy's computer.

## Exact operator-dispatched flow

The workflow `.github/workflows/workstation-w13-github-native-admission.yml` is `workflow_dispatch` only. It refuses non-main refs, other dispatch actors, `execute=false`, missing/invalid job IDs, and unequal exact job confirmations. It installs no new native engine. It uses:

1. `cp_motion admit-research` to register the existing checkpoint graph.
2. `game_w13_native_cli copy / prepare / admit` to pin exactly the preserved W13 fixture and worker source edition, with explicit confirmations.
3. `coordinator_window bind-job / run-linked` for exactly one admitted, bound W13 game job.
4. `controls reverify` and `cp_motion handoff --reverify` to independently check original W12 replay and native journal evidence in new Python processes.
5. `actions/upload-artifact` to retain the actual native runtime journal, source edition, execution output, re-verification, verdict and hashes for 30 days.

To dispatch: **Actions → workstation-w13-github-native-admission → Run workflow → main**. Supply a unique safe `job_id`, repeat it exactly as `confirm_job_id`, and enable `execute`. The dispatcher must be the GitHub repository owner. This opt-in authorizes execution of copied Python code on an ephemeral GitHub runner; it is not an OS sandbox for arbitrary worker submissions.

**Required result:** `GAME-W13-WORLDS = WITNESSED` and the separate `GAME-NATIVE-VERIFIER = ADMISSIBLE`. Both must derive from the *actual* source-matched native job and fresh verifier, never the workflow's success badge alone.

## State, replay and remaining wall

The runner is destroyed after each run. Its journal is an **artifact**, not a continuously running server or automatically restored workstation. Archive retention is 30 days, and job-ID uniqueness is not guaranteed across separate workflow runs.

A later native verifier must recover the original archive, pin GitHub's exact run ID/attempt, artifact ID and digest, checkout/source hashes, worker handoff, and journal history, and fresh-reverify before accepting the source-owned parent. Mere artifact existence cannot promote a checkpoint. This movement does **not** create unattended scheduling, execute `GAME-NATIVE-VERIFIER`, or grant automatic next-job authorization.
