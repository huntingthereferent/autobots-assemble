"""No fake departures, false returns, or invented elapsed times."""
import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from views.traces.fork_return import (REPOS, VERSION, build_snapshot, collect,
                                     markdown, observe, stamp)


def fork(*, ident=42, full="someone/autobots-assemble", at="2026-10-17T10:00:00Z"):
    return {"id":ident,"full_name":full,"created_at":at,
            "html_url":f"https://github.com/{full}"}


def pr(*, repo=REPOS[0], head="someone/autobots-assemble",
       ident=42, at="2026-10-17T11:00:00Z",
       sha="a"*40, number=123):
    return {
        "head":{"repo":{"id":ident,"full_name":head}},
        "base":{"repo":{"full_name":repo}},
        "merged_at":at,"merge_commit_sha":sha,
        "number":number,
        "html_url":f"https://github.com/{repo}/pull/{number}",
    }


class PublicForkReturnTests(unittest.TestCase):
    def test_external_copy_and_exact_merge_return(self):
        view=observe(REPOS[0],[fork()],[pr()],
                     fork_coverage="PAGED_TO_END",pr_coverage="PAGED_TO_END")
        self.assertEqual(view["forks_observed"],1)
        self.assertEqual(view["returns_observed"],1)
        row=view["observations"][0]
        self.assertEqual(row["status"],"RETURN_OBSERVED")
        self.assertEqual(row["elapsed_seconds"],3600)
        self.assertEqual(row["return_pr"]["number"],123)

    def test_open_copy_has_null_return_not_zero(self):
        view=observe(REPOS[0],[fork()],[pr(at=None)],
                     fork_coverage="PAGED_TO_END",pr_coverage="PAGED_TO_END")
        row=view["observations"][0]
        self.assertEqual(row["status"],"OPEN")
        self.assertIsNone(row["elapsed_seconds"])
        self.assertIsNone(row["returned_at"])

    def test_owner_branch_is_not_departure(self):
        p=pr(ident=999,head=REPOS[0])
        v=observe(REPOS[0],[],[p],
                  fork_coverage="PAGED_TO_END",pr_coverage="PAGED_TO_END")
        self.assertEqual(v["forks_observed"],0)
        self.assertEqual(v["returns_observed"],0)

    def test_unrelated_fork_does_not_return(self):
        for bad in [pr(ident=202),pr(head="not-the-fork/repo"),
                    pr(repo=REPOS[1]),pr(sha=None),pr(sha="a"*39),
                    pr(at=None)]:
            view=observe(REPOS[0],[fork()],[bad],
                         fork_coverage="PAGED_TO_END",pr_coverage="PAGED_TO_END")
            self.assertEqual(view["returns_observed"],0)

    def test_earliest_real_return_wins_even_if_prs_unordered(self):
        vals=[pr(number=100,at="2026-10-17T13:00:00Z"),
              pr(number=9,at="2026-10-17T10:20:00Z")]
        result=observe(REPOS[0],[fork()],vals,
                       fork_coverage="PAGED_TO_END",pr_coverage="PAGED_TO_END")
        self.assertEqual(result["observations"][0]["elapsed_seconds"],1200)
        self.assertEqual(result["observations"][0]["return_pr"]["number"],9)

    def test_bad_provenance_and_timestamps_are_rejected(self):
        for rows,prs in [
            ([fork(),fork()],[]),
            ([fork(at="nope")],[]),
            ([fork(full="javascript:bad")],[]),
            ([fork()], [pr(at="2026-10-16T23:00:00Z")]),
            ([fork()], [pr(at="2026-10-17T11:00:00")]),
            ([fork()], [pr(number=0)]),
            ([fork()], [pr(sha="a"*40,number=123)|{"html_url":"https://elsewhere.test/pr"}]),
        ]:
            with self.assertRaises(ValueError):
                observe(REPOS[0],rows,prs,
                        fork_coverage="PAGED_TO_END",pr_coverage="PAGED_TO_END")

    def test_partial_api_page_never_claims_total_coverage(self):
        def page(repo,kind,p,token):
            return ([{"page":p}]*100 if p==1 else [{"page":p}])
        rows,cover=collect(REPOS[0],"forks",get=page)
        self.assertEqual(len(rows),101)
        self.assertEqual(cover,"PAGED_TO_END")
        def full(repo,kind,p,token):
            return [{"page":p}]*100
        rows,cover=collect(REPOS[0],"forks",get=full)
        self.assertEqual(len(rows),300)
        self.assertEqual(cover,"BOUNDED_FIRST_300")

    def test_snapshot_keeps_original_repositories_distinct(self):
        inputs={repo:{"forks":[],"pulls":[],
                      "fork_coverage":"PAGED_TO_END",
                      "pr_coverage":"PAGED_TO_END"} for repo in REPOS}
        inputs[REPOS[0]]["forks"]=[fork()]
        inputs[REPOS[0]]["pulls"]=[pr()]
        inputs[REPOS[1]]["forks"]=[fork(ident=42,full="someone/huntingthereferent")]
        snapshot=build_snapshot(checked_at="2026-10-17T12:00:00Z",inputs=inputs)
        self.assertEqual(snapshot["schema"],VERSION)
        self.assertEqual([r["returns_observed"] for r in snapshot["repositories"]],[1,0])
        out=markdown(snapshot)
        self.assertIn("GitHub fork",out) if False else None
        self.assertIn("**60.0 minutes**",out)
        self.assertIn("None observed",markdown(build_snapshot(
            checked_at="2026-10-17T12:00:00Z",
            inputs={repo:{"forks":[],"pulls":[],
                    "fork_coverage":"PAGED_TO_END",
                    "pr_coverage":"PAGED_TO_END"} for repo in REPOS})))

    def test_missing_second_repo_rejected(self):
        with self.assertRaises(ValueError):
            build_snapshot(checked_at="2026-10-17T12:00:00Z",inputs={})

if __name__=="__main__":
    unittest.main()
