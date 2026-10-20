"""Opt-in A/B *submitted-message* recorder, never a device keylogger.

Only text deliberately submitted to this local research entrance is recorded.
No keyboard hooks, password field, background listener, native secrets,
request metadata or workstation HTTP route. This is a small consent-based
research/maze instrument; it does not control access to cryptographic keys.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
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
    "You can end the session or clear the transcript at any time."
)
MAX_MESSAGE = 280
MAX_RECORDS = 64
MAX_SESSIONS = 8
ROOMS = ("threshold", "turn", "mirror", "passage")
_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
_BEARER = re.compile(r"\bBearer\s+[^\s]+", re.I)
_SECRET_FIELD = re.compile(
    r"\b(password|passwd|passphrase|api[_-]?key|secret[_-]?key|"
    r"access[_-]?token|private[_-]?key)\s*[:=]\s*\S+", re.I
)
_PRIVATE_KEY = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.I)
_CONTROL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")


@dataclass(frozen=True)
class SubmittedApproach:
    """Redacted submitted message and model-only room; no device metadata."""
    message: str
    room: str
    step: int


class ConsentApproachRecorder:
    """Small bounded in-memory transcript visible only to the local host.

    This cannot capture typing until the participant explicitly submits an
    entire message. The host may pass its EXISTING shared A/B boundary;
    this class does not construct, read, or mutate cryptographic keys.
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
            # A participant's submitted approach moves the probe trajectory,
            # never protected keys or native authenticated admission.
            observed = self.boundary.approach()
            entry = SubmittedApproach(
                message=redacted,
                room=ROOMS[(observed.step - 1) % len(ROOMS)],
                step=observed.step,
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
    stdout.write("Type messages; /show displays stored messages, /erase clears, "
                 "/quit exits and erases.\n")
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
                    stdout.write(f"[{entry.step} {entry.room}] {entry.message}\n")
                continue
            try:
                entry = recorder.submit(session, line.rstrip("\r\n"))
            except (ValueError, PermissionError) as exc:
                stdout.write(f"Not recorded: {exc}\n")
                continue
            stdout.write(f"Observed approach {entry.step} — room: {entry.room}\n")
    recorder.erase_session(session)
    stdout.write("Session ended; transcript erased from memory.\n")
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(local_demo(stdin=sys.stdin, stdout=sys.stdout))
