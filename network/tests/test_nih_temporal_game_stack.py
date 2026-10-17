"""One Complete Stack actually executes the existing NIH temporal workers and game BUILDER."""
from __future__ import annotations
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.nih_temporal_game_stack import join


class NIHTemporalGameStackTests(unittest.TestCase):
    def setUp(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.data = Path(tmp.name) / "shared-native"
        self.out = Path(tmp.name) / "created"

    def test_01_real_nih_workers_and_game_build_share_original_native_runtime(self):
        result = join(data_dir=self.data, output_dir=self.out)
        self.assertEqual(result["witnessed_nih_phase_1"], [
            "NIH-P1-ONTOLOGY", "NIH-P1-REASONING", "NIH-P1-SCOPE"])
        self.assertEqual(result["next_phase_1"], "NIH-P1-PACKET")
        self.assertEqual(result["phase_2_test"], "BLOCKED")
        self.assertIn("NIH-P1-PACKET", result["phase_2_test_blocked_by"])
        self.assertTrue(result["one_native_workstation"])
        self.assertTrue(result["synthetic_only"])
        self.assertEqual(result["game_native_build"], "COMPLETE")
        self.assertEqual(result["game_browser_witness"], "NOT_RUN")
        self.assertTrue((self.out / "built-world-room.html").is_file())
        journal = HandoffRuntime(event_store=RuntimeJournal(self.data / "runtime.jsonl"))
        self.assertEqual(len(journal.snapshot()), 4)
        for job in result["exact_nih_jobs"] + [result["native_game_build_job"]]:
            self.assertEqual(journal.state(job).status, "COMPLETE")

    def test_02_restart_does_not_reexecute_any_native_job(self):
        first = join(data_dir=self.data, output_dir=self.out)
        before = (self.data / "runtime.jsonl").read_bytes()
        indexes = (self.data / "coordinator-windows.jsonl").read_bytes()
        second = join(data_dir=self.data, output_dir=self.out)
        self.assertEqual(first, second)
        self.assertEqual((self.data / "runtime.jsonl").read_bytes(), before)
        self.assertEqual((self.data / "coordinator-windows.jsonl").read_bytes(), indexes)

    def test_04_native_packet_worker_builds_source_derived_local_proposal(self):
        packet=join(data_dir=self.data, output_dir=self.out, packet_build=True)
        self.assertEqual(packet["packet_native_witness"],"PASS")
        self.assertEqual(packet["packet_worker"],"nih-phase1-packet")
        self.assertEqual(packet["packet_job"],"nih-packet-001")
        self.assertEqual(packet["next_prototype"],"NIH-P2-PROTOTYPE")
        self.assertFalse(packet["official_submission"])
        self.assertEqual(packet["next_phase_1"],"NIH-P1-SUBMISSION-EXTERNAL")
        self.assertEqual(packet["phase_2_test"],"BLOCKED")
        self.assertNotIn("NIH-P1-PACKET",packet["phase_2_test_blocked_by"])
        text=(self.out/"nih-phase1-temporal-design-packet.md").read_text(encoding="utf8")
        self.assertIn("## Temporal benchmark cases",text)
        self.assertIn("before-result",text)
        self.assertIn("delayed-result",text)
        self.assertIn("future",text)
        self.assertIn("Not an NIH submission",text)
        runtime=HandoffRuntime(event_store=RuntimeJournal(self.data/"runtime.jsonl"))
        child=runtime.get("nih-packet-001")
        self.assertEqual(child.dependencies,("nih-reasoning-001",))
        self.assertEqual(child.metadata["checkpoint_contract"],"NIH-P1-PACKET")
        self.assertEqual(runtime.state("nih-packet-001").status,"COMPLETE")
        self.assertEqual(len(runtime.snapshot()),5)

    def test_05_packet_replays_without_double_running_or_index_duplication(self):
        original=join(data_dir=self.data,output_dir=self.out,packet_build=True)
        journal=(self.data/"runtime.jsonl").read_bytes()
        index=(self.data/"coordinator-windows.jsonl").read_bytes()
        replay=join(data_dir=self.data,output_dir=self.out,packet_build=True)
        self.assertEqual(original,replay)
        self.assertEqual(journal,(self.data/"runtime.jsonl").read_bytes())
        self.assertEqual(index,(self.data/"coordinator-windows.jsonl").read_bytes())

    def test_06_mutated_packet_worker_refuses_native_reverification(self):
        join(data_dir=self.data,output_dir=self.out,packet_build=True)
        from systems.workspace.workstation import ProcessWorkstation
        desk=ProcessWorkstation(self.data/"workstation")
        source=desk._edition("nih-phase1-packet","packet-v1")/"packet_worker.py"
        source.write_text(source.read_text(encoding="utf8")+"\n# bad edit\n",encoding="utf8")
        with self.assertRaises(ValueError):
            join(data_dir=self.data,output_dir=self.out,packet_build=True)

    def test_07_real_runnable_phase2_prototype_consumes_verified_phase1(self):
        import json
        import subprocess
        import sys
        result=join(data_dir=self.data,output_dir=self.out,
                    packet_build=True,prototype_build=True)
        self.assertEqual(result["phase_2_prototype"],"WITNESSED")
        self.assertEqual(result["phase_2_game_test"],"BLOCKED")
        self.assertEqual(result["prototype_native_witness"],"PASS")
        self.assertGreater(result["prototype_hidden_queries"],0)
        self.assertGreater(result["prototype_static_leakage_examples"],0)
        self.assertNotIn("NIH-P2-PROTOTYPE",result["phase_2_test_blocked_by"])
        self.assertEqual(len(result["witnessed_nih_phase_1"]),5)
        runtime=HandoffRuntime(event_store=RuntimeJournal(self.data/"runtime.jsonl"))
        child=runtime.get("nih-prototype-001")
        self.assertEqual(child.dependencies,("nih-reasoning-001","nih-packet-001"))
        self.assertEqual(runtime.state(child.handoff_id).status,"COMPLETE")
        self.assertEqual(len(runtime.snapshot()),6)
        source=self.out/"temporal_query.py"
        dataset=self.out/"temporal_dataset.json"
        self.assertTrue(source.is_file())
        self.assertTrue(dataset.is_file())
        def query(known,target):
            r=subprocess.run([sys.executable,str(source),str(dataset)],
                             input=json.dumps({"known_at":known,"target_at":target}),
                             text=True,capture_output=True,timeout=5,check=True)
            return json.loads(r.stdout)
        before=query("2026-01-04","2026-01-04")
        after=query("2026-01-06","2026-01-04")
        self.assertEqual(before["temporal_ids"],["prior-note"])
        self.assertEqual(before["static_snapshot_ids"],["delayed-result","prior-note"])
        self.assertEqual(before["future_leakage_ids"],["delayed-result"])
        self.assertEqual(after["future_leakage_ids"],[])
        self.assertIn("delayed-result",after["temporal_ids"])
        self.assertEqual(before["clinical_verdict"],"NOT_EVALUATED")

    def test_08_prototype_restart_reuses_original_workstation_jobs(self):
        first=join(data_dir=self.data,output_dir=self.out,
                   packet_build=True,prototype_build=True)
        journal=(self.data/"runtime.jsonl").read_bytes()
        index=(self.data/"coordinator-windows.jsonl").read_bytes()
        second=join(data_dir=self.data,output_dir=self.out,
                    packet_build=True,prototype_build=True)
        self.assertEqual(first,second)
        self.assertEqual(journal,(self.data/"runtime.jsonl").read_bytes())
        self.assertEqual(index,(self.data/"coordinator-windows.jsonl").read_bytes())

    def test_09_unverified_prototype_source_cannot_replay(self):
        join(data_dir=self.data,output_dir=self.out,
             packet_build=True,prototype_build=True)
        from systems.workspace.workstation import ProcessWorkstation
        desk=ProcessWorkstation(self.data/"workstation")
        source=desk._edition("nih-temporal-prototype","prototype-v1")/"prototype_worker.py"
        source.write_text(source.read_text(encoding="utf8")+"\n# untrusted edit\n",encoding="utf8")
        with self.assertRaises(ValueError):
            join(data_dir=self.data,output_dir=self.out,
                 packet_build=True,prototype_build=True)

    def test_10_prototype_refuses_missing_packet_parent(self):
        with self.assertRaises(ValueError):
            join(data_dir=self.data,output_dir=self.out,
                 packet_build=False,prototype_build=True)

    def test_03_damaged_temporal_source_refuses_inherited_success(self):
        join(data_dir=self.data, output_dir=self.out)
        from systems.workspace.workstation import ProcessWorkstation
        desk = ProcessWorkstation(self.data / "workstation")
        src = desk._edition("nih-temporal-reasoning", "reasoning-v1") / "reasoning_worker.py"
        src.write_text(src.read_text() + "\n# unauthorized mutation\n")
        with self.assertRaises(ValueError):
            join(data_dir=self.data, output_dir=self.out)

if __name__ == "__main__":
    unittest.main()
