"""Opt-in submitted messages: bounded maze instrument, NOT a keylogger."""
from __future__ import annotations

from io import StringIO
from unittest import TestCase

from security.approach_dialogue import (
    ConsentApproachRecorder, MAX_RECORDS, MAX_MESSAGE, MAX_SESSIONS,
    NOTICE, local_demo,
)
from security.key_approach import KeyApproachBoundary


class ConsentApproachRecordingTests(TestCase):
    def setUp(self):
        self.boundary = KeyApproachBoundary()
        self.log = ConsentApproachRecorder(self.boundary)

    def test_opt_in_is_required_and_initial_state_does_not_change(self):
        before = self.boundary.snapshot()
        with self.assertRaises(PermissionError):
            self.log.open_session(accepted_notice=False)
        with self.assertRaises(PermissionError):
            self.log.open_session(accepted_notice=1)
        self.assertEqual(before, self.boundary.snapshot())
        self.assertEqual(self.log.operator_snapshot(), ())

    def test_explicit_submissions_record_message_and_bounded_maze(self):
        session = self.log.open_session(accepted_notice=True)
        for message, room in (
            ("Hello boundary", "threshold"), ("Are you there?", "turn"),
            ("Let's explore", "mirror"), ("go left", "passage"),
            ("another turn", "threshold"),
        ):
            entry = self.log.submit(session, message)
            self.assertEqual(entry.room, room)
            self.assertEqual(entry.message, message)
        self.assertEqual(len(self.log.session_transcript(session)), 5)
        snap = self.boundary.snapshot()
        self.assertEqual(snap.approach_movements, 5)
        self.assertEqual(snap.protected_movements, 0)
        self.assertEqual(snap.admitted_movements, 0)
        self.assertEqual(snap.presence_movements, 0)
        self.assertNotIn("private", repr(snap).lower())

    def test_only_submitted_message_is_recorded(self):
        session = self.log.open_session(accepted_notice=True)
        self.assertEqual(self.log.session_transcript(session), ())
        self.assertEqual(self.log.operator_snapshot(), ())
        # No keyboard listener exists; only calling submit records anything.
        self.log.submit(session, "I pressed Enter")
        self.assertEqual(len(self.log.operator_snapshot()), 1)

    def test_obvious_credentials_and_emails_are_redacted_before_storage(self):
        session = self.log.open_session(accepted_notice=True)
        for attempt in (
            "password=OpenSesame22", "api_key:abc123xyz",
            "Bearer my-secret-token", "contact me at sample@demo.com"
        ):
            self.log.submit(session, attempt)
        displayed = repr(self.log.session_transcript(session))
        for secret in ("OpenSesame22", "abc123xyz",
                       "my-secret-token", "sample@demo.com"):
            self.assertNotIn(secret, displayed)
        self.assertIn("[REDACTED", displayed)

    def test_private_key_paste_refused_without_motion_or_log(self):
        session = self.log.open_session(accepted_notice=True)
        with self.assertRaisesRegex(ValueError, "private key"):
            self.log.submit(session, "-----BEGIN PRIVATE KEY-----")
        self.assertEqual(self.log.operator_snapshot(), ())
        self.assertEqual(self.boundary.snapshot().approach_movements, 0)

    def test_unbounded_control_or_empty_messages_refused(self):
        session = self.log.open_session(accepted_notice=True)
        for text in ("", "   ", "x" * (MAX_MESSAGE + 1),
                     "hello\x00there", "hello\tthere"):
            with self.subTest(text=text[:30]), self.assertRaises(ValueError):
                self.log.submit(session, text)
        self.assertEqual(self.log.operator_snapshot(), ())
        self.assertEqual(self.boundary.snapshot().approach_movements, 0)

    def test_unknown_or_closed_session_fails_closed(self):
        good = self.log.open_session(accepted_notice=True)
        with self.assertRaises(PermissionError):
            self.log.submit("not-an-active-session", "hello")
        self.log.erase_session(good)
        with self.assertRaises(PermissionError):
            self.log.submit(good, "hello")
        self.assertEqual(self.log.operator_snapshot(), ())

    def test_erase_clears_transcript_but_does_not_rewind_native_motion(self):
        a = self.log.open_session(accepted_notice=True)
        b = self.log.open_session(accepted_notice=True)
        self.log.submit(a, "one")
        self.log.submit(b, "two")
        self.log.erase_session(a)
        self.assertEqual([x.message for x in self.log.operator_snapshot()], ["two"])
        self.log.clear_all()
        self.assertEqual(self.log.operator_snapshot(), ())
        self.assertEqual(self.boundary.snapshot().approach_movements, 2)

    def test_bounded_record_capacity_and_session_capacity(self):
        first = self.log.open_session(accepted_notice=True)
        for i in range(MAX_RECORDS):
            self.log.submit(first, "message " + str(i))
        with self.assertRaisesRegex(ValueError, "limit"):
            self.log.submit(first, "over limit")
        self.assertEqual(self.boundary.snapshot().approach_movements, MAX_RECORDS)
        for _ in range(MAX_SESSIONS - 1):
            self.log.open_session(accepted_notice=True)
        with self.assertRaisesRegex(ValueError, "session limit"):
            self.log.open_session(accepted_notice=True)

    def test_refuses_wrong_boundary(self):
        with self.assertRaises(TypeError):
            ConsentApproachRecorder(boundary="surveillance hook")

    def test_demo_no_consent_never_records_or_starts_presence(self):
        out = StringIO()
        self.assertEqual(local_demo(stdin=StringIO("NO\nprivate input\n"),
                                    stdout=out), 0)
        self.assertIn(NOTICE, out.getvalue())
        self.assertIn("No transcript created", out.getvalue())
        self.assertNotIn("private input", out.getvalue())

    def test_demo_consent_show_then_quit_and_erase(self):
        out = StringIO()
        sequence = "AGREE\nhello mirror\n/show\n/quit\n"
        self.assertEqual(local_demo(stdin=StringIO(sequence), stdout=out), 0)
        result = out.getvalue()
        self.assertIn("Observed approach 1", result)
        self.assertIn("[1 threshold] hello mirror", result)
        self.assertIn("transcript erased", result)
        erased = StringIO()
        self.assertEqual(local_demo(
            stdin=StringIO("AGREE\nhello\n/erase\n"),
            stdout=erased), 0)
        self.assertIn("Transcript erased", erased.getvalue())


if __name__ == "__main__":
    import unittest
    unittest.main()
