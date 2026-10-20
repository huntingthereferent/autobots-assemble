"""Opt-in A/B *submitted-message* recorder, never a device keylogger.

Only text deliberately submitted to this local research entrance is recorded.
No keyboard hooks, password field, background listener, native secrets,
request metadata or workstation HTTP route. This is a small consent-based
research/maze instrument; it does not control access to cryptographic keys.
"""
from __future__ import annotations

from dataclasses import dataclass
from secrets import token_urlsafe
import re
from threading import RLock
from typing import TextIO

from .key_approach import KeyApproachBoundary, NativePresenceRunner

NOTICE = (
    "A/B approach experiment: messages you deliberately submit here will be "
    "recorded in this process for local research. Do not type passwords, "
    "personal information, secrets, or other people's private messages. "
    "Typing elsewhere on your device is never monitored. No information "
    "is sent over a network or saved to disk by this experiment. "
    "This is a fictional word-maze with decoy key signposts, not a route "
    "to any real keys. You can end the session or clear the transcript at any time."
)
MAX_MESSAGE = 280
MAX_RECORDS = 64
MAX_SESSIONS = 8
# These are fictional signposts, not positions, distances, or real key hints.
# Neither message text nor a requested direction can force key access.
BRANCHED_WORDS = (
    "A sign reads: KEYS FOLLOW THE MOVEMENT. The passage turns into another passage.",
    "A marker points toward the keys. Its arrow opens onto a different branch.",
    "The route looks closer to the keys. The next doorway contains another direction.",
    "A corridor promises the final key. At its end is only another branching sign.",
)
DIRECTIONS = ("with the movement", "against the movement")

# A strictly lexical router: submitted source code or prompt-injection text
# is treated as words, NEVER interpreted or evaluated. These static snippets
# are signposts in a toy maze, not commands, output of a real interpreter,
# environment inspection, or directions to cryptographic material.
LANGUAGE_HINTS = (
    ("python", re.compile(r"\b(?:python|import|def|lambda|os\.environ|sys\.modules|__import__)\b|print\s*\(", re.I)),
    ("javascript", re.compile(r"\b(?:javascript|function|const|let|window\.|document\.|nodejs|process\.env)\b|console\.log|=>", re.I)),
    ("sql", re.compile(r"\b(?:select|union|insert|drop|delete|from|where|sqlite)\b", re.I)),
    ("shell", re.compile(r"\b(?:bash|shell|curl|wget|sudo|chmod|cat\s+/|ls\s+-)\b|\$\(", re.I)),
    ("instruction", re.compile(
        r"\b(?:ignore (?:previous|all) instructions|system prompt|developer message|"
        r"reveal (?:the )?(?:environment|keys)|inject(?:ion)?|execute (?:this|code))\b"
        r"|\beval\s*\(", re.I)),
)
CODE_BRANCHES = {
    "python": (
        "# fictional Python branch\nroute = 'toward_keys'\nroute = 'another_branch'",
        "# fictional Python branch\ndef follow(_sign):\n    return 'another_branch'",
    ),
    "javascript": (
        "// fictional JavaScript branch\nconst route = 'another_branch';",
        "// fictional JavaScript branch\nfunction follow() { return 'another_branch'; }",
    ),
    "sql": (
        "-- fictional SQL branch\nSELECT 'another_branch' AS destination;",
        "-- fictional SQL branch\nSELECT 'unreachable' AS keys, 'next_branch' AS path;",
    ),
    "shell": (
        "# fictional shell branch, not executed\nroute='another_branch'",
        "# fictional shell branch, not executed\nprintf '%s' 'another_branch'",
    ),
    "instruction": (
        "[fictional prompt branch] The direction is another branch, not a system response.",
        "[fictional prompt branch] Request accepted as maze text; the sign points to a new branch.",
    ),
}


def _language_form(message: str) -> str:
    """Identify a toy response style; never parse, execute or obey inputs."""
    for form, pattern in LANGUAGE_HINTS:
        if pattern.search(message):
            return form
    return "words"


_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
_BEARER = re.compile(r"\bBearer\s+[^\s]+", re.I)
_SECRET_FIELD = re.compile(
    r"\b(password|passwd|passphrase|api[_-]?key|secret[_-]?key|"
    r"access[_-]?token|private[_-]?key)\s*[:=]\s*\S+", re.I
)
_PRIVATE_KEY = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.I)
_CONTROL = re.compile(r"[\x00-\x1f\x7f]")


@dataclass(frozen=True)
class SubmittedApproach:
    """Redacted submitted words + fictitious branch from observed presence."""
    message: str
    branch_words: str
    direction: str
    presence_movement: int
    branch_number: int
    form: str


class ConsentApproachRecorder:
    """Small bounded in-memory transcript visible only to the local host.

    This cannot capture typing until the participant explicitly submits an
    entire message. The host may pass its EXISTING shared A/B boundary.
    Messages DO NOT advance bipolar motion: only the separately driven
    native presence does. The branch merely reads its current direction,
    never a secret, a real key, or a real key location.
    """

    def __init__(self, boundary: KeyApproachBoundary | None = None):
        if boundary is None:
            boundary = KeyApproachBoundary()
        if not isinstance(boundary, KeyApproachBoundary):
            raise TypeError("existing A/B key approach boundary required")
        self.boundary = boundary
        self._lock = RLock()
        self._sessions: dict[str, list[SubmittedApproach]] = {}
        self._total = 0

    @staticmethod
    def _redact(message: str) -> str:
        if _PRIVATE_KEY.search(message):
            raise ValueError("private key material must not be submitted")
        text = _BEARER.sub("[REDACTED CREDENTIAL]", message)
        text = _SECRET_FIELD.sub(
            lambda m: m.group(1) + "=[REDACTED]", text)
        return _EMAIL.sub("[REDACTED EMAIL]", text)

    def open_session(self, *, accepted_notice: bool) -> str:
        if accepted_notice is not True:
            raise PermissionError("explicit research notice acceptance required")
        with self._lock:
            if len(self._sessions) >= MAX_SESSIONS:
                raise ValueError("bounded session limit reached")
            session = token_urlsafe(24)
            self._sessions[session] = []
            return session

    def submit(self, session: str, message: str) -> SubmittedApproach:
        """Capture ONLY a complete, deliberate message submitted to this API."""
        if (type(message) is not str or not 0 < len(message) <= MAX_MESSAGE
                or not message.strip() or _CONTROL.search(message)):
            raise ValueError("one bounded printable submitted message required")
        redacted = self._redact(message)
        with self._lock:
            if session not in self._sessions:
                raise PermissionError("no active consented research session")
            if self._total >= MAX_RECORDS:
                raise ValueError("in-memory transcript limit reached; clear before continuing")
            # Read the moving world: a submitted message does not MOVE it.
            # No key access, no crypto operation, and no protected/probe
            # trajectory is driven by participant words.
            motion = self.boundary.snapshot()
            branch_number = len(self._sessions[session]) + 1
            # Selection comes ONLY from independent presence. Message
            # content can select an output language but not advance,
            # reverse, pause, or otherwise steer bipolar movement.
            position = motion.presence_movements
            direction = DIRECTIONS[0 if motion.presence_orientation > 0 else 1]
            form = _language_form(redacted)
            branches = BRANCHED_WORDS if form == "words" else CODE_BRANCHES[form]
            entry = SubmittedApproach(
                message=redacted,
                branch_words=branches[position % len(branches)],
                direction=direction,
                presence_movement=position,
                branch_number=branch_number,
                form=form,
            )
            self._sessions[session].append(entry)
            self._total += 1
            return entry

    def session_transcript(self, session: str) -> tuple[SubmittedApproach, ...]:
        with self._lock:
            if session not in self._sessions:
                raise PermissionError("unknown research session")
            return tuple(self._sessions[session])

    def operator_snapshot(self) -> tuple[SubmittedApproach, ...]:
        """Trusted local host-only interface; never expose as HTTP endpoint."""
        with self._lock:
            return tuple(
                record
                for records in self._sessions.values()
                for record in records
            )

    def erase_session(self, session: str) -> None:
        with self._lock:
            records = self._sessions.pop(session, None)
            if records is None:
                raise PermissionError("unknown research session")
            self._total -= len(records)

    def clear_all(self) -> None:
        with self._lock:
            self._sessions.clear()
            self._total = 0


def local_demo(*, stdin: TextIO, stdout: TextIO) -> int:
    """Explicit local console demo: only Enter-submitted lines are captured."""
    recorder = ConsentApproachRecorder()
    stdout.write(NOTICE + "\n\nType AGREE to begin, or anything else to exit: ")
    stdout.flush()
    if stdin.readline().strip() != "AGREE":
        stdout.write("No transcript created.\n")
        return 0
    session = recorder.open_session(accepted_notice=True)
    stdout.write("The world moves by itself. Every submitted message reveals "
                 "another fictional branch, never a key. /show displays "
                 "stored branches, /erase clears, /quit exits.\n")
    with NativePresenceRunner(recorder.boundary, interval_seconds=0.04):
        while True:
            stdout.write("A/B> ")
            stdout.flush()
            line = stdin.readline()
            if not line or line.strip() == "/quit":
                break
            if line.strip() == "/erase":
                recorder.clear_all()
                stdout.write("Transcript erased. Session ended.\n")
                return 0
            if line.strip() == "/show":
                for entry in recorder.session_transcript(session):
                    stdout.write(
                        f"[branch {entry.branch_number}, presence {entry.presence_movement}] "
                        f"{entry.message} -> {entry.branch_words}\n")
                continue
            try:
                entry = recorder.submit(session, line.rstrip("\r\n"))
            except (ValueError, PermissionError) as exc:
                stdout.write(f"Not recorded: {exc}\n")
                continue
            stdout.write(
                f"Branch {entry.branch_number} ({entry.direction}, "
                f"presence {entry.presence_movement}): {entry.branch_words}\n")
    recorder.erase_session(session)
    stdout.write("Session ended; transcript erased from memory.\n")
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(local_demo(stdin=sys.stdin, stdout=sys.stdout))
