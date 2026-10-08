"""GitHub work-ledger → persistent handoffs → Ohayo agent birth integration."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime.repository_tasks import read_active_work, admit_active_work
from runtime.service import EcosystemService


SAMPLE = """# TASKS
## Active ALL WORK
| Work | Lane | State | Next movement |
|---|---|---|---|
| [Review ARC](research/ARC.md) | Research | MOVE | Follow next real witness. |
| [Repair runtime](runtime/README.md) | Operations | MOVE_WITH_WALL | Preserve wall and search sources. |
| [Historical foundation](foundation/README.md) | Archive | FROZEN / EVIDENCE | Preserve. |
## Pinned / resumable
| Work | Lane | State | Next movement |
|---|---|---|---|
| [Pinned game](research/pinned.md) | Research | PINNED | Do not admit. |
"""


class RepositoryConnectionTests(unittest.TestCase):
    def source(self, root):
        p = Path(root) / "TASKS.md"
        p.write_text(SAMPLE, encoding="utf-8")
        return p

    def test_only_explicit_active_rows_are_admitted(self):
        with TemporaryDirectory() as tmp:
            path = self.source(tmp)
            rows = read_active_work(path)
            self.assertEqual([x.title for x in rows], ["Review ARC", "Repair runtime"])
            svc = EcosystemService(data_dir=Path(tmp) / "state")
            ids = admit_active_work(svc.runtime, path)
            self.assertEqual(len(ids), 2)
            self.assertEqual(admit_active_work(svc.runtime, path), ())
            for id_ in ids:
                handoff = svc.runtime.get(id_)
                self.assertEqual(handoff.to_actor, "james")
                self.assertEqual(svc.runtime.state(id_).status, "READY")
                self.assertTrue(any(x.startswith("repository:") for x in handoff.provenance))
                self.assertEqual(handoff.metadata["source_system"], "repository")
            self.assertNotIn("Pinned game", [svc.runtime.get(x).referent for x in ids])

    def test_get_reports_work_connection_without_side_effects(self):
        with TemporaryDirectory() as tmp:
            path = self.source(tmp)
            svc = EcosystemService(data_dir=Path(tmp) / "state",
                                   repository_work_file=path)
            report = svc.activate("ohayo", actor_id="james")
            self.assertEqual(report["tasks"], [])
            self.assertEqual(report["agents"], [])
            self.assertEqual(report["repository_work"]["eligible_active_rows"], 2)
            self.assertEqual(len(svc.runtime.snapshot()), 0)
            con = svc.connections()
            self.assertTrue(con["handoff_runtime"]["durable"])
            self.assertFalse(con["agents"]["ab_evaluator_connected"])
            self.assertFalse(con["systems"]["online_school_registered"])
            self.assertFalse(con["systems"]["factory_registered"])
            self.assertTrue(con["repository_work"]["available"])

    def test_explicit_ohayo_admits_then_spawns_one_and_persists(self):
        with TemporaryDirectory() as tmp:
            path = self.source(tmp)
            svc = EcosystemService(data_dir=Path(tmp) / "state",
                                   repository_work_file=path)
            one = svc.ohayo(actor_id="james")
            self.assertEqual(len(one["repository_handoffs_admitted"]), 2)
            self.assertEqual(len(one["agent_spawned"]), 1)
            self.assertEqual(len(one["tasks"]), 2)
            self.assertEqual(one["agent_summary"]["ready"], 1)
            root = one["agent_spawned"][0]
            input_refs = [x["handoff_id"] for x in svc.runtime.get(root).inputs["task_handoffs"]]
            self.assertEqual(input_refs, one["repository_handoffs_admitted"])
            self.assertEqual(len(svc.runtime.snapshot()), 3)
            two = svc.ohayo(actor_id="james")
            self.assertEqual(two["agent_spawned"], [])
            self.assertEqual(two["repository_handoffs_admitted"], [])
            self.assertEqual(two["agent_roots"], [root])
            restarted = EcosystemService(data_dir=Path(tmp) / "state",
                                         repository_work_file=path)
            again = restarted.ohayo(actor_id="james")
            self.assertEqual(again["agent_spawned"], [])
            self.assertEqual(again["agent_roots"], [root])
            self.assertEqual(len(restarted.runtime.snapshot()), 3)

    def test_new_source_row_does_not_rebirth_existing_agent(self):
        with TemporaryDirectory() as tmp:
            path = self.source(tmp)
            svc = EcosystemService(data_dir=Path(tmp) / "state",
                                   repository_work_file=path)
            root = svc.ohayo(actor_id="james")["agent_spawned"][0]
            path.write_text(SAMPLE.replace("## Pinned / resumable",
                "| [Later](later.md) | Other | MOVE | Another candidate. |\n## Pinned / resumable"),
                encoding="utf-8")
            later = svc.ohayo(actor_id="james")
            self.assertEqual(later["agent_roots"], [root])
            self.assertEqual(later["agent_spawned"], [])
            self.assertEqual(later["repository_handoffs_admitted"], [])
            self.assertEqual(later["repository_work"]["eligible_active_rows"], 3)
            self.assertEqual(len(svc.runtime.snapshot()), 3)

    def test_empty_and_frozen_source_do_not_seed(self):
        with TemporaryDirectory() as tmp:
            path = self.source(tmp)
            path.write_text(SAMPLE.replace("MOVE_WITH_WALL", "PINNED")
                            .replace("| MOVE |", "| FROZEN |"), encoding="utf-8")
            svc = EcosystemService(data_dir=Path(tmp) / "state",
                                   repository_work_file=path)
            report = svc.ohayo(actor_id="james")
            self.assertEqual(report["agent_summary"]["total"], 0)
            self.assertEqual(report["repository_handoffs_admitted"], [])
            self.assertEqual(report["tasks"], [])

    def test_missing_source_fails_clearly(self):
        with TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(FileNotFoundError, "repository work source"):
                EcosystemService(data_dir=Path(tmp) / "state",
                                 repository_work_file=Path(tmp) / "missing.md")

    def test_invalid_repository_link_rejected_before_write(self):
        with TemporaryDirectory() as tmp:
            path = self.source(tmp)
            path.write_text(SAMPLE.replace("(research/ARC.md)", "(../secrets.txt)"),
                            encoding="utf-8")
            svc = EcosystemService(data_dir=Path(tmp) / "state")
            with self.assertRaisesRegex(ValueError, "unsafe repository link"):
                admit_active_work(svc.runtime, path)
            self.assertEqual(len(svc.runtime.snapshot()), 0)

    def test_documented_repository_ledger_has_active_source(self):
        source = Path(__file__).resolve().parents[2] / "TASKS.md"
        rows = read_active_work(source)
        self.assertTrue(rows, "online branch needs explicitly active tasks")
        self.assertTrue(all(row.state.startswith("MOVE") for row in rows))


if __name__ == "__main__":
    unittest.main()
