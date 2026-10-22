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
        counts={"success":225, "failure":30, "cancelled":84,
                "skipped":5, "timed_out":0, "action_required":0}
        def get(path):
            called.append(path)
            self.assertIn("per_page=1",path)
            self.assertIn("created=",path)
            status=path.partition("&status=")[2]
            return {"total_count":counts[status]}
        result=collect({"A":"owner-a/repo-a","B":"owner-b/repo-b"},
                      dt.datetime(2026,10,22,17,tzinfo=UTC),getter=get)
        self.assertTrue(result["all_sources"])
        self.assertEqual(result["totals"]["success"],450)
        self.assertEqual(result["totals"]["failure"],60)
        self.assertEqual(result["totals"]["cancelled"],168)
        self.assertEqual(result["totals"]["known_outcome_runs_lower_bound"],688)
        self.assertEqual(len(called),2*len(CONCLUSIONS))
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

    def test_high_volume_queries_split_before_github_count_cap(self):
        from systems.workspace.meta_daily import github_count
        from urllib.parse import unquote
        calls=[]
        def get(path):
            calls.append(path)
            created=unquote(path.split("created=")[1].split("&")[0])
            start,end=created.split("..")
            span=(dt.datetime.fromisoformat(end.replace("Z","+00:00"))-
                  dt.datetime.fromisoformat(start.replace("Z","+00:00"))).total_seconds()
            return {"total_count":1200 if span>100000 else 600}
        count=github_count("a/b","2026-10-22T05:00:00Z..2026-10-23T04:59:59Z",
                           status="success",getter=get,split_threshold=1000)
        self.assertEqual(count,1200)
        self.assertEqual(len(calls),3)

    def test_noninteger_count_not_silently_accepted(self):
        result=collect({"A":"a/b","B":"c/d"},
                      dt.datetime(2026,10,22,17,tzinfo=UTC),
                      getter=lambda path:{"total_count":"67"})
        self.assertIsNone(result["totals"])


if __name__ == "__main__":
    unittest.main()
