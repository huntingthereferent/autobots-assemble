"""W12-preserving W13 multi-world worker, native replay and CP non-promotion."""
from __future__ import annotations
import copy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from runtime.handoff import EvidenceRecord,ExecutionResult
from systems.workspace.workstation import ProcessWorkstation
from systems.workspace.game_w12_reference import (GameSpec, run_actions, verify_trace,
                                                     verify_expanded_browser_receipt)
from systems.workspace.game_w13_native import (validate_request, expected_report, canonical,
                                                check_preserved_reference,CP_ID,VERIFIER)
from systems.workspace.game_w13_bridge import (GameW13Bridge,WORKER_ID,
                                                copy_game_source,run_source,WITNESS,SOURCE)
from systems.workspace.controls import run_job,reverify_job
from systems.workspace.coordinator_window import (CoordinatorIndex,from_existing_workstation,
                                                  freshly_reverify_linked_jobs)
from systems.workspace.cp_motion import (admit_research,attach_native_cp_contracts,
                                         one_cp_handoff)

ROOT=Path(__file__).resolve().parents[2]
DATA=json.loads((ROOT/'network/tests/fixtures/game_w13_example.json').read_text(encoding='utf8'))

class GameW13NativeTests(unittest.TestCase):
    def test_original_w12_reference_byte_identical(self):
        self.assertTrue(check_preserved_reference())
        first=run_actions(['right','interact'])
        self.assertTrue(verify_trace(first)['valid'])
        self.assertTrue(first['solved'])

    def test_original_expanded_receipt_still_verified_exactly(self):
        trace=run_actions(['right','interact'])
        data={'version':trace['version'],'spec':trace['spec'],
              'actions':['right','interact'],'observations':[
                 {k:v[k] for k in ('action','before','after','verdict')}
                 for v in trace['steps']], 'final':trace['final']}
        self.assertTrue(verify_expanded_browser_receipt(data)['valid'])
        fake=copy.deepcopy(data);fake['observations'][0]['before']['turns']=9
        with self.assertRaises(ValueError):verify_expanded_browser_receipt(fake)
        with self.assertRaises(ValueError):
            from systems.workspace.game_w12_reference import verify_browser_receipt
            verify_browser_receipt(data)

    def test_native_multi_world_replay_agrees_with_pinned_source(self):
        validated=validate_request(DATA)
        expected=expected_report(validated)
        self.assertEqual(expected['worlds_completed'],2)
        self.assertTrue(expected['solved'])
        from systems.workspace.game_w13_bridge import SOURCE_DIRECTORY
        observed=run_source(SOURCE_DIRECTORY,validated)
        self.assertEqual(canonical(observed['report']),canonical(expected))
        self.assertEqual(expected['worlds'][0]['trace']['final']['turns'],2)

    def test_explicit_advance_requires_completed_previous_world(self):
        bad={**DATA,'actions':['advance','right','interact']}
        with self.assertRaisesRegex(ValueError,'advance'):
            expected_report(bad)
        other={**DATA,'actions':['right','interact','advance','right']}
        with self.assertRaisesRegex(ValueError,'unsolved'):
            expected_report(other)

    def test_reject_unknown_actions_floats_and_duplicate_worlds(self):
        for bad in [
            {**DATA,'actions':['right','interact','teleport','right','interact']},
            {**DATA,'worlds':[DATA['worlds'][0],DATA['worlds'][0]]},
            {**DATA,'worlds':[{**DATA['worlds'][0],'spec':{**DATA['worlds'][0]['spec'],'width':4.0}},DATA['worlds'][1]]},
            {**DATA,'worlds':[DATA['worlds'][0],{**DATA['worlds'][1],'spec':DATA['worlds'][0]['spec']}]},
        ]:
            with self.subTest(bad=str(bad)[:80]),self.assertRaises((ValueError,TypeError)):
                validate_request(bad)

class GameW13WorkstationTests(unittest.TestCase):
    def setUp(self):
        tmp=TemporaryDirectory();self.addCleanup(tmp.cleanup)
        self.data=Path(tmp.name)/'private';self.data.mkdir()
        self.desk=ProcessWorkstation(self.data/'workstation')
        self.runtime=HandoffRuntime(event_store=RuntimeJournal(self.data/'runtime.jsonl'))
        self.bridge=GameW13Bridge(runtime=self.runtime,workstation=self.desk)
        self.index=CoordinatorIndex(self.data/'coordinator-windows.jsonl')
        admit_research(self.index)
        copy_game_source(self.data,version_id='w13-v1',allow_copy=True)

    def admit(self):
        return self.bridge.admit(version_id='w13-v1',inputs=DATA,from_actor='world-build',job_id='game-w13-job')

    def bind(self):
        self.index.bind_planned('complete-stack','game',slot='cp-game-w13-worlds',
                                job_id='game-w13-job',worker_id=WORKER_ID,version_id='w13-v1')

    def test_copy_does_not_execute_or_admit(self):
        self.assertFalse((self.data/'runtime.jsonl').exists())

    def test_exact_admission_execute_and_reverify(self):
        self.admit()
        self.assertEqual(self.runtime.state('game-w13-job').status,'READY')
        with self.assertRaises(PermissionError):self.bridge.execute('game-w13-job')
        with self.assertRaises(PermissionError):run_job(data_dir=self.data,job_id='game-w13-job',confirm_execute='wrong')
        state=run_job(data_dir=self.data,job_id='game-w13-job',confirm_execute='game-w13-job')
        self.assertEqual(state['status'],'COMPLETE')
        self.assertTrue(reverify_job(data_dir=self.data,job_id='game-w13-job')['reverified'])
        before=(self.data/'runtime.jsonl').read_bytes()
        run_job(data_dir=self.data,job_id='game-w13-job',confirm_execute='game-w13-job')
        self.assertEqual(before,(self.data/'runtime.jsonl').read_bytes())

    def test_candidate_build_does_not_close_full_w13_checkpoint(self):
        self.admit();self.bind()
        run_job(data_dir=self.data,job_id='game-w13-job',confirm_execute='game-w13-job')
        restored=HandoffRuntime(event_store=RuntimeJournal(self.data/'runtime.jsonl'))
        view=attach_native_cp_contracts(from_existing_workstation(self.data),restored._handoffs.values())
        fresh=freshly_reverify_linked_jobs(self.index,'complete-stack',view,
                 lambda j: reverify_job(data_dir=self.data,job_id=j))
        cp=one_cp_handoff(self.index,'complete-stack',fresh)['cp_automation']
        self.assertNotIn(CP_ID,cp['witnessed'])
        self.assertIn(CP_ID,cp['frontier'])
        self.assertNotIn('GAME-NATIVE-VERIFIER',cp['frontier'])

    def test_worker_cannot_self_certify_W13_complete(self):
        h=self.admit()
        from systems.workspace.game_w13_native import expected_report
        false=ExecutionResult('COMPLETE',output={
          'kind':'game-w13-multiworld-build/v1','checkpoint_contract':CP_ID,
          'checkpoint_verdict':'PASS','checkpoint_worker_role':'game-build',
          'native_verifier':VERIFIER,'report':expected_report(DATA),
          'worker_version':'w13-v1','edition_fingerprint':h.metadata['edition_fingerprint'],
          'child_pid':42},evidence=(EvidenceRecord(condition=WITNESS,kind='computation',source=SOURCE,
                          ref=h.metadata['edition_fingerprint'],depth='native-W12-replay'),))
        with self.assertRaises(ValueError):self.runtime.return_result(h.handoff_id,actor_id=h.to_actor,result=false)
        self.assertEqual(self.runtime.state(h.handoff_id).status,'READY')

    def test_forged_trace_rejected_by_original_w12_replay(self):
        h=self.admit();report=expected_report(DATA)
        report['worlds'][1]['trace']['steps'][-1]['after']['turns']=300
        fake=ExecutionResult('COMPLETE',output={
          'kind':'game-w13-multiworld-build/v1','checkpoint_contract':CP_ID,
          'checkpoint_verdict':'CANDIDATE','checkpoint_worker_role':'game-build',
          'native_verifier':VERIFIER,'report':report,
          'worker_version':'w13-v1','edition_fingerprint':h.metadata['edition_fingerprint'],
          'child_pid':42},evidence=(EvidenceRecord(condition=WITNESS,kind='computation',source=SOURCE,
                         ref=h.metadata['edition_fingerprint'],depth='native-W12-replay'),))
        with self.assertRaisesRegex(ValueError,'native verifier rejects'):
            self.runtime.return_result(h.handoff_id,actor_id=h.to_actor,result=fake)
        self.assertEqual(self.runtime.state(h.handoff_id).status,'READY')

    def test_preserved_W12_copy_edit_blocks_job_before_execution(self):
        self.admit()
        file=self.data/'workstation'/WORKER_ID/'w13-v1'/'game_w12_reference.py'
        file.write_bytes(file.read_bytes()+b'\n# changed\n')
        with self.assertRaises(ValueError):self.bridge.execute('game-w13-job',allow_local_execution=True)
        self.assertEqual(self.runtime.state('game-w13-job').status,'READY')

    def test_restart_recovery_reverify(self):
        self.admit()
        run_job(data_dir=self.data,job_id='game-w13-job',confirm_execute='game-w13-job')
        recovered=HandoffRuntime(event_store=RuntimeJournal(self.data/'runtime.jsonl'))
        GameW13Bridge(runtime=recovered,workstation=self.desk).reverify('game-w13-job')
        self.assertEqual(recovered.state('game-w13-job').status,'COMPLETE')

if __name__=='__main__':unittest.main()

class GameW13BranchHelpTests(unittest.TestCase):
    def setUp(self):
        td=TemporaryDirectory();self.addCleanup(td.cleanup)
        self.data=Path(td.name)/'private';self.data.mkdir()
        idx=CoordinatorIndex(self.data/'coordinator-windows.jsonl');admit_research(idx)
        copy_game_source(self.data,version_id='base-game',allow_copy=True)
        self.inputs=Path(td.name)/'input.json';self.inputs.write_text(json.dumps(DATA))

    def test_game_w13_composition_helper_branches_but_cannot_close_parent(self):
        from systems.workspace.branch_help import open_and_staff_known,verify_return,CAP_W13
        result=open_and_staff_known(data_dir=self.data,lane='game',slot='cp-game-w13-worlds',
                                   capability=CAP_W13,opening_key='level-composition',
                                   reason='Need a two-world replayable composition',
                                   parent_version='base-game',inputs_file=self.inputs,
                                   allow_native_admission=True)
        self.assertEqual(result['state'],'ASSIGNED_NOT_VERIFIED')
        child=result['child'];self.assertEqual(child['worker_id'],WORKER_ID)
        self.assertNotEqual(child['version_id'],'base-game')
        rt=HandoffRuntime(event_store=RuntimeJournal(self.data/'runtime.jsonl'))
        self.assertEqual(rt.state(child['job_id']).status,'READY')
        duplicate=open_and_staff_known(data_dir=self.data,lane='game',slot='cp-game-w13-worlds',
                                   capability=CAP_W13,opening_key='level-composition',
                                   reason='Need a two-world replayable composition',
                                   parent_version='base-game',inputs_file=self.inputs,
                                   allow_native_admission=True)
        self.assertEqual(result['child'],duplicate['child'])
        run_job(data_dir=self.data,job_id=child['job_id'],confirm_execute=child['job_id'])
        returned=verify_return(data_dir=self.data,opening_id=result['opening_id'])
        self.assertEqual(returned['state'],'RETURN_RECORDED_REVERIFY_BEFORE_USE')
        self.assertFalse(returned['parent_cp_witnessed'])

    def test_general_game_engine_build_stays_unstaffed(self):
        from systems.workspace.branch_help import open_and_staff_known,CAP_GAME
        result=open_and_staff_known(data_dir=self.data,lane='game',slot='cp-game-w13-worlds',
                                   capability=CAP_GAME,opening_key='whole-engine-agent',
                                   reason='Need autonomous model-backed game coding',
                                   parent_version='base-game',inputs_file=self.inputs,
                                   allow_native_admission=True)
        self.assertEqual(result['state'],'OPEN_UNSTAFFED')
        self.assertIsNone(result['child'])