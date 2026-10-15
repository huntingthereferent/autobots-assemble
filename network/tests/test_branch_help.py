"""Unfinished parent can request a helper without inventing a new capability."""
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.branch_help import (open_help, staff_finite, verify_return,
                                           help_summary, CAP_FINITE, CAP_GAME)
from systems.workspace.coordinator_window import CoordinatorIndex
from systems.workspace.cp_motion import admit_research, one_cp_handoff
from systems.workspace.workstation import ProcessWorkstation
from systems.workspace.controls import run_job
from systems.workspace.process_handoff import WORKER_ID

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'work'/'arc_like_maze'/'chatbot'
INPUTS={"old_phi":[0,0,1], "new_phi":[0,0,0],
        "candidate_words":[["ABAA","ABBABA"],["ABAA","AAABB","BAAAB"]],
        "required_state":[0,0,0],"required_action":"B"}

class BranchHelpTests(unittest.TestCase):
    def setUp(self):
        t=TemporaryDirectory();self.addCleanup(t.cleanup)
        self.root=Path(t.name);self.data=self.root/'private'
        self.index=CoordinatorIndex(self.data/'coordinator-windows.jsonl')
        self.assertEqual(admit_research(self.index),13)
        self.source=self.root/'selected-source';self.source.mkdir()
        for f in ('finite_goal_priority.py','finite_required_edge_guard.py'):
            shutil.copyfile(SOURCE/f,self.source/f)
        self.desk=ProcessWorkstation(self.data/'workstation')
        self.desk.copy_source(self.source,worker_id=WORKER_ID,version_id='base')
        self.inputs=self.root/'finite.json';self.inputs.write_text(json.dumps(INPUTS))
    def runtime(self):
        return HandoffRuntime(event_store=RuntimeJournal(self.data/'runtime.jsonl'))
    def open(self, cap=CAP_FINITE, key='need-a-prefilter'):
        return open_help(data_dir=self.data,lane='game',slot='cp-game-w13-worlds',
                         capability=cap,opening_key=key,reason='Source-specific audit assistance')
    def staff(self,oid):
        return staff_finite(data_dir=self.data,opening_id=oid,
                            parent_version='base',inputs_file=self.inputs)
    def test_unfinished_game_cp_can_open_help_and_does_not_claim_game_worker(self):
        row=self.open(CAP_GAME)
        self.assertEqual(row['state'],'OPEN_UNSTAFFED')
        self.assertFalse(row['registered_capability'])
        self.assertEqual(self.runtime().state(row['opening_id']).status,'READY')
        self.assertFalse(row['parent_cp_witnessed'])
        with self.assertRaisesRegex(ValueError,'no source-owned adapter'):
            self.staff(row['opening_id'])
        self.assertFalse(any((self.data/'runtime.jsonl').read_text().count(x) for x in ('HELP_ASSIGNED','HELP_RETURNED')))
    def test_real_helper_branch_and_native_worker_return(self):
        row=self.open();oid=row['opening_id']
        staffed=self.staff(oid)
        self.assertEqual(staffed['state'],'ASSIGNED_NOT_VERIFIED')
        self.assertTrue(staffed['registered_capability'])
        self.assertFalse(staffed['parent_cp_witnessed'])
        job=staffed['child']['job_id']; child=staffed['child']['version_id']
        self.assertEqual(self.desk._read(WORKER_ID,child)[1]['parent_version'],'base')
        self.assertEqual(self.runtime().state(job).status,'READY')
        with self.assertRaisesRegex(ValueError,'native completion'):
            verify_return(data_dir=self.data,opening_id=oid)
        self.assertEqual(run_job(data_dir=self.data,job_id=job,confirm_execute=job)['status'],'COMPLETE')
        returned=verify_return(data_dir=self.data,opening_id=oid)
        self.assertEqual(returned['state'],'RETURN_RECORDED_REVERIFY_BEFORE_USE')
        self.assertFalse(returned['parent_cp_witnessed'])
        self.assertEqual([x.event_type for x in self.runtime().event_store.for_handoff(oid)],
                         ['CREATED','HELP_ASSIGNED','HELP_RETURNED'])
        self.assertEqual(help_summary(self.data)[0]['opening_id'],oid)
        # A finite-predicate helper is NOT a game-native witness.
        packet=one_cp_handoff(self.index,'complete-stack',{'jobs':[]})
        self.assertNotIn('GAME-W13-WORLDS',packet['cp_automation']['witnessed'])
    def test_restarts_and_repeated_calls_never_birth_duplicate_helpers(self):
        first=self.open();oid=first['opening_id']
        self.assertEqual(first,self.open())
        child=self.staff(oid)
        self.assertEqual(child,self.staff(oid))
        self.assertEqual(len([h for h in self.runtime()._handoffs if h.startswith('help-job-')]),1)
        job=child['child']['job_id']
        run_job(data_dir=self.data,job_id=job,confirm_execute=job)
        verify_return(data_dir=self.data,opening_id=oid)
        before=(self.data/'runtime.jsonl').read_bytes()
        verify_return(data_dir=self.data,opening_id=oid)
        self.assertEqual(before,(self.data/'runtime.jsonl').read_bytes())
    def test_collision_or_different_request_refused(self):
        self.open()
        with self.assertRaisesRegex(ValueError,'different request'):
            open_help(data_dir=self.data,lane='game',slot='cp-game-w13-worlds',
                      capability=CAP_FINITE,opening_key='need-a-prefilter',
                      reason='Changed after original open')
        with self.assertRaisesRegex(ValueError,'existing exact checkpoint'):
            open_help(data_dir=self.data,lane='game',slot='does-not-exist',
                      capability=CAP_FINITE,opening_key='x',reason='Missing')
    def test_changed_helper_source_blocks_native_return(self):
        oid=self.open()['opening_id'];child=self.staff(oid)['child'];job=child['job_id']
        run_job(data_dir=self.data,job_id=job,confirm_execute=job)
        edition=self.desk._edition(WORKER_ID,child['version_id'])
        p=edition/'finite_goal_priority.py'
        p.write_text(p.read_text()+'\n# mutated\n')
        with self.assertRaisesRegex(ValueError,'source or native completion'):
            verify_return(data_dir=self.data,opening_id=oid)
    def test_wrong_worker_source_cannot_open_from_unsafe_id(self):
        with self.assertRaises(ValueError):
            open_help(data_dir=self.data,lane='game',slot='cp-game-w13-worlds',
                      capability=CAP_FINITE,opening_key='../oops',reason='Unsafe')
        self.assertFalse((self.data/'runtime.jsonl').exists())
    def test_no_help_job_executed_by_open_or_staff(self):
        oid=self.open()['opening_id']
        self.staff(oid)
        self.assertNotIn('STARTED',(self.data/'runtime.jsonl').read_text())
        self.assertNotIn('RESULT',(self.data/'runtime.jsonl').read_text())

if __name__=='__main__':unittest.main()