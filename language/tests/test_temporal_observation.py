"""Native checks for timed observation without inferred feelings or invented replies."""

from datetime import datetime, timedelta, timezone
import unittest

from language.words.temporal_observation import ConversationTrace


START = datetime(2026, 10, 16, 18, 0, tzinfo=timezone.utc)


def later(seconds: int) -> datetime:
    return START + timedelta(seconds=seconds)


class TemporalObservationTests(unittest.TestCase):
    def test_feeling_is_reported_at_the_first_moment_not_after_the_flow(self):
        flow = ConversationTrace("discussion", START, expected_return=True)
        flow.report_feeling(
            experienced_at=START, recorded_at=START, speaker="speaker",
            exact_words="I noticed the pause immediately", report_mode="contemporaneous"
        )
        flow.observe_no_reply(
            since=START, through=START, recorded_at=START,
            observer="chat source", evidence_ref="source://checked-0"
        )
        state = flow.snapshot(START)
        self.assertEqual(state["elapsed_seconds"], 0)
        self.assertEqual(len(state["reported_feelings"]), 1)
        self.assertEqual(state["no_reply_observed_through"], START)

    def test_time_passes_without_fabricating_a_new_observation(self):
        flow = ConversationTrace("discussion", START, expected_return=True)
        flow.observe_no_reply(
            since=START, through=later(10), recorded_at=later(10),
            observer="chat source", evidence_ref="source://checked-10"
        )
        state = flow.snapshot(later(300))
        self.assertEqual(state["elapsed_seconds"], 300)
        self.assertEqual(state["no_reply_observed_through"], later(10))
        self.assertEqual(state["reported_feelings"], ())

    def test_changed_feelings_are_two_reports_not_one_derived_state(self):
        flow = ConversationTrace("discussion", START, expected_return=True)
        flow.report_feeling(
            experienced_at=START, recorded_at=START, speaker="person",
            exact_words="Something changed immediately", report_mode="contemporaneous"
        )
        flow.report_feeling(
            experienced_at=later(180), recorded_at=later(180), speaker="person",
            exact_words="Now the same silence feels different", report_mode="contemporaneous"
        )
        reports = flow.snapshot(later(300))["reported_feelings"]
        self.assertEqual([x[3] for x in reports], [
            "Something changed immediately", "Now the same silence feels different"
        ])
        self.assertEqual(len(flow.journal), 2)

    def test_later_memory_does_not_replace_earlier_words(self):
        flow = ConversationTrace("discussion", START)
        first = flow.report_feeling(
            experienced_at=START, recorded_at=START, speaker="person",
            exact_words="first impression", report_mode="contemporaneous"
        )
        flow.report_feeling(
            experienced_at=later(30), recorded_at=later(3600), speaker="person",
            exact_words="looking back, I remember it differently", report_mode="recollection"
        )
        reports = flow.snapshot(later(3600))["reported_feelings"]
        self.assertEqual(reports[0][3], first.words)
        self.assertEqual(reports[1][4], "recollection")
        self.assertEqual(len(flow.snapshot(later(100))["reported_feelings"]), 1)

    def test_no_expected_reply_means_no_silence_claim(self):
        flow = ConversationTrace("discussion", START)
        with self.assertRaises(ValueError):
            flow.observe_no_reply(
                since=START, through=later(1), recorded_at=later(1),
                observer="screen", evidence_ref="source://screen"
            )

    def test_observed_reply_prevents_contradictory_new_absence(self):
        flow = ConversationTrace("discussion", START, expected_return=True)
        flow.observe_reply(at=later(10), recorded_at=later(10), observer="chat", evidence_ref="reply:1")
        with self.assertRaises(ValueError):
            flow.observe_no_reply(
                since=START, through=later(30), recorded_at=later(30),
                observer="chat", evidence_ref="check:1"
            )

    def test_late_discovered_reply_preserves_and_marks_conflicting_evidence(self):
        flow = ConversationTrace("discussion", START, expected_return=True)
        flow.observe_no_reply(
            since=START, through=later(60), recorded_at=later(60),
            observer="chat", evidence_ref="check:1"
        )
        flow.observe_reply(
            at=later(30), recorded_at=later(90), observer="chat", evidence_ref="reply:late"
        )
        snapshot = flow.snapshot(later(90))
        self.assertEqual(snapshot["no_reply_observed_through"], later(60))
        self.assertEqual(len(snapshot["conflicts"]), 1)
        self.assertEqual(len(flow.journal), 2)

    def test_naive_time_and_missing_source_cannot_be_admitted(self):
        with self.assertRaises(ValueError):
            ConversationTrace("discussion", datetime(2026, 10, 16))
        flow = ConversationTrace("discussion", START, expected_return=True)
        with self.assertRaises(ValueError):
            flow.observe_no_reply(
                since=START, through=later(5), recorded_at=later(5),
                observer="screen", evidence_ref=""
            )
        with self.assertRaises(ValueError):
            flow.report_feeling(
                experienced_at=later(5), recorded_at=START,
                speaker="person", exact_words="felt", report_mode="contemporaneous"
            )

    def test_append_order_is_recording_order_not_retrospective_experience(self):
        flow = ConversationTrace("discussion", START)
        flow.report_feeling(
            experienced_at=later(10), recorded_at=later(100),
            speaker="person", exact_words="recalled", report_mode="recollection"
        )
        with self.assertRaises(ValueError):
            flow.report_feeling(
                experienced_at=later(20), recorded_at=later(50),
                speaker="person", exact_words="cannot backdate journal", report_mode="recollection"
            )


if __name__ == "__main__":
    unittest.main()
