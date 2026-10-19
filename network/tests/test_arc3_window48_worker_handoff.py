"""Adversarial original-source tests for the bounded WORLD48 worker handoff."""
from __future__ import annotations

from copy import deepcopy
import unittest

from work.arc3.window48_worker_handoff import (
    content_digest, produce_record, verify_record,
)


def reseal(packet):
    payload = {k: v for k, v in packet.items() if k != "payload_sha256"}
    packet["payload_sha256"] = content_digest(payload)


class Window48WorkerHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = produce_record()

    def test_all_source_workers_replay_and_event_counts(self):
        report = verify_record(self.packet)
        self.assertTrue(report["verified"])
        self.assertEqual(report["challenges"], 48)
        self.assertEqual(report["witnesses"], 48)
        self.assertEqual(report["action_events_replayed"], self.packet["claims"]["action_events"])
        self.assertGreater(report["action_events_replayed"], 0)
        self.assertFalse(report["native_arc_evidence"])
        self.assertFalse(report["w13_evidence"])

    def test_trial_order_is_not_an_arbitrary_literal_witness_gate(self):
        packet = deepcopy(self.packet)
        packet["certificates"][0]["trials"].reverse()
        reseal(packet)
        self.assertTrue(verify_record(packet)["verified"])

    def test_checksum_must_match_original_packet(self):
        packet = deepcopy(self.packet)
        packet["claims"]["action_events"] += 1
        with self.assertRaisesRegex(ValueError, "checksum"):
            verify_record(packet)

    def test_resealed_forged_events_and_claims_rejected(self):
        edits = [
            lambda p: p["certificates"][2]["trials"][0]["events"][0]["after"].__setitem__(0, 26),
            lambda p: p["certificates"][3]["trials"][1]["final"].__setitem__(\n                1, (p["certificates"][3]["trials"][1]["final"][1] + 1) % 27\n            ),
            lambda p: p["certificates"][4]["verdict"].__setitem__("passed", False),
            lambda p: p["claims"].__setitem__("witnesses", 49),
            lambda p: p["certificates"].pop(),
            lambda p: p["certificates"].__setitem__(1, deepcopy(p["certificates"][0])),
            lambda p: p.__setitem__("scope", "native-arc"),
            lambda p: p["source_digests"].__setitem__(
                "work/arc_like_maze/window_combined.py", "0"*64
            ),
        ]
        for i, edit in enumerate(edits):
            with self.subTest(edit=i):
                packet = deepcopy(self.packet)
                edit(packet)
                reseal(packet)
                with self.assertRaises(ValueError):
                    verify_record(packet)

    def test_unexpected_fields_rejected_even_if_checksum_recomputed(self):
        packet = deepcopy(self.packet)
        packet["external_native_win"] = True
        reseal(packet)
        with self.assertRaises(ValueError):
            verify_record(packet)


if __name__ == "__main__":
    unittest.main()
