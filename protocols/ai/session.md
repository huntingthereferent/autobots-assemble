# AI Protocol — Session

## Enter

1. Read \`ENTRY.md\`.
2. Read \`state/current.json\`.
3. Load the protocol named by \`state/current.json\`.
4. Load the active record reached from the referent.

## Session surface and speaker continuity

Standing preference recorded from James on 2026-10-07:

- James's project/research work stays GitHub-centered. Work Mode is reserved by preference for Dessy's songwriting and writing. A current explicit request may override this preference.
- The application surface is not evidence of who is speaking. Preserve established speaker context and authorization; follow `ai.james` where identity is unresolved.
- At session entry, compare the requested workflow with the actual surface when that information is available. If James's GitHub work is in Work Mode, state the mismatch once, plainly and early. Do not wait for him to notice a change in behavior.
- Do not silently redirect work to another mode, workspace, or project. If a real workflow transfer is necessary, explain the concrete reason before proposing it. Do not repeatedly ask to transfer files when useful authorized work remains possible through the connected repository.
- Distinguish the chat surface from the GitHub connector. Having GitHub tools does not mean the chat itself has changed modes. Never claim to switch the application mode without a capability and a confirmed result. This protocol cannot enforce application routing.
- Preserve James's communication pattern across surfaces: current referent → relations present → what changed or survived → next supported movement. Use grounded, confident, considerate, precise language; avoid repetitive permission loops and canned project-management phrasing.
- A different code location does not establish a different project. Trace existing project relations before proposing a duplicate system or treating missing local files as a project-wide blocker. State access limits accurately without pretending unavailable code was inspected.
- When corrected with “one layer up,” revisit the parent referent before continuing the implementation detail. Preserve the user's correction in the next movement.

If a context mismatch is found, preserve the goal, repository, established authorization, findings and next movement. Continue useful authorized work in the current session unless the user asks to stop or move. If a handoff is requested, carry those facts forward without treating it as a fresh project.

## Operate

For each substantive step:

- name the referent internally;
- identify evidence actually used;
- check the witnesses;
- move once or emit a wall/unknown state;
- keep older layers as evidence only;
- write durable changes back to the appropriate layer.

## Exit

Before ending substantial work, leave a recoverable next movement. If repository state changed, update the canonical record or state pointer rather than relying on chat memory alone.

## Verification boundary

`network/tests/test_session_continuity.py` checks the documented entry route,
active protocol resolution, and preservation of the continuity clauses below
that entry. CI runs it separately before the broader suite. This is a static
repository contract check, not evidence of assistant compliance, speaker
authentication, or application-mode control. The front-page traversal session
is a browsing trace, not the AI conversation session.

See [verification record](../../state/session-continuity-verification.md) for
observed gaps and the next movement.
