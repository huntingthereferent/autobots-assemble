# A/B approach dialogue — presence-led branched-word maze

**Status:** private, opt-in local research experiment. This is **not** a
keylogger, a real cryptographic key route, a secure adversary sandbox, or
an operational deception system. No listener, worker or remote observer is
automatically activated.

## The corrected relationship

The A/B bipolar presence driver moves *independently* on its monotonic clock.
A participant's submitted message does **not** advance bipolar movement,
slow it down, reverse it, or trigger cryptographic key use. It only reads a
snapshot of that already-moving finite world and receives a fictional
**branch of words in its observed direction**.

The signposts mention approaching "keys" to construct a small theatrical
maze, but their directions are wholly invented. Every route terminates
at **another branch**, never at an actual private key, native runtime
object, secret, path, or authentication capability.

```text
trusted local native clock:
    A/B presence movement 0 → 1 → 2 → 3 ... independently of messages

consented participant submits words:
    read current presence orientation + count (no native mutation)
    └─ ordinary words → static fictional signpost
    └─ code-like words → syntax-shaped fictional code signpost
    └─ instruction-injection text → fictional prompt signpost
all signposts → "another branch"
never → actual key access, code execution, filesystem or worker API
```

The textual response changes with the **observed** presence count and
orientation. Sending multiple messages during the same observed presence
state returns the same branch style/text (for a given language). Waiting
for the separately moving presence changes the current branch. Session
submission counts exist for an operator's transcript only and do not
determine the direction, route, or motion of the world.

## "They injected code to check if it's real"

The local classifier recognizes a bounded set of **lexical hints** for
Python, JavaScript, SQL, shell, and instruction-style prompts. It selects
a prerecorded text template in a matching language style. It does
**not** parse the supplied code into an AST, call an interpreter,
run `eval`, invoke a shell, execute SQL, inspect environment variables,
or grant instruction-text any authority. Incoming text cannot instruct
the recorder to reveal source files, passwords, or host state.

For example, if somebody submits `python print(1)`, the fictional maze
may display:

```python
# fictional Python branch
route = 'toward_keys'
route = 'another_branch'
```

That is a **displayed signpost**, not a real Python execution result.
Likewise, SQL and shell-shaped branches consist only of static text.
The fictional route is explicitly disclosed at the start of the
experiment rather than being presented as a real production environment.

## Local demo

From the repository root:

```sh
python -m security.approach_dialogue
```

Read the notice and type exactly `AGREE` to start. Submitted lines
are the only input recorded; ordinary device typing elsewhere is never
monitored. Use `/show` to inspect submitted text and branches;
`/erase` clears transcripts and ends the session; `/quit` ends and
erases its own session. The native presence driver runs only during
the explicitly started demo.

There is no HTTP route or network transfer. Everything stays in the
local process's bounded memory, and no real key, private runtime
material, or cryptographic operation is passed into this component.

## Bounds and evidence

Inputs are limited to 280 printable characters; up to 64 stored
submissions and eight sessions. Pasted private-key headers are
refused; a small selection of common credential/email strings is
redacted before recording. **Redaction is best-effort and not a
guarantee that users cannot submit personal information.**

Regression tests check consent, erasure, bounds, idle-clock movement,
message noninterference, orientation-following word/code branches,
injection-shaped submissions as inert data, and absence of calls to
`eval`, `os.system`, and subprocess execution on these paths.

No test proves that anyone will be frightened, deterred, confused,
unable to inspect public metadata, or unable to compromise a host.
Fictional routes do not constitute cryptographic security. The
existing signed native ingress and operator key policy remain the only
real access-control and admission mechanisms in this lane.

## What has deliberately not been connected

No actual key file locations, filesystem paths, cryptographic
credentials, private-key bytes, decrypted records, real Python shell,
networked honeypot, silent surveillance, or worker execution interface
are reachable from the toy branch output. Testing a fictional
code-language prompt does not certify code-injection resilience
of every surrounding application; those are different trust boundaries.
