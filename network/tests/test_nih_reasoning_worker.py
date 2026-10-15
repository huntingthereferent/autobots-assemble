"""NIH-P1-REASONING native CP witness and full prior scope->RDF->reasoning ancestry."""
from __future__ import annotations
import copy,json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from runtime.engine import HandoffRuntime
from runtime.handoff import ExecutionResult
from runtime.journal import RuntimeJournal
from systems.workspace.workstation import ProcessWorkstation
from systems.workspace.nih_scope_bridge import NIHScopeBridge, copy_scope_source, WORKER_ID as SCOPE_ID
from systems.workspace.nih_ontology_bridge import NIHOntologyBridge, copy_ontology_source, WORKER_ID as ONTO_ID
from systems.workspace.nih_reasoning_bridge import NIHReasoningBridge, copy_reasoning_source, WORKER_ID, run_source
from systems.workspace.nih_reasoning_native import (validate_request,expected_reasoning_report,
    verify_reasoning_report,CP_ID,VERIFIER)
from systems.workspace.nih_ontology_worker_source.ontology_worker import render
from systems.workspace.controls import run_job,reverify_job
from systems.workspace.coordinator_window import (CoordinatorIndex,from_existing_workstation,
    freshly_reverify_linked_jobs)
from systems.workspace.cp_motion import admit_research,one_cp_handoff,attach_native_cp_contracts

ROOT=Path(__file__).resolve().parents[2]
SCOPE=json.loads((ROOT/'network/tests/fixtures/nih_scope_example.json').read_text())
REQUEST=json.loads((ROOT/'network/tests/fixtures/nih_reasoning_example.json').read_text())
ONTO_REQ={'kind':'synthetic-temporal-ontology/v1','synthetic':True,
          'mapping_id':'synthetic-one','scope_job_id':'scope-job','format':'turtle'}


class ReasoningNativeTests(unittest.TestCase):
    def report(self, scope=SCOPE, req=REQUEST):
        from systems.workspace.nih_reasoning_bridge import SOURCE_DIRECTORY
        ontology=render(ONTO_REQ,scope)
        result=run_source(SOURCE_DIRECTORY,{'request':validate_request(req),
                                           'ontology_turtle':ontology['turtle'],
                                           'scope':scope,'mapping_id':'synthetic-one'})['report']
        return result,ontology

    def test_as_known_at_and_expired_interval(self):
        result,ontology=self.report()
        self.assertEqual(verify_reasoning_report(result,request=REQUEST,scope=SCOPE,
                   ontology_report=ontology,mapping_id='synthetic-one')['verdict'],'PASS')
        cases={row['id']:row for row in result['cases']}
        self.assertEqual(cases['before-result']['withheld_future'],['delayed-result'])
        self.assertEqual(cases['before-result']['admissible'],['prior-note'])
        self.assertEqual(cases['after-result']['admissible'],['delayed-result','prior-note'])
        self.assertEqual(cases['after-validity']['not_applicable'],['delayed-result','prior-note'])

    def test_declared_functional_predicate_conflicts_only_after_known(self):
        scope=copy.deepcopy(SCOPE)
        duplicate=copy.deepcopy(scope['observations'][0]);duplicate.update(
            id='second-status',object='other-status',known_at='2026-01-05',source_ref='fixture-update')
        scope['observations'].append(duplicate)
        result,ontology=self.report(scope)
        self.assertEqual(verify_reasoning_report(result,request=REQUEST,scope=scope,
                ontology_report=ontology,mapping_id='synthetic-one')['declared_conflict_cases'],1)
        cases={x['id']:x for x in result['cases']}
        self.assertEqual(cases['before-result']['declared_conflicts'],[])
        self.assertEqual(cases['after-result']['declared_conflicts'],[['prior-note','second-status']])
        nonexclusive={**REQUEST,'functional_predicates':['has-result']}
        nonexclusive_result,_=self.report(scope,nonexclusive)
        self.assertEqual([x['declared_conflicts'] for x in nonexclusive_result['cases']],[[],[],[]])

    def test_reject_forged_result_and_future_leakage(self):
        report,ontology=self.report()
        for mutation in ('promote-future','fake-conflict','rewrite-parent','false-claim'):
            fake=copy.deepcopy(report); parent=copy.deepcopy(ontology)
            if mutation=='promote-future':
                next(x for x in fake['cases'] if x['id']=='before-result')['admissible'].append('delayed-result')
            elif mutation=='fake-conflict':fake['cases'][0]['declared_conflicts']=[['x','y']]
            elif mutation=='rewrite-parent':parent['turtle']+='\n<https://example.org/nih-temporal-synthetic/fake> <https://example.org/nih-temporal-synthetic/diagnosed> "true" .\n'
            else:fake['conclusion']='clinical-diagnosis'
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):
                verify_reasoning_report(fake,request=REQUEST,scope=SCOPE,
                                        ontology_report=parent,mapping_id='synthetic-one')

    def test_refuse_undeclared_constraints_unsafe_requests(self):
        for changes in ({'synthetic':False},{'ontology_job_id':'../../escape'},
                        {'functional_predicates':[]},{'functional_predicates':['has-status']*2},
                        {'cases':[REQUEST['cases'][0]]},
                        {'cases':[REQUEST['cases'][0]]*2},
                        {'patient_name':'fake'}):
            with self.subTest(changes=changes),self.assertRaises(ValueError):
                validate_request({**REQUEST,**changes})


class ReasoningWorkstationTests(unittest.TestCase):
    def setUp(self):
        temp=TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.data=Path(temp.name)/'runtime';self.data.mkdir()
        self.index=CoordinatorIndex(self.data/'coordinator-windows.jsonl')
        admit_research(self.index)
        copy_scope_source(self.data,version_id='scope-v1',allow_copy=True)
        copy_ontology_source(self.data,version_id='ontology-v1',allow_copy=True)
        copy_reasoning_source(self.data,version_id='reasoning-v1',allow_copy=True)
        self.reload()

    def reload(self):
        self.runtime=HandoffRuntime(event_store=RuntimeJournal(self.data/'runtime.jsonl'))
        self.workstation=ProcessWorkstation(self.data/'workstation')
        self.scope=NIHScopeBridge(runtime=self.runtime,workstation=self.workstation)
        self.ontology=NIHOntologyBridge(runtime=self.runtime,workstation=self.workstation,scope_bridge=self.scope)
        self.reasoning=NIHReasoningBridge(runtime=self.runtime,workstation=self.workstation,ontology_bridge=self.ontology)

    def prior(self):
        self.scope.admit(version_id='scope-v1',inputs=SCOPE,from_actor='operator',job_id='scope-job')
        self.index.bind_planned('complete-stack','nih',slot='cp-nih-p1-scope',
                                job_id='scope-job',worker_id=SCOPE_ID,version_id='scope-v1')
        run_job(data_dir=self.data,job_id='scope-job',confirm_execute='scope-job')
        self.reload()
        self.ontology.admit(version_id='ontology-v1',inputs=ONTO_REQ,from_actor='operator',job_id='ontology-job')
        self.index.bind_planned('complete-stack','nih',slot='cp-nih-p1-ontology',
                                job_id='ontology-job',worker_id=ONTO_ID,version_id='ontology-v1')
        run_job(data_dir=self.data,job_id='ontology-job',confirm_execute='ontology-job')
        self.reload()

    def admit(self):
        return self.reasoning.admit(version_id='reasoning-v1',inputs=REQUEST,from_actor='operator',job_id='reasoning-job')

    def test_cannot_skip_scope_or_ontology(self):
        with self.assertRaises(KeyError):self.admit()
        self.scope.admit(version_id='scope-v1',inputs=SCOPE,from_actor='operator',job_id='scope-job')
        with self.assertRaises(KeyError):self.admit()
        self.assertEqual(len(self.runtime.snapshot()),1)

    def test_full_three_worker_CP_advance(self):
        self.prior();self.admit()
        self.index.bind_planned('complete-stack','nih',slot='cp-nih-p1-reasoning',
                                job_id='reasoning-job',worker_id=WORKER_ID,version_id='reasoning-v1')
        self.assertEqual(self.runtime.state('reasoning-job').status,'READY')
        with self.assertRaises(PermissionError):self.reasoning.execute('reasoning-job')
        run_job(data_dir=self.data,job_id='reasoning-job',confirm_execute='reasoning-job')
        self.reload()
        native=attach_native_cp_contracts(from_existing_workstation(self.data),self.runtime._handoffs.values())
        native=freshly_reverify_linked_jobs(self.index,'complete-stack',native,
                         lambda job:reverify_job(data_dir=self.data,job_id=job))
        result=one_cp_handoff(self.index,'complete-stack',native)['cp_automation']
        self.assertEqual(result['witnessed'],['NIH-P1-ONTOLOGY','NIH-P1-REASONING','NIH-P1-SCOPE'])
        self.assertIn('NIH-P1-PACKET',result['frontier'])
        self.assertIn('NIH-P2-PROTOTYPE',result['frontier'])
        self.assertIn('GAME-W13-WORLDS',result['frontier'])
        self.assertNotIn('NIH-P2-TEST',result['frontier'])

    def test_parent_must_be_complete(self):
        self.prior()
        with self.assertRaisesRegex(ValueError,'ontology parent'):
            self.admit() if False else self.reasoning.admit(version_id='reasoning-v1',inputs={**REQUEST,'ontology_job_id':'missing-parent'},from_actor='operator')

    def test_forged_result_is_rejected_by_host_verifier(self):
        self.prior();h=self.admit()
        run_job(data_dir=self.data,job_id='reasoning-job',confirm_execute='reasoning-job')
        new_runtime=HandoffRuntime(event_store=RuntimeJournal(self.data/'runtime.jsonl'))
        result=new_runtime.state('reasoning-job')
        forged=copy.deepcopy(result.output)
        forged['report']['cases'][0]['admissible']=['invented']
        with self.assertRaisesRegex(ValueError,'host temporal reasoning witness'):
            self.reasoning._verify(h,ExecutionResult(status='COMPLETE',output=forged,evidence=result.evidence))

    def test_changed_ontology_source_invalidates_reasoning_reverify(self):
        self.prior();self.admit()
        run_job(data_dir=self.data,job_id='reasoning-job',confirm_execute='reasoning-job')
        original=self.data/'workstation'/ONTO_ID/'ontology-v1'/'ontology_worker.py'
        original.write_text(original.read_text()+'\n# tampered\n')
        with self.assertRaisesRegex(ValueError,'changed'):
            reverify_job(data_dir=self.data,job_id='reasoning-job')

    def test_modified_reasoning_source_blocks_execution(self):
        self.prior();self.admit()
        source=self.data/'workstation'/WORKER_ID/'reasoning-v1'/'reasoning_worker.py'
        source.write_text(source.read_text()+'\n# changed\n')
        with self.assertRaisesRegex(ValueError,'changed'):
            self.reasoning.execute('reasoning-job',allow_local_execution=True)

    def test_exact_execution_and_recovery_is_idempotent(self):
        self.prior();self.admit()
        with self.assertRaises(PermissionError):run_job(data_dir=self.data,job_id='reasoning-job',confirm_execute='wrong')
        run_job(data_dir=self.data,job_id='reasoning-job',confirm_execute='reasoning-job')
        journal=self.data/'runtime.jsonl';before=journal.read_bytes()
        again=run_job(data_dir=self.data,job_id='reasoning-job',confirm_execute='reasoning-job')
        self.assertTrue(again['reverified']);self.assertEqual(journal.read_bytes(),before)

if __name__=='__main__':unittest.main()