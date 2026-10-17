"""Static guardrails for the GitHub-hosted native W13 dispatch workflow.

These do not dispatch or claim to witness a job; the real runner must do so.
"""
from __future__ import annotations

from pathlib import Path
import re
import subprocess
import textwrap
import unittest

WORKFLOW = (
    Path(__file__).resolve().parents[2] /
    ".github/workflows/workstation-w13-github-native-admission.yml"
)


class GameW13GithubHostedWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = WORKFLOW.read_text(encoding="utf8")

    def test_01_dispatch_only_owner_main_explicit_execution(self):
        s = self.source
        self.assertRegex(s, r"(?m)^on:\s*\n  workflow_dispatch:")
        self.assertNotRegex(s, r"(?m)^  (?:push|pull_request|schedule|workflow_run):")
        for marker in (
            "github.ref == 'refs/heads/main'",
            "github.actor == github.repository_owner",
            "inputs.execute == true",
            "default: false",
            "persist-credentials: false",
            "cancel-in-progress: false",
            "permissions:\n  contents: read",
        ):
            self.assertIn(marker, s)

    def test_02_native_exact_job_and_fresh_CP_verifier(self):
        s = self.source
        for marker in (
            "confirm_job_id:", "execute:", "if confirm != job:",
            "re.fullmatch", "GITHUB_REF", "GITHUB_ACTOR",
            "GITHUB_REPOSITORY_OWNER", "--confirm-copy",
            "admit-research", "game_w13_native_cli", "prepare --version",
            "--confirm-admit", "--from-actor", "bind-job",
            "cp-game-w13-worlds", "run-linked", "--confirm-execute",
            "reverify --job-id", "handoff --reverify",
            "states.get('GAME-W13-WORLDS') != 'WITNESSED'",
            "states.get('GAME-NATIVE-VERIFIER') != 'ADMISSIBLE'",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, s)

    def test_03_ephemeral_runtime_evidence_archive(self):
        s = self.source
        for marker in (
            "RUNNER_TEMP/w13-private-runtime", "RUNNER_TEMP/w13-evidence",
            "GITHUB_ENV", "native-runtime.tar.gz",
            "native-runtime.sha256", "source_worker_sha256",
            "fixture_sha256", "GITHUB_RUN_ATTEMPT",
            "actions/upload-artifact@v4", "retention-days: 30",
            "if-no-files-found: error",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, s)
        self.assertNotIn("${{ runner.temp }}", s.split("    steps:", 1)[0])

    def test_04_all_shell_blocks_parse(self):
        lines = self.source.splitlines()
        scripts = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if line == "        run: |":
                i += 1
                block = []
                while i < len(lines) and (not lines[i].strip() or lines[i].startswith("          ")):
                    block.append(lines[i])
                    i += 1
                scripts.append(textwrap.dedent("\n".join(block)))
                continue
            if line.startswith("        run: "):
                scripts.append(line.split("run: ", 1)[1])
            i += 1
        self.assertEqual(len(scripts), 7)
        for index, script in enumerate(scripts):
            with self.subTest(script=index):
                checked = subprocess.run(
                    ["bash", "-n"], input=script,
                    text=True, capture_output=True, check=False
                )
                self.assertEqual(checked.returncode, 0, checked.stderr)


if __name__ == "__main__":
    unittest.main()
