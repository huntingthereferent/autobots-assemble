import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from runtime.journal import RuntimeJournal
from runtime.handoff import Handoff, HandoffEvent


class ABJournalGateTests(unittest.TestCase):
    def test_submission_and_recovery(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "journal.jsonl"
            journal = RuntimeJournal(path)
            handoff = Handoff("ab-gate-1", "actual referent", "source", "receiver", "compare")
            created = HandoffEvent.create(handoff_id=handoff.handoff_id,
                                          event_type="CREATED", actor_id="source")
            journal.append_submission(handoff, created)
            self.assertEqual(len(RuntimeJournal(path).all()), 1)
            self.assertEqual(len(journal.all()), 1)

    def test_unknown_event_does_not_write(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "journal.jsonl"
            journal = RuntimeJournal(path)
            handoff = Handoff("ab-gate-2", "actual referent", "source", "receiver", "compare")
            created = HandoffEvent.create(handoff_id=handoff.handoff_id,
                                          event_type="CREATED", actor_id="source")
            journal.append_submission(handoff, created)
            prior = path.read_bytes()
            bad = HandoffEvent.create(handoff_id=handoff.handoff_id,
                                      event_type="INVENTED", actor_id="source",
                                      parents=(created.event_id,))
            with self.assertRaises(ValueError):
                journal.append(bad)
            self.assertEqual(path.read_bytes(), prior)

    def test_unknown_handoff_cannot_enter(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "journal.jsonl"
            journal = RuntimeJournal(path)
            event = HandoffEvent.create(handoff_id="missing",
                                        event_type="RESULT", actor_id="source")
            with self.assertRaises(ValueError):
                journal.append(event)
            self.assertFalse(path.exists())


    def test_replay_of_event_and_rejected_corruption(self):
        import json
        from runtime.journal import event_to_dict
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "journal.jsonl"
            journal = RuntimeJournal(path)
            handoff = Handoff("ab-gate-replay", "referent", "source", "receiver", "compare")
            created = HandoffEvent.create(handoff_id=handoff.handoff_id,
                                          event_type="CREATED", actor_id="source")
            journal.append_submission(handoff, created)
            observed = HandoffEvent.create(handoff_id=handoff.handoff_id,
                                           event_type="WORKSTATION_MOVEMENT_OBSERVED",
                                           actor_id="source", parents=(created.event_id,))
            journal.append(observed)
            self.assertEqual(len(RuntimeJournal(path).all()), 2)
            corrupted = HandoffEvent.create(handoff_id=handoff.handoff_id,
                                            event_type="WORKSTATION_MOVEMENT_OBSERVED",
                                            actor_id="source", parents=(created.event_id,))
            with path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps({"record_type": "EVENT",
                                         "event": event_to_dict(corrupted)}) + "\n")
            with self.assertRaises(ValueError):
                RuntimeJournal(path)

if __name__ == "__main__":
    unittest.main()
