# A/B finite branch browser — consented localhost laboratory

This is a **browser interface to the existing Python fictional maze**,
not a standalone JavaScript simulation. The Python process owns the
actual `KeyApproachBoundary`, the monotonic-clock
`NativePresenceRunner`, the closed `branch_world` graph and any
voluntarily submitted in-memory transcript. The page receives only
bounded JSON views of that world.

## Start the local experiment

From the repository root:

```sh
python -m security.branch_browser
```

The console prints an ephemeral URL such as
`http://127.0.0.1:PORT`. Open that URL on the *same computer* and
accept the participant notice to begin. There are two visible fictional
exits at every story location:

- **Follow movement:** submit your text and follow the current `along`
  fictional edge, based on the native presence orientation.
- **Take side branch:** submit text but choose the other current fictional
  edge. This advances only the participant's story cursor, never the
  native A/B world or keys.

The observed presence counter and bipolar swing update without any
submitted messages. Text resembling Python, SQL, shell, JavaScript or
instruction injections only chooses static, **displayed** branch words;
nothing is executed or sent to a runtime shell.

**Erase and exit** deletes the consented session's in-memory transcript
and invalidates its token. Stopping the server clears all transcripts.
Closing a browser tab alone does *not* guarantee deletion while the
local process remains alive. No cookies, client-side storage, HTTP
analytics, third-party scripts or external assets are used.

## Trust boundary

`security.branch_browser.BranchBrowserServer` binds **only to
127.0.0.1** and must be started explicitly by a local host. It is
**not** a production service; local loopback access does *not*
authenticate an operating-system user.

The only routes are:

```text
GET  /                 fixed local HTML
GET  /maze.js          fixed local JavaScript
POST /api/consent      requires explicit accepted=true, creates memory session
GET  /api/state        authorized story cursor and real native presence
GET  /api/transcript   only the consented session's bounded records
POST /api/submit       submitted message + fictional along/side choice
POST /api/erase        erases that memory session
```

Incoming writes require an exact same-origin `Origin`,
a loopback peer and strict `Host`, bounded JSON body and a session
token for participant actions. Duplicate JSON fields, nonfinite data,
invalid choices, unknown routes and remote/cross-site origins are
refused. Responses include no-cache, content-type protection, no
framing, and restrictive CSP headers. Submitted text is put into
JavaScript `textContent` nodes, **never** HTML or a code interpreter.

**Known limits:** this is plain HTTP on the local loopback network
namespace, not independently authenticated HTTPS. Other processes
running on the same computer may contact it, and browser extensions or
local malware may see the page. The code is not a general-purpose
sandbox and must never be provided native keys, source files, worker
execution methods or real secret paths. Simple regex redaction is not
a complete privacy mechanism, and users must not submit sensitive
data. The presence thread stops if this program stops; no unattended
background persistence is claimed.

No public endpoint, hosted website or real external adversarial
testing is included. These changes remain isolated to draft PR #262.

## Tests

`network/tests/test_security_branch_browser.py` makes real localhost
HTTP requests against the Python handler and checks consent,
unauthorized/cross-origin refusal, present-time ticks with no incoming
submissions, message/code-shaped responses, safe browser rendering
primitives, story cursor movement, transcript erasure, bounded JSON and
the absence of native admission.

This is server/HTTP integration evidence, **not** an independently
witnessed full browser/Chromium replay or a proof of complete security.

```sh
python -W error::ResourceWarning -m unittest discover \
  -s network/tests -p 'test_security_branch_browser.py' -v
```
