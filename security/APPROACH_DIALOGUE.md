# A/B approach dialogue — local opt-in research instrument

**This is not a keylogger.** It never attaches to the system keyboard,
listens to other applications, records background typing or intercepts
password entry. It only sees an entire text message voluntarily submitted
to its dedicated, disclosed research entrance.

## Why this exists

The existing `KeyApproachBoundary` observes bipolar probe movement
separately from native, authenticated, durably committed worker movement.
This experiment allows a willing participant to *say something to the
approach boundary* and see a tiny bounded sequence of maze-room labels.
Those messages form an operator-inspectable but **in-memory only**
transcript. They never become authorization to use a key.

The first toy rooms are `threshold → turn → mirror → passage`, repeated
over the finite probe trajectory. Rooms label observed approaches; they
are not navigation around authentication and have no connection to
Ed25519/X25519 private keys or real protected storage.

## Local experiment

Run from the repository root:

```sh
python -m security.approach_dialogue
```

The participant sees a plain-language notice. Typing exactly `AGREE`
opens an opt-in session. Only pressing Enter to submit an entire message
calls `ConsentApproachRecorder.submit`.

- `/show` displays this session's redacted submitted messages and the
  finite room associated with each.
- `/erase` clears all in-memory transcripts and ends the session.
- `/quit` ends the session and erases its transcript.
- If the terminal is closed or the process ends, its memory-only records
  disappear; no local file or network record is created by the instrument.

A trusted local host can inspect `operator_snapshot()` on an explicitly
instantiated recorder **in that process**, and can pass an existing
`KeyApproachBoundary` rather than creating a new one. There is no HTTP
route or native service hook that automatically starts this recorder.

## Bounded collection and safety

The instrument requires explicit notice acceptance, limits each submitted
message to 280 printable characters, limits storage to 64 entries and eight
sessions, rejects pasted private-key headers, and redacts several obvious
credential formats and email addresses. It stores neither physical
keystroke events nor addresses, keyboard-device identity, IP addresses,
user-agent strings, browser history, or timestamps.

**Redaction is best-effort, not a privacy guarantee.** Unrecognized secrets,
names and personal details may still be submitted. Do not use it for
real private communications or connect it to a public service without
a separate privacy, retention and consent review. The recorder is local
research instrumentation and should not handle private research.

The optional `NativePresenceRunner` runs independent monotonic-clock
bipolar presence for the CLI demo. It does not move encryption keys,
rotate credentials, execute worker tasks, or count toy messages as
authenticated handoff admissions.

## Observed claims and unknowns

Unit tests check consent, explicit submit semantics, bounded storage,
redaction, erasure, finite room order, no modification to the native
protected trajectory, and successful local CLI operation.

They **do not** show that an observer loses interest, cannot learn
public metadata, or can never reach a real cryptographic key. They
do **not** provide covert surveillance or threat-actor attribution.

The real workstation security boundary remains standard pinned
cryptography, native validation, protected storage, and explicit
operator authorization. This experiment is neither that boundary
nor a replacement for it.
