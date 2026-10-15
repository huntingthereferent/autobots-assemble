"""Scope native validation, independent output and complete workstation handoff."""
import copy
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT=Path(__file__).resolve().parents[2]
from systems.workspace.nih_scope_native import validate_scope,expected_scope_report,CP_ID,VERIFIER
from systems.workspace.nih_scope_bridge import NIHScopeBridge,WORKER_ID,copy_scope_source,run_source
from systems.workspace.workstation import ProcessWorkstation
from systems.workspace.coordinator_window import CoordinatorIndex
from systems.workspace.cp_motion import admit_research, one_cp_handoff,attach_native_cp_contracts
from systems.workspace.coordinator_window import from_existing_workstation,freshly_reverify_linked_jobs
from systems.workspace.controls import run_job,reverify_job
from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from runtime.handoff import ExecutionResult

SCOPE=json.loads((ROOT/'network/tests/fixtures/nih_scope_example.json').read_text())


class NIHScopeNativeTests(unittest.TestCase):
    def test_expected_as_known_at(self):
        report=expected_scope_report(SCOPE)
        self.assertEqual(report['visible_ids'],['prior-note'])
        self.assertEqual(report['withheld_future_ids'],['delayed-result'])
        self.assertEqual(report['clinical_verdict'],'NOT_EVALUATED')

    def test_reject_actual_private_or_unchecked_record(self):
        for mutation in ({'synthetic':False},{'patient_name':'Jane'}, {'kind':'medical-record'},
                         {'query_at':'2026-02-29'},{'application':'other'}):
            with self.subTest(mutation=mutation):
                with self.assertRaises((ValueError,TypeError)):
                    validate_scope({**SCOPE,**mutation})

    def test_reject_future_data_forged_visible(self):
        value=copy.deepcopy(SCOPE)
        value['observations'][1]['known_at']='2026-01-04'
        with self.assertRaisesRegex(ValueError,'both available and future-hidden'):
            validate_scope(value)

    def test_worker_source_matches_host_independent_computation(self):
        data=validate_scope(SCOPE)
        from systems.workspace.nih_scope_bridge import SOURCE_DIRECTORY
        outcome=run_source(SOURCE_DIRECTORY,data)
        self.assertEqual(outcome['report'],expected_scope_report(data))


class NIHScopeWorkstationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.data=Path(self.tmp.name)/'runtime';self.data.mkdir()
        self.workstation=ProcessWorkstation(self.data/'workstation')
        self.runtime=HandoffRuntime(event_store=RuntimeJournal(self.data/'runtime.jsonl'))
        self.bridge=NIHScopeBridge(runtime=self.runtime,workstation=self.workstation)
        self.index=CoordinatorIndex(self.data/'coordinator-windows.jsonl')
        admit_research(self.index)
        self.input=validate_scope(SCOPE)
        copy_scope_source(self.data,version_id='source-v1',allow_copy=True)

    def admit(self,job='nih-p1-scope-01'):
        return self.bridge.admit(version_id='source-v1',inputs=self.input,
                                 from_actor='local-operator',job_id=job)

    def bind(self,job='nih-p1-scope-01'):
        self.index.bind_planned('complete-stack','nih',slot='cp-nih-p1-scope',
                                job_id=job,worker_id=WORKER_ID,version_id='source-v1')

    def test_copy_never_admits(self):
        self.assertEqual(self.runtime.snapshot(),{})
        self.assertFalse((self.data/'runtime.jsonl').exists())

    def test_ready_does_not_count_as_pass(self):
        self.admit(); self.bind()
        native=attach_native_cp_contracts(from_existing_workstation(self.data),self.runtime._handoffs.values())
        result=one_cp_handoff(self.index,'complete-stack',native)['cp_automation']
        self.assertEqual(result['witnessed'],[])
        self.assertIn(CP_ID,result['frontier'])

    def test_complete_requires_reverify_and_advances_ontology(self):
        self.admit();self.bind()
        self.assertEqual(self.runtime.state('nih-p1-scope-01').status,'READY')
        with self.assertRaises(PermissionError):
            self.bridge.execute('nih-p1-scope-01')
        outcome=run_job(data_dir=self.data,job_id='nih-p1-scope-01',confirm_execute='nih-p1-scope-01')
        self.assertEqual(outcome['status'],'COMPLETE')
        fresh=attach_native_cp_contracts(from_existing_workstation(self.data),self.runtime._handoffs.values())
        report=freshly_reverify_linked_jobs(self.index,'complete-stack',fresh,
                                lambda j:reverify_job(data_dir=self.data,job_id=j))
        cp=one_cp_handoff(self.index,'complete-stack',report)['cp_automation']
        self.assertEqual(cp['witnessed'],[CP_ID])
        self.assertIn('NIH-P1-ONTOLOGY',cp['frontier'])
        self.assertIn('GAME-W13-WORLDS',cp['frontier'])
        self.assertNotIn('NIH-P2-TEST',cp['frontier'])

    def test_worker_forged_report_fails_without_result(self):
        handoff=self.admit()
        witness=self.bridge.runtime.get(handoff.handoff_id)
        from runtime.handoff import EvidenceRecord
        from systems.workspace.nih_scope_bridge import WITNESS,SOURCE
        fake=ExecutionResult(status='COMPLETE',output={
            'kind':'nih-synthetic-temporal-scope/v1','checkpoint_contract':CP_ID,
            'checkpoint_verdict':'PASS','checkpoint_worker_role':'research-scoper',
            'native_verifier':VERIFIER,'report':{**expected_scope_report(self.input),'visible_ids':['delayed-result']},
            'worker_version':'source-v1', 'edition_fingerprint':handoff.metadata['edition_fingerprint'],'child_pid':1},
            evidence=(EvidenceRecord(condition=WITNESS,kind='computation',source=SOURCE,
                                    ref=handoff.metadata['edition_fingerprint'],depth='independent-host-replay'),))
        with self.assertRaisesRegex(ValueError,'host verifier rejected'):
            self.runtime.return_result(handoff.handoff_id,actor_id=handoff.to_actor,result=fake)
        self.assertEqual(self.runtime.state(handoff.handoff_id).status,'READY')

    def test_source_edit_blocks_execution(self):
        self.admit()
        source=self.data/'workstation'/WORKER_ID/'source-v1'/'nih_scope_source.py'
        source.write_text(source.read_text()+'\n# edit\n')
        with self.assertRaisesRegex(ValueError,'changed'):
            self.bridge.execute('nih-p1-scope-01',allow_local_execution=True)
        self.assertEqual(self.runtime.state('nih-p1-scope-01').status,'READY')

    def test_bad_job_id_confirmation_cannot_execute(self):
        self.admit()
        with self.assertRaises(PermissionError):
            run_job(data_dir=self.data,job_id='nih-p1-scope-01',confirm_execute='wrong')
        self.assertEqual(self.runtime.state('nih-p1-scope-01').status,'READY')

    def test_restart_and_no_duplicate_result(self):
        self.admit();self.bind()
        run_job(data_dir=self.data,job_id='nih-p1-scope-01',confirm_execute='nih-p1-scope-01')
        before=(self.data/'runtime.jsonl').read_bytes()
        result=run_job(data_dir=self.data,job_id='nih-p1-scope-01',confirm_execute='nih-p1-scope-01')
        self.assertTrue(result['reverified'])
        self.assertEqual(before,(self.data/'runtime.jsonl').read_bytes())

if __name__=='__main__':unittest.main()