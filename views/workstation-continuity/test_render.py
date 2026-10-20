"""Tests for read-only projection of the EXISTING ProcessWorkstation state."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace
from tempfile import TemporaryDirectory
import unittest
import xml.etree.ElementTree as ET

from systems.workspace.workstation import ProcessWorkstation
from systems.workspace.monitor import workstation_snapshot

FILE = Path(__file__).with_name("render.py")
spec = importlib.util.spec_from_file_location("workstation_visual_renderer", FILE)
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


def source():
    return {
        "schema_version": 1,
        "read_only": True,
        "worker_execution_triggered": False,
        "runtime_execution_connected_by_view": False,
        "editions": [
            {"worker_id": "w1", "version_id": "one", "parent_version": None,
             "state": "AVAILABLE", "source_modified": False,
             "modified": [], "added": [], "deleted": [],
             "current_fingerprint": "a" * 64},
            {"worker_id": "w1", "version_id": "two", "parent_version": "one",
             "state": "AVAILABLE", "source_modified": True,
             "modified": ["private-secret-file.py"], "added": [], "deleted": [],
             "current_fingerprint": "b" * 64},
        ],
        "jobs": [
            {"job_id": "bounded-1", "worker_id": "w1", "version_id": "two",
             "status": "COMPLETE", "source_state": "MATCHES_ADMISSION",
             "verification": "recorded-not-reverified",
             "result": {"dont-export": "private-result"}},
        ],
    }


class VisualTests(unittest.TestCase):
    def test_existing_native_editions_and_return_are_read_not_replayed(self):
        data = renderer.project_native(source())
        self.assertEqual(data["counts"]["editions"], 2)
        self.assertEqual(data["counts"]["edited_editions"], 1)
        self.assertEqual(data["counts"]["admitted_jobs"], 1)
        self.assertEqual(data["parent_edges"],
                         [{"kind": "edition-parent", "from": "w1/one", "to": "w1/two"}])
        self.assertEqual(data["jobs"][0]["verification"], "recorded-not-reverified")
        self.assertNotIn("private-secret-file", str(data))
        self.assertNotIn("private-result", str(data))
        svg = renderer.render_svg(data)
        ET.fromstring(svg)
        self.assertIn("WORKSTATION / SOURCE CONTINUITY", svg)
        self.assertIn("not freshly reverified", svg.lower())

    def test_unknown_parent_is_not_invented(self):
        raw = source()
        raw["editions"][1]["parent_version"] = "missing-version"
        data = renderer.project_native(raw)
        self.assertEqual(data["parent_edges"], [])

    def test_rejects_tamper_duplicate_and_misleading_source(self):
        raw = source()
        raw["editions"][1]["source_modified"] = False
        with self.assertRaises(ValueError):
            renderer.project_native(raw)
        raw = source()
        raw["worker_execution_triggered"] = True
        with self.assertRaises(ValueError):
            renderer.project_native(raw)
        raw = source()
        raw["editions"].append(dict(raw["editions"][0]))
        with self.assertRaises(ValueError):
            renderer.project_native(raw)
        raw = source()
        raw["editions"][0]["worker_id"] = "../../bad"
        with self.assertRaises(ValueError):
            renderer.project_native(raw)

    def test_real_process_workstation_copy_edit_branch_projections(self):
        with TemporaryDirectory() as tmp:
            home = Path(tmp)
            src = home / "original"
            src.mkdir()
            (src / "worker.py").write_text("print(1)\n")
            desk = ProcessWorkstation(home / "private-editions")
            desk.copy_source(src, worker_id="finite", version_id="v1")
            (home / "private-editions" / "finite" / "v1" / "worker.py").write_text("print(2)\n")
            desk.branch(worker_id="finite", parent_version="v1", version_id="v2")
            # The original monitor owns source ancestry and observes real file edits.
            native = workstation_snapshot(root=home / "private-editions",
                                          runtime=SimpleNamespace(_handoffs={}))
            projected = renderer.project_native(native)
            self.assertEqual(projected["counts"]["editions"], 2)
            self.assertEqual(projected["counts"]["edited_editions"], 1)
            self.assertEqual(projected["parent_edges"],
                             [{"kind": "edition-parent",
                               "from": "finite/v1", "to": "finite/v2"}])
            self.assertEqual(projected["counts"]["admitted_jobs"], 0)
            self.assertFalse(projected["executed_by_this_view"])


if __name__ == "__main__":
    unittest.main()
