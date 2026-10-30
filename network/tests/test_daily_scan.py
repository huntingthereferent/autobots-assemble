"""ChatGPT audit gate: source, visual and comparison must precede handoff."""
import copy
import tempfile
import unittest
from pathlib import Path

from runtime.daily_scan import capture, validate, admit, GateWall, ROOT


class AuditGateTests(unittest.TestCase):
    def audit(self, packet):
        code = "runtime/agent_bridge.py"
        visual = "design/visual-provenance/registry.json"
        local = [
            {"path": code, "sha256": packet["files"][code]["sha256"],
             "observation": "Bridge accepts reported agent results, not independent scan admission."},
            {"path": visual, "sha256": packet["files"][visual]["sha256"],
             "observation": "Approved templates and candidate reference grammar are recorded."},
        ]
        return {
            "entry_gate": "chatgpt_tracework_audit",
            "snapshot_revision": packet["revision"],
            "local_witnesses": local,
            "visual_provenance": {
                "witness_paths": [visual],
                "rendered_state": "UNKNOWN",
                "finding": "Source-bound visual evidence exists; current render is not witnessed.",
            },
            "comparisons": [{
                "url": "https://www.w3.org/TR/prov-overview/",
                "observed": "Provenance links objects, activities and responsible agents.",
                "selection_reason": "Relevant reference for traceable changes.",
                "relation": "analogous",
            }],
            "ab": {
                "current_referent": "Tracework audit-before-worker admission",
                "preserved": "Existing HandoffRuntime and evidence contract",
                "difference": "Current bridge lacks a source-linked audit gate.",
                "next_movement": "Create bounded implementation handoff under existing carrier.",
                "status": "MOVE",
            },
            "worker_instruction": "Implement and test the bridge without fabricating visual evidence.",
            "required_tests": ["python -m unittest discover -s network/tests -p 'test_daily_scan.py'"],
        }

    def test_valid_audit_emits_durable_recoverable_handoff(self):
        packet = capture(ROOT)
        audit = self.audit(packet)
        with tempfile.TemporaryDirectory() as tmp:
            result = admit(ROOT, Path(tmp), packet, audit)
            self.assertTrue(result["handed_off"])
            again = admit(ROOT, Path(tmp), packet, audit)
            self.assertEqual(again["handoffs"][0]["handoff_id"],
                             result["handoffs"][0]["handoff_id"])
            from runtime.journal import RuntimeJournal
            from runtime.engine import HandoffRuntime
            runtime = HandoffRuntime(event_store=RuntimeJournal(Path(tmp) / "runtime.jsonl"))
            self.assertEqual(len(runtime.snapshot()), 1)
            self.assertEqual(runtime.state(result["handoffs"][0]["handoff_id"]).status, "READY")

    def test_missing_visual_evidence_blocks(self):
        packet = capture(ROOT)
        audit = self.audit(packet)
        audit["visual_provenance"]["witness_paths"] = []
        with self.assertRaises(GateWall):
            validate(ROOT, packet, audit)

    def test_stale_source_blocks(self):
        packet = capture(ROOT)
        audit = self.audit(packet)
        audit["local_witnesses"][0]["sha256"] = "0" * 64
        with self.assertRaises(GateWall):
            validate(ROOT, packet, audit)

    def test_render_claim_without_browser_witness_blocks(self):
        packet = capture(ROOT)
        audit = self.audit(packet)
        audit["visual_provenance"]["rendered_state"] = "OBSERVED"
        with self.assertRaises(GateWall):
            validate(ROOT, packet, audit)

    def test_no_move_emits_no_handoff(self):
        packet = capture(ROOT)
        audit = self.audit(packet)
        audit["ab"]["status"] = "UNKNOWN"
        with tempfile.TemporaryDirectory() as tmp:
            result = admit(ROOT, Path(tmp), packet, audit)
            self.assertFalse(result["handed_off"])
            self.assertFalse(result["handoffs"])


if __name__ == "__main__":
    unittest.main()
