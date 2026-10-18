"""Signed GitHub log redirects: strip bearer token; retain bounded source."""
from __future__ import annotations

from io import BytesIO
from urllib.request import Request
from zipfile import ZipFile, ZIP_DEFLATED
import unittest

from systems.workspace.github_owner_signed_logs import (
    SignedGitHubLogsRedirect,decode_job_log,fetch_signed_job_log)


class GithubSignedLogTests(unittest.TestCase):
    def test_redirect_to_signed_actions_storage_strips_auth(self):
        req=Request(
            "https://api.github.com/repos/huntingthereferent/autobots-assemble/actions/jobs/117699812720/logs",
            headers={"Authorization":"Bearer test-secret","X-GitHub-Api-Version":"2022-11-28"})
        dest="https://pipelinesghubeus6.actions.githubusercontent.com/signed-log?token=fixture"
        redirected=SignedGitHubLogsRedirect().redirect_request(req,None,302,"Found",{},dest)
        self.assertEqual(redirected.full_url,dest)
        self.assertNotIn("authorization",{x.lower() for x in redirected.headers})
        self.assertNotIn("authorization",{x.lower() for x in redirected.unredirected_hdrs})
        self.assertIn("authorization",{x.lower() for x in req.headers})

    def test_bad_or_insecure_redirect_is_rejected(self):
        req=Request("https://api.github.com/a")
        for target in (
            "https://evil.example/log",
            "http://pipelines.actions.githubusercontent.com/log",
            "https://actions.githubusercontent.com.attacker.example/log",
        ):
            with self.assertRaisesRegex(ValueError,"untrusted"):
                SignedGitHubLogsRedirect().redirect_request(
                    req,None,302,"Found",{},target)

    def test_raw_and_zipped_logs_are_bounded_and_decoded_without_storage(self):
        self.assertEqual(decode_job_log(b'{"game_w13_cp": "WITNESSED"}\n'),
                         '{"game_w13_cp": "WITNESSED"}\n')
        data=BytesIO()
        with ZipFile(data,"w",compression=ZIP_DEFLATED) as z:
            z.writestr("step.txt",'{"child_result_event_id": "evt_fixture"}\n')
        self.assertIn("child_result_event_id",decode_job_log(data.getvalue()))
        for invalid in (b"",b"\xff",b"x"*4_000_001):
            with self.assertRaises(ValueError if invalid!=b"\xff" else UnicodeDecodeError):
                decode_job_log(invalid)

    def test_other_job_identity_must_not_download_log(self):
        with self.assertRaisesRegex(ValueError,"exact original owner job"):
            fetch_signed_job_log(repository="huntingthereferent/autobots-assemble",
                                 job_id=117699812721,token="dummy")


if __name__=="__main__":
    unittest.main()
