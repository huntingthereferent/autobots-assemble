"""GitHub owner-merged one-shot native game request boundary tests.

These tests inspect intent; only a successful actual GitHub-hosted native run
can witness the checkpoint.
"""
from __future__ import annotations

from pathlib import Path
import json
import subprocess
import textwrap
import unittest

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / '.github/workflows/workstation-w13-owner-merged-one-shot.yml'
REQUEST = ROOT / 'systems/workspace/native_job_requests/w13/game-w13-github-001.json'


class W13OwnerMergedOneShotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=WORKFLOW.read_text(encoding='utf8')
        cls.request=json.loads(REQUEST.read_text(encoding='utf8'))

    def test_01_owner_protected_main_push_only(self):
        s=self.source
        self.assertIn('on:\n  push:\n    branches: [main]',s)
        self.assertIn("'systems/workspace/native_job_requests/w13/game-w13-github-001.json'",s)
        self.assertNotIn('  pull_request:',s)
        self.assertNotIn('  workflow_dispatch:',s)
        for v in ("github.event_name == 'push'",
                  "github.ref == 'refs/heads/main'",
                  "github.actor == github.repository_owner",
                  'persist-credentials: false',
                  'permissions:\n  contents: read',
                  'cancel-in-progress: false'):
            with self.subTest(v=v): self.assertIn(v,s)

    def test_02_exact_additive_single_record_and_pinned_unchanged_source(self):
        record=self.request
        self.assertEqual(record,{
            'contract':'game-w13-owner-merged-one-shot-v1',
            'checkpoint':'GAME-W13-WORLDS',
            'job_id':'game-w13-github-001',
            'worker_id':'game-worlds-w13',
            'source_version':'w13-github-v1',
            'worker_git_blob':'54d847dadda9b5fd10297e2e88ee65bea9be2ad1',
            'fixture_git_blob':'645819b70f022feee7b54e764f3d438c8e45f4c1',
            'authorizes_copy':True,'authorizes_admit':True,'authorizes_execute':True,
            'execution_scope':'one-finite-original-WORLD-W13-two-room-job',
            'activation':'one-new-file-in-protected-main-owner-merge'
        })
        for rel,sha in (
            ('systems/workspace/game_w13_worker_source/game_worlds_worker.py',record['worker_git_blob']),
            ('network/tests/fixtures/game_w13_native_cp_example.json',record['fixture_git_blob'])
        ):
            actual=subprocess.check_output(['git','hash-object',str(ROOT/rel)],text=True).strip()
            self.assertEqual(actual,sha)
        for condition in (
            "if len(parents) != 3:",
            "if changes != 'A\\t'+request_path.as_posix():",
            "json.loads(request_path.read_text(encoding='utf8')) != expected",
            "'git','hash-object',path",
            "'git','rev-list','--parents'",
        ):
            self.assertIn(condition,self.source)

    def test_03_existing_native_CP_used_without_bypass(self):
        s=self.source
        for marker in (
            'admit-research','game_w13_native_cli','--confirm-copy',
            'prepare --version','--confirm-admit','--from-actor',
            'bind-job','cp-game-w13-worlds','run-linked',
            '--confirm-execute','reverify --job-id','handoff --reverify',
            "states.get('GAME-W13-WORLDS')!='WITNESSED'",
            "states.get('GAME-NATIVE-VERIFIER')!='ADMISSIBLE'",
            'native-runtime.tar.gz','native-runtime.sha256',
            'authorization.json','actions/upload-artifact@v4',
            'retention-days: 30',
        ):
            with self.subTest(marker=marker): self.assertIn(marker,s)

    def test_04_shell_blocks_parse_with_bash(self):
        scripts=[]
        lines=self.source.splitlines()
        i=0
        while i<len(lines):
            line=lines[i]
            if line=='        run: |':
                i+=1
                block=[]
                while i<len(lines) and (not lines[i].strip() or lines[i].startswith('          ')):
                    block.append(lines[i]);i+=1
                scripts.append(textwrap.dedent('\n'.join(block)))
                continue
            if line.startswith('        run: '):
                scripts.append(line.split('run: ',1)[1])
            i+=1
        self.assertEqual(len(scripts),7)
        for script in scripts:
            p=subprocess.run(['bash','-n'],input=script,text=True,capture_output=True)
            self.assertEqual(p.returncode,0,p.stderr)


if __name__=='__main__':
    unittest.main()
