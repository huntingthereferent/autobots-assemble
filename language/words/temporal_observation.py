"""Time-aware, append-only observations for the existing Words Movement layer.

Only explicitly witnessed conversation events and first-person reports are stored.
Elapsed time is a calculation, not evidence of a reply, a feeling, or intent.
There is no background clock, watcher, mood inference or chat integration.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

Kind = Literal["REPLY", "NO_REPLY_OBSERVED", "FELT_REPORT"]
ReportMode = Literal["contemporaneous", "recollection"]


def _aware(value: datetime, field: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field} must be a timezone-aware datetime")
    return value


def _nonempty(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must not be empty")
    return value


@dataclass(frozen=True)
class Moment:
    kind: Kind
    at: datetime
    recorded_at: datetime
    source: str
    words: str | None = None
    since: datetime | None = None
    evidence_ref: str | None = None
    report_mode: ReportMode | None = None


class ConversationTrace:
    """One referent, with explicit time observations and unchanged first-person words.

    A SILENCE/NO_REPLY_OBSERVED entry covers only the declared, checked interval.
    No absence is inferred merely because more wall-clock time has passed.
    """

    def __init__(self, referent: str, started_at: datetime, *, expected_return: bool = False):
        self.referent = _nonempty(referent, "referent")
        self.started_at = _aware(started_at, "started_at")
        if not isinstance(expected_return, bool):
            raise ValueError("expected_return must be a boolean")
        self.expected_return = expected_return
        self._journal: list[Moment] = []

    @property
    def journal(self) -> tuple[Moment, ...]:
        return tuple(self._journal)

    def _record(self, moment: Moment) -> Moment:
        _aware(moment.at, "at")
        _aware(moment.recorded_at, "recorded_at")
        if moment.at < self.started_at:
            raise ValueError("an observation cannot predate the conversation start")
        if moment.recorded_at < moment.at:
            raise ValueError("recorded_at cannot precede the observed/reported time")
        if self._journal and moment.recorded_at < self._journal[-1].recorded_at:
            raise ValueError("recorded_at cannot move backward in an append-only journal")
        self._journal.append(moment)
        return moment

    def report_feeling(
        self,
        *,
        experienced_at: datetime,
        recorded_at: datetime,
        speaker: str,
        exact_words: str,
        report_mode: ReportMode,
    ) -> Moment:
        """Store reported feeling, never a mood deduced from words or silence."""
        if report_mode not in ("contemporaneous", "recollection"):
            raise ValueError("explicit report_mode is required")
        return self._record(
            Moment(
                "FELT_REPORT",
                _aware(experienced_at, "experienced_at"),
                _aware(recorded_at, "recorded_at"),
                _nonempty(speaker, "speaker"),
                words=_nonempty(exact_words, "exact_words"),
                report_mode=report_mode,
            )
        )

    def observe_no_reply(
        self,
        *,
        since: datetime,
        through: datetime,
        recorded_at: datetime,
        observer: str,
        evidence_ref: str,
    ) -> Moment:
        """Witness absence only in an explicitly checked, expected return window."""
        if not self.expected_return:
            raise ValueError("no expected return was declared for this conversation")
        start = _aware(since, "since")
        end = _aware(through, "through")
        if start < self.started_at or end < start:
            raise ValueError("invalid checked interval")
        if any(m.kind == "REPLY" and start <= m.at <= end for m in self._journal):
            raise ValueError("a recorded reply contradicts this no-reply interval")
        return self._record(
            Moment(
                "NO_REPLY_OBSERVED",
                end,
                _aware(recorded_at, "recorded_at"),
                _nonempty(observer, "observer"),
                since=start,
                evidence_ref=_nonempty(evidence_ref, "evidence_ref"),
            )
        )

    def observe_reply(
        self,
        *,
        at: datetime,
        recorded_at: datetime,
        observer: str,
        evidence_ref: str,
    ) -> Moment:
        """A late-discovered reply is retained even if it contradicts an earlier check."""
        return self._record(
            Moment(
                "REPLY",
                _aware(at, "at"),
                _aware(recorded_at, "recorded_at"),
                _nonempty(observer, "observer"),
                evidence_ref=_nonempty(evidence_ref, "evidence_ref"),
            )
        )

    def snapshot(self, at: datetime) -> dict:
        """Clock movement alone changes elapsed time, never the witness record."""
        now = _aware(at, "at")
        if now < self.started_at:
            raise ValueError("snapshot cannot precede start")
        known = [m for m in self._journal if m.recorded_at <= now]
        gaps = [m for m in known if m.kind == "NO_REPLY_OBSERVED"]
        replies = [m for m in known if m.kind == "REPLY"]
        reports = [m for m in known if m.kind == "FELT_REPORT"]
        conflicts = [
            {"no_reply_through": gap.at.isoformat(), "reply_at": reply.at.isoformat()}
            for gap in gaps
            for reply in replies
            if gap.since <= reply.at <= gap.at
        ]
        return {
            "referent": self.referent,
            "elapsed_seconds": (now - self.started_at).total_seconds(),
            "expected_return": self.expected_return,
            "no_reply_observed_through": max((m.at for m in gaps), default=None),
            "observed_no_reply_windows": tuple((m.since, m.at, m.evidence_ref) for m in gaps),
            "reported_feelings": tuple(
                (m.at, m.recorded_at, m.source, m.words, m.report_mode) for m in reports
            ),
            "observed_replies": tuple((m.at, m.evidence_ref) for m in replies),
            "conflicts": tuple(conflicts),
        }
