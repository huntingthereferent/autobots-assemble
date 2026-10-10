# Session continuity verification — 2026-10-08

Referent: GitHub entry → standing AI session rules → active project referent.

Base inspected: `4479a7b9da18822be5cc925866c3b2fa6dc18fdb`.

## Movement and witnesses

- README already links ENTRY. ENTRY now explicitly loads ai.session once before
  the referent-specific sequence, without recursively repeating session entry.
- Registered core.traversal, which state/current.json already selects.
- Preserved the existing session continuity rules and current project pointer.
- Added four static contract checks in network/tests/test_session_continuity.py.
  Before the fixes: one passed, two failed, one errored (missing focused CI command).
  After the fixes: all four passed locally.
- Removing each of the speaker/surface distinction, correction-preservation
  clause, and application-routing boundary in memory caused the clause test
  to fail. No source files were changed by these mutation probes.
- CI now runs the focused checks separately before the existing broad suite.
  This record does not claim a successful new GitHub Actions run.

Command: `python -m unittest discover -s network/tests -p "test_session_continuity.py" -v`.

## Runtime boundary and remaining gaps

Inspected runtime/http/index.html, runtime/http/app.js, runtime/http_server.py,
and runtime/service.py. Front-page entry uses API routes and a browser-local
traversal session (continuityTraceSession, parent, referent and depth). That
browsing trace is distinct from the AI conversation and does not itself load or
enforce ai.session. The attention/activation UI passes actor=james; that is not
proof of the current conversational speaker or repository-write authorization.

The tests protect documented reachability and wording, not assistant obedience,
semantic equivalence of rewritten rules, authenticated identity, or application
routing. The repository cannot switch ChatGPT modes or ensure a host loads ENTRY.
A runtime/host witness is still needed to demonstrate actual speaker, goal,
authorization, correction, and next-movement preservation across a real handoff.

The base commit does have a push run:
https://github.com/huntingthereferent/language-network/actions/runs/37717544946 .
It ran 227 network tests and failed on missing curriculum_obligations and the
adult-math placement expectation. The language step was skipped. Those failures
are outside this session-contract change; the broad suite was not rerun locally.

Next movement: inspect the new focused CI step, then separately witness an actual
host/session handoff before claiming runtime continuity. Preserve the existing
frontage referent rather than replacing it with this verification record.

## Session language/precision amendment — 2026-10-10

**Referent:** The user corrected repeated assistant drift. Shared research
begins with communicable language at **every** reached layer, because humans
cannot transfer thoughts directly and mathematics itself is a human formal
language. This is a rule for communication and evidence precision, not a
declaration of a universal physical or cognitive law.

**Canonical changes:**
- `protocols/ai/session.md`: added language-first precision at every layer
  and a five-question self-check against unrequested reorientation.
- `ENTRY.md`: now routes entry through that standing discipline before any
  mathematical formalization or implementation.
- `network/tests/test_session_continuity.py`: added a static regression
  contract for the clauses and their reachability from ENTRY.

**Scope preserved:** No changes to the A/B mathematical definition in
`AB_CONTRACT.md`, no new engine or workflow, no change to the unrelated
frontage referent in `state/current.json`. The rules do not imply language
precedes thought, mathematics is separate from language, formalized results
are physical results, or that any final declaration must be made.

**Verification:** The GitHub workflow's focused session continuity check
passed at commit `ed2b0c4864c6cde897ff1e56697d79337ef57796`:
https://github.com/huntingthereferent/language-network/actions/runs/38094299234 .
This static check proves only that the source protocol clauses and entry
links exist; it does **not** demonstrate the assistant will obey them in a
future conversation. The larger protocol suite remained in progress when
this addendum was written; its earlier failures must not be silently promoted
to success.

**Next referent:** In an actual subsequent research move, check whether the
assistant can restate the current referent accurately, preserve native
mathematical scope, refrain from inserting a destination, and retain the
correction over a real session handoff. Record observed behavior separately
from these static source checks.
