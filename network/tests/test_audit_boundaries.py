"""Audit regressions: routing, retired writers, local monitoring, native source evidence."""
from pathlib import Path
import unittest

from systems.workspace.research_observatory import ROOT, research_snapshot
from views.traces.research_live import projection


class AuditBoundaryTests(unittest.TestCase):
    def test_current_referent_is_not_assigned_from_historical_pointer(self):
        scope=(ROOT/"SCOPE.md").read_text(encoding="utf-8")
        entry=(ROOT/"ENTRY.md").read_text(encoding="utf-8")
        state=(ROOT/"state/current.json").read_text(encoding="utf-8")
        self.assertIn("active conversation",scope)
        self.assertIn("status: historical",scope)
        self.assertIn("historical",entry)
        self.assertIn('"status": "historical"',state)

    def test_old_income_generator_cannot_overwrite_current_tasks(self):
        self.assertFalse((ROOT/"tools/generate_work_views.py").exists())
        self.assertFalse((ROOT/"tools/generate_ab_views.py").exists())
        self.assertFalse((ROOT/"views/work_state.json").exists())
        self.assertFalse((ROOT/"jobs").exists())
        tasks=(ROOT/"TASKS.md").read_text(encoding="utf-8")
        self.assertIn("Active ALL WORK",tasks)
        self.assertIn("Swallow-first Boundary Adapter",tasks)

    def test_retired_work_is_absent_from_workstation(self):
        tasks=(ROOT/"TASKS.md").read_text()
        self.assertNotIn("St. Joseph",tasks)
        self.assertNotIn("Program Foundation",tasks)
        source=research_snapshot()
        self.assertNotIn("work/projects/st-joseph-complete-stack/",str(source))
        self.assertNotIn("foundation/PROGRAM_FOUNDATION.md",str(source))

    def test_public_projection_preserves_source_classification(self):
        research=research_snapshot()
        exported=projection(research)
        self.assertTrue(exported["movements"])
        self.assertEqual(len({m["id"] for m in exported["movements"]}),len(exported["movements"]))
        self.assertTrue(any(m["evidence"]=="structured-source-state" and
                            m["state"]=="MOVE_WITH_WALL" for m in exported["movements"]))
        self.assertTrue(any(m["evidence"]=="documented-heading-only" and
                            isinstance(m["line"],int) for m in exported["movements"]))
        self.assertTrue(all(m["evidence"] in ("structured-source-state","documented-heading-only")
                            for m in exported["movements"]))
        self.assertTrue(all(m["path"] for m in exported["movements"]))
        self.assertNotIn("native_execution",str(exported["movements"]).lower())

    def test_local_compose_requires_explicit_passwords_and_loopback_ports(self):
        compose=(ROOT/"work/projects/public-data-monitor/docker-compose.yml").read_text()
        self.assertIn("${MONITOR_DB_PASSWORD:?Set_MONITOR_DB_PASSWORD}",compose)
        self.assertIn("${GRAFANA_ADMIN_PASSWORD:?Set_GRAFANA_ADMIN_PASSWORD}",compose)
        self.assertNotIn("GF_SECURITY_ADMIN_PASSWORD: admin",compose)
        self.assertNotIn("postgresql+psycopg://monitor:monitor@",compose)
        for mapping in ("8000:8000","9090:9090","9093:9093","3000:3000","8080:80"):
            self.assertIn('"127.0.0.1:'+mapping+'"',compose)
            self.assertNotIn('      - "'+mapping+'"',compose)

    def test_page_renders_both_original_movements_and_walls(self):
        page=(ROOT/"docs/live/work.html").read_text(encoding="utf-8")
        self.assertIn('id="research-movements"',page)
        self.assertIn("Document heading only; not native verification",page)
        self.assertIn("m.evidence===\"structured-source-state\"",page)
        self.assertIn('id="research-walls"',page)
        self.assertIn('id="runs"',page)
        self.assertIn('Array.isArray(json.movements)',page)


if __name__=="__main__":
    unittest.main()
