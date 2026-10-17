# W13 one-shot native job by repository-owner merge

**Referent:** Commit one explicitly authorized, source-pinned, finite W13 job request to protected `main` and let GitHub Actions execute it without the operator's desktop and without confusing CI tests with native checkpoint evidence.

The only authorized request is `native_job_requests/w13/game-w13-github-001.json`. The separate `workstation-w13-owner-merged-one-shot.yml` workflow fires only on a `main` push touching that exact path, and its job checks `github.actor == github.repository_owner`. The Python boundary independently demands the exact new file be **added** by a two-parent protected-main merge, exactly one W13 request in that folder, strict JSON equality, and preserved Git blobs for the W13 source subprocess and input fixture.

The public record states only the finite scope and explicit source-copy/admit/execute authorizations, **not** the conversational identity marker. Source copy still uses the existing workstation; admission still creates an immutable handoff; the original coordinator binds and executes only the exact named job. Fresh `controls reverify` and `cp_motion handoff --reverify` must establish `GAME-W13-WORLDS=WITNESSED` and `GAME-NATIVE-VERIFIER=ADMISSIBLE`.

The workflow archives the original execution journal, copied source edition, independent verifier output, exact authorization, hashes, and GitHub run identity for 30 days. This archive is *not* a durable always-on workstation, cannot stand in for fresh source verification on a later run, and is not proof that `GAME-NATIVE-VERIFIER` itself has been executed.

**Security and scope:** No `workflow_dispatch` impersonation, private-machine access, arbitrary Python source selection, wildcard job IDs, or unattended loop. This is a *single* protected-main committed owner authorization, scoped to the original W13 fixture and source bytes. It is distinct from the existing manual operator `workflow_dispatch` path, which remains unchanged.

The next movement, after an actual successful run and preserved artifact, is to build a separately authorized and independently verifying consumer for `GAME-NATIVE-VERIFIER` using this exact source-owned job, not a browser-only or historic PASS.
