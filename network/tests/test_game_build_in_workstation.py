"""Integration: WORLD tasks cause bounded ProcessWorkstation BUILD to create playable HTML."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.controls import reverify_job
from systems.workspace.game_build_native import verify_build, check_world
from systems.workspace.game_build_stack import construct, JOB_ID
from systems.workspace.game_build_bridge import WORKER_ID
from systems.workspace.workstation import ProcessWorkstation

ROOT = Path(__file__).resolve().parents[2]
WORLDS = [
    ROOT / "network/tests/fixtures/game_build_world_next.json",
    ROOT / "network/tests/fixtures/game_build_world_alternate.json",
]


class GameBuildInWorkstationTests(unittest.TestCase):
    def setUp(self):
        t = TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        self.data = self.root/"native"
        self.out = self.root/"published"
        self.world = json.loads(WORLDS[0].read_text())

    def test_01_real_worker_constructs_new_playable_room(self):
        report = construct(data_dir=self.data, world=self.world, output_dir=self.out)
        self.assertEqual(report["BUILD_native_execution"], "COMPLETE")
        self.assertEqual(report["WITNESS_native_w12"], "PASS")
        self.assertTrue(report["subprocess_did_build_new_artifact"])
        self.assertGreater(report["plan_length"], 1)
        self.assertTrue((self.out/"built-world-room.html").is_file())
        self.assertIn(self.world["world_id"],(self.out/"built-world-room.html").read_text())
        runtime=HandoffRuntime(event_store=RuntimeJournal(self.data/"runtime.jsonl"))
        self.assertEqual(runtime.get(JOB_ID).metadata["worker_id"], WORKER_ID)
        self.assertEqual(runtime.state(JOB_ID).status,"COMPLETE")
        self.assertEqual(reverify_job(data_dir=self.data,job_id=JOB_ID)["status"],"COMPLETE")

    def test_02_second_distinct_WORLD_constructs_different_playable_room(self):
        first=construct(data_dir=self.data,world=self.world,output_dir=self.out)
        alternate=json.loads(WORLDS[1].read_text())
        other=construct(data_dir=self.root/"other-native",world=alternate,
                        output_dir=self.root/"other-published")
        self.assertNotEqual(first["html_sha256"],other["html_sha256"])
        self.assertNotEqual(first["plan"],other["plan"])
        self.assertEqual(other["world_id"],"fourth-room")
        self.assertEqual(other["WITNESS_native_w12"],"PASS")

    def test_03_repeat_verified_job_does_not_execute_twice(self):
        first=construct(data_dir=self.data,world=self.world,output_dir=self.out)
        before=(self.data/"runtime.jsonl").read_bytes()
        second=construct(data_dir=self.data,world=self.world,output_dir=self.out)
        self.assertEqual(first,second)
        self.assertEqual((self.data/"runtime.jsonl").read_bytes(),before)

    def test_04_native_witness_rejects_forged_build(self):
        construct(data_dir=self.data,world=self.world,output_dir=self.out)
        rt=HandoffRuntime(event_store=RuntimeJournal(self.data/"runtime.jsonl"))
        built=rt.state(JOB_ID).output["build"]
        for change in ("html","plan","world"):
            altered=json.loads(json.dumps(built))
            if change=="html":
                altered["html"]=altered["html"].replace('id="reset"','id="missing"')
            elif change=="plan":
                altered["plan"]=altered["plan"][:-1]
            else:
                altered["world"]["spec"]["width"]=9
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    verify_build(self.world,altered)

    def test_05_mutated_worker_source_revokes_fresh_reverification(self):
        construct(data_dir=self.data,world=self.world,output_dir=self.out)
        desk=ProcessWorkstation(self.data/"workstation")
        edition=desk._edition(WORKER_ID,"source-v1")
        f=edition/"room_builder.py"
        f.write_text(f.read_text()+"\n# mutated\n")
        with self.assertRaises(ValueError):
            reverify_job(data_dir=self.data,job_id=JOB_ID)

    def test_06_malformed_WORLD_cannot_create_job(self):
        bad=json.loads(json.dumps(self.world))
        bad["spec"]["target"]=[99,2]
        with self.assertRaises(ValueError):
            construct(data_dir=self.data,world=bad,output_dir=self.out)
        self.assertFalse((self.data/"runtime.jsonl").exists())

    def test_07_preserved_W13_original_and_game_builder_are_distinct(self):
        from systems.workspace.game_w13_native_bridge import WORKER_ID as W13
        self.assertNotEqual(WORKER_ID,W13)
        self.assertNotEqual(self.world["contract"],"game-w13-multiworld-v1")


if __name__=="__main__":
    unittest.main()
