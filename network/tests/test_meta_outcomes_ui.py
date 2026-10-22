"""Do not regress Meta's exact daily counts or historical follow-up framing."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
HTML=(ROOT/"docs/live/meta.html").read_text(encoding="utf-8")

class DailyOutcomeUI(unittest.TestCase):
    def test_full_day_summary_is_source_owned_not_last100(self):
        self.assertIn("meta-observations/daily.json",HTML)
        self.assertIn("meta-workstation/daily-runs-v1",HTML)
        self.assertIn("SUCCESSFUL RUNS / TODAY",HTML)
        self.assertIn("HISTORICAL FAILED RUNS",HTML)
        self.assertIn("America/Chicago",HTML)
        self.assertIn('r?.all_sources===true',HTML)
        self.assertIn('renderDaily()',HTML)
        self.assertNotIn("PASSED / TODAY*",HTML)
        self.assertNotIn("NOT PASSED / TODAY*",HTML)

    def test_not_passed_does_not_fold_cancelled_into_failed(self):
        self.assertIn('const isCancelled=r=>',HTML)
        self.assertIn('if(isCancelled(r))return{label:"CANCELLED",cls:"neutral"}',HTML)
        self.assertIn('id="cancelled"',HTML)
        self.assertIn("Failed runs are historical attempts",HTML)
        self.assertIn("not outstanding tests",HTML.lower())
        self.assertIn("Later matching passes",HTML)

    def test_same_workflow_later_pass_is_only_a_scoped_source_link(self):
        self.assertIn("r.workflowId",HTML)
        self.assertIn("r.branch",HTML)
        self.assertIn("r.laterSuccess",HTML)
        self.assertIn("later.href=r.laterSuccess.url",HTML)
        self.assertIn("not proof",HTML.lower())

    def test_red_counter_is_current_health_not_historical_failures(self):
        self.assertIn("CURRENT ISSUES",HTML)
        self.assertIn('id="current-open"',HTML)
        self.assertIn('id="historical-failed"',HTML)
        self.assertIn('meta-observations/health.json',HTML)
        self.assertIn('id="health-list"',HTML)
        self.assertIn('id="inspect-open"',HTML)
        self.assertIn("clears its earlier failed state",HTML)
        self.assertIn('label:"PAST FAILURE",cls:"neutral"',HTML)
        self.assertIn('label:"LATER PASS",cls:"good"',HTML)
        self.assertNotIn('id="followup-count"',HTML)
        self.assertNotIn('label:r.conclusion?.toUpperCase()||"FAILED",cls:"bad"',HTML)

if __name__=="__main__":
    unittest.main()
