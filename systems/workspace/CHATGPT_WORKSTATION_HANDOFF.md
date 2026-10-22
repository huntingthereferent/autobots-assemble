# ChatGPT ↔ Workstation handoff protocol

## Purpose

Resume a lane from its current evidence instead of reconstructing state from chat history. This is a read-only handoff protocol; it does not create jobs, execute workers, or make public research records authoritative over the private runtime.

## Three distinct state sources

1. **Public research source index:** `views/traces/research-live.json` and `systems/workspace/research_observatory.py`. Useful for locating source records and their recorded next movements. It may be stale and is not a runtime journal.
2. **GitHub execution evidence:** pull-request heads, checks, workflow logs, and artifacts. These prove only what those particular workflow runs report.
3. **Private live workstation:** the authorized machine's `runtime/data/` journals and current source editions. This is the authority for live coordinator/job state and must not be inferred from (1) or (2).

## Resume procedure

For each new ChatGPT window or return after a detour:

1. Read this protocol and `systems/workspace/README.md`.
2. Read the relevant source lane's native record and its cited evidence. For ARC, start from the active dive/experiment and inspect open ARC PRs and their latest workflow runs/artifacts.
3. Keep the distinctions explicit: proposed vs admitted; READY vs executed; COMPLETE vs natively reverified; observation vs interpretation; historical vs current.
4. Before choosing the next experiment, inspect the private workstation handoff below if the owner has supplied a fresh snapshot. If no fresh snapshot is available, say that live coordinator state is **unobserved** and proceed only from the identified GitHub lane.
5. End each work session with a compact return point: referent, exact changed files/PR/commit, workflow run and artifact IDs, result, what survived, unresolved wall, and one next movement. Do not claim the private workstation changed unless its native journal confirms it.

## Obtain a fresh private status snapshot

Run from the repository root on the authorized workstation. These commands are read-only status/reverification operations; they do not execute a READY job.

```powershell
python -m systems.workspace.cp_motion --data-dir runtime/data handoff --markdown --reverify
```

If the task is not represented in the CP coordinator, inspect the existing read-only workstation view instead:

```powershell
python -m systems.workspace.view_server --data-dir runtime/data --port 8051
```

Then open `http://127.0.0.1:8051/workstation.html` on that same machine. Do not expose the private viewer publicly.

Share only the relevant status section or a deliberately redacted export in the ChatGPT window. Do **not** upload the complete `runtime/data` directory, credentials, private source archives, or unrelated personal records to a public repository.

## Handoff template

```text
LANE:
REFERENT:
LIVE RUNTIME SNAPSHOT: observed / not observed (timestamp + source)
CURRENT NATIVE STATE:
LATEST SOURCE CHANGE: PR / commit / file
LATEST RUN: workflow ID + conclusion
ARTIFACT: name + digest or link
RESULT:
PRESERVED:
WALL / UNKNOWN:
NEXT MOVEMENT:
```

## Safety and evidence rules

- A successful GitHub Actions run is not proof that the private local coordinator advanced.
- A committed projection is not a live status check.
- A result's own PASS-like text is not a witness; use the native verifier and its declared evidence.
- Reverification is not execution. Never run a READY job merely because a continuation note names it.
- If current runtime evidence conflicts with the public projection, preserve both records, mark the discrepancy, and resolve it through the owning native source rather than overwriting history.
