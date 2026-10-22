"""Checks for complete daily GitHub run counters and honest outcomes."""
import datetime as dt
import unittest
from systems.workspace.meta_daily import collect, day_window, CONCLUSIONS

UTC = dt.timezone.utc


class DailySourceTests(unittest.TestCase):
    def test_dst_boundary_is_local_day_not_utc_midnight(self):
        day,start,end = day_window(dt.datetime(2026,10,22,17,0,tzinfo=UTC))
        self.assertEqual(day, "2026-10-22")
        self.assertEqual(start, "2026-10-22T05:00:00Z")
        self.assertEqual(end, "2026-10-23T04:59:59Z")

    def test_gets_source_total_counts_not_100_run_page(self):
        called=[]
        counts={"success":2257, "failure":300, "cancelled":845,
                "skipped":53, "timed_out":0, "action_required":0}
        def get(path):
            called.append(path)
            self.assertIn("per_page=1",path)
            self.assertIn("created=",path)
            status=path.partition("&status=")[2]
            return {"total_count":counts.get(status,3500)}
        result=collect({"A":"owner-a/repo-a","B":"owner-b/repo-b"},
                      dt.datetime(2026,10,22,17,tzinfo=UTC),getter=get)
        self.assertTrue(result["all_sources"])
        self.assertEqual(result["totals"]["success"],4514)
        self.assertEqual(result["totals"]["failure"],600)
        self.assertEqual(result["totals"]["cancelled"],1690)
        self.assertEqual(result["totals"]["created"],7000)
        self.assertEqual(len(called),2*(1+len(CONCLUSIONS)))
        self.assertEqual(result["basis"].startswith("GitHub Actions workflow runs"),True)
        self.assertIn("NOT unresolved",result["limitations"])

    def test_missing_second_repo_never_claims_zero(self):
        def get(path):
            if "owner-b" in path:
                raise ValueError("Missing scope")
            return {"total_count":0}
        result=collect({"A":"owner-a/repo-a","B":"owner-b/repo-b"},
                      dt.datetime(2026,10,22,17,tzinfo=UTC),getter=get)
        self.assertFalse(result["all_sources"])
        self.assertIsNone(result["totals"])
        self.assertFalse(result["nodes"]["B"]["observed"])

    def test_inconsistent_source_counts_not_reported(self):
        def get(path):
            return {"total_count":3 if "&status=" in path else 1}
        result=collect({"A":"a/b","B":"c/d"},
                      dt.datetime(2026,10,22,17,tzinfo=UTC),getter=get)
        self.assertFalse(result["all_sources"])
        self.assertIsNone(result["totals"])

    def test_noninteger_count_not_silently_accepted(self):
        result=collect({"A":"a/b","B":"c/d"},
                      dt.datetime(2026,10,22,17,tzinfo=UTC),
                      getter=lambda path:{"total_count":"67"})
        self.assertIsNone(result["totals"])


if __name__ == "__main__":
    unittest.main()
