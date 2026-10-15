"""Native RDF triple equivalence and CP-dependent Process Workstation jobs."""
from __future__ import annotations
import copy,json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from rdflib import Graph
from runtime.engine import HandoffRuntime
from runtime.handoff import ExecutionResult
from runtime.journal import RuntimeJournal
from systems.workspace.workstation import ProcessWorkstation
from systems.workspace.nih_scope_bridge import NIHScopeBridge,copy_scope_source,WORKER_ID as SCOPE_ID
from systems.workspace.nih_scope_native import validate_scope
from systems.workspace.nih_ontology_bridge import NIHOntologyBridge,copy_ontology_source,WORKER_ID,run_source
from systems.workspace.nih_ontology_native import validate_request, verify_report,CP_ID,VERIFIER
from systems.workspace.controls import run_job,reverify_job
from systems.workspace.coordinator_window import CoordinatorIndex,from_existing_workstation,freshly_reverify_linked_jobs
from systems.workspace.cp_motion import admit_research,one_cp_handoff,attach_native_cp_contracts

ROOT=Path(__file__).resolve().parents[2]
SCOPE=json.loads((ROOT/'network/tests/fixtures/nih_scope_example.json').read_text())
REQ={'kind':'synthetic-temporal-ontology/v1','synthetic':True,'mapping_id':'synthetic-one',
     'scope_job_id':'scope-job','format':'turtle'}


class OntologyNativeTests(unittest.TestCase):
    def test_parse_real_rdf_turtle_and_preserve_future_fact_without_promoting(self):
        from systems.workspace.nih_ontology_bridge import SOURCE_DIRECTORY
        child=run_source(SOURCE_DIRECTORY,{'request':REQ,'scope':validate_scope(SCOPE)})
        check=verify_report(child['report'],scope=SCOPE,mapping_id=REQ['mapping_id'])
        self.assertEqual(check['visible_ids'],['prior-note'])
        self.assertEqual(check['withheld_future_ids'],['delayed-result'])
        g=Graph().parse(data=child['report']['turtle'],format='turtle')
        from systems.workspace.nih_ontology_native import EX, RDF, Literal, XSD
        self.assertIn((EX['obs-delayed-result'],EX.eligibleAtQuery,Literal(False,datatype=XSD.boolean)),g)
        self.assertEqual(check['triple_count'],len(g))

    def test_reject_tampered_visible_or_added_rdf_fact(self):
        from systems.workspace.nih_ontology_bridge import SOURCE_DIRECTORY
        child=run_source(SOURCE_DIRECTORY,{'request':REQ,'scope':validate_scope(SCOPE)})
        report=child['report']
        for change in ('future-promoted','extra-edge','missing-time','bad-syntax','false-count'):
            bad=copy.deepcopy(report)
            if change=='future-promoted':
                bad['turtle']=bad['turtle'].replace('"false"^^<http://www.w3.org/2001/XMLSchema#boolean>','"true"^^<http://www.w3.org/2001/XMLSchema#boolean>')
            elif change=='extra-edge':
                bad['turtle']+='\n<https://example.org/nih-temporal-synthetic/obs-delayed-result> <https://example.org/nih-temporal-synthetic/diagnosed> "true" .\n'
            elif change=='missing-time':
                bad['turtle']='\n'.join(x for x in bad['turtle'].splitlines() if 'inXSDDate' not in x)
            elif change=='bad-syntax': bad['turtle']='not RDF Turtle !'
            else: bad['triple_count']+=1
            with self.subTest(change=change),self.assertRaises(ValueError):
                verify_report(bad,scope=SCOPE,mapping_id=REQ['mapping_id'])

    def test_reject_unbounded_or_untrusted_request(self):
        for m in ({'synthetic':False},{'scope_job_id':'../../secret'},{'format':'json-ld'},
                  {'patient_name':'Someone'},{'mapping_id':'invalid space'}):
            with self.subTest(m=m),self.assertRaises(ValueError):validate_request({**REQ,**m})


class OntologyWorkstationTests(unittest.TestCase):
    def setUp(self):
        t=TemporaryDirectory();self.addCleanup(t.cleanup)
        self.data=Path(t.name)/'runtime';self.data.mkdir()
        self.workstation=ProcessWorkstation(self.data/'workstation')
        self.runtime=HandoffRuntime(event_store=RuntimeJournal(self.data/'runtime.jsonl'))
        self.scope_bridge=NIHScopeBridge(runtime=self.runtime,workstation=self.workstation)
        self.bridge=NIHOntologyBridge(runtime=self.runtime,workstation=self.workstation,scope_bridge=self.scope_bridge)
        self.index=CoordinatorIndex(self.data/'coordinator-windows.jsonl')
        admit_research(self.index)
        copy_scope_source(self.data,version_id='scope-v1',allow_copy=True)
        copy_ontology_source(self.data,version_id='ontology-v1',allow_copy=True)

    def scope(self):
        self.scope_bridge.admit(version_id='scope-v1',inputs=SCOPE,from_actor='operator',job_id='scope-job')
        self.index.bind_planned('complete-stack','nih',slot='cp-nih-p1-scope',job_id='scope-job',worker_id=SCOPE_ID,version_id='scope-v1')
        run_job(data_dir=self.data,job_id='scope-job',confirm_execute='scope-job')
        # A separate workstation command wrote the journal; reopen it before
        # the next CP rather than using a stale in-memory runtime snapshot.
        self.runtime=HandoffRuntime(event_store=RuntimeJournal(self.data/'runtime.jsonl'))
        self.scope_bridge=NIHScopeBridge(runtime=self.runtime,workstation=self.workstation)
        self.bridge=NIHOntologyBridge(runtime=self.runtime,workstation=self.workstation,scope_bridge=self.scope_bridge)

    def admit(self):
        return self.bridge.admit(version_id='ontology-v1',inputs=REQ,from_actor='operator',job_id='ontology-job')

    def test_scope_is_required_before_ontology_job_admission(self):
        with self.assertRaises(KeyError):self.admit()
        self.scope_bridge.admit(version_id='scope-v1',inputs=SCOPE,from_actor='operator',job_id='scope-job')
        with self.assertRaisesRegex(ValueError,'not completed'):self.admit()
        self.assertEqual(len(self.runtime.snapshot()),1)

    def test_successful_handoff_advances_only_next_checkpoint(self):
        self.scope();self.admit()
        self.index.bind_planned('complete-stack','nih',slot='cp-nih-p1-ontology',job_id='ontology-job',worker_id=WORKER_ID,version_id='ontology-v1')
        with self.assertRaises(PermissionError):self.bridge.execute('ontology-job')
        self.assertEqual(self.runtime.state('ontology-job').status,'READY')
        self.assertEqual(run_job(data_dir=self.data,job_id='ontology-job',confirm_execute='ontology-job')['status'],'COMPLETE')
        native=attach_native_cp_contracts(from_existing_workstation(self.data),self.runtime._handoffs.values())
        fresh=freshly_reverify_linked_jobs(self.index,'complete-stack',native,lambda job: reverify_job(data_dir=self.data,job_id=job))
        packet=one_cp_handoff(self.index,'complete-stack',fresh)
        cp=packet['cp_automation']
        self.assertEqual(cp['witnessed'],['NIH-P1-ONTOLOGY','NIH-P1-SCOPE'])
        self.assertIn('NIH-P1-REASONING',cp['frontier'])
        self.assertIn('GAME-W13-WORLDS',cp['frontier'])
        self.assertNotIn('NIH-P2-TEST',cp['frontier'])

    def test_copy_is_not_job_and_forged_rdf_is_rejected(self):
        self.scope();h=self.admit()
        run_job(data_dir=self.data,job_id='ontology-job',confirm_execute='ontology-job')
        restored=HandoffRuntime(event_store=RuntimeJournal(self.data/'runtime.jsonl'))
        current=restored.state('ontology-job')
        forged=copy.deepcopy(current.output)
        forged['report']['visible_ids']=['delayed-result']
        with self.assertRaisesRegex(ValueError,'availability claim'):
            self.bridge._verify(h,ExecutionResult(status='COMPLETE',output=forged,evidence=current.evidence))

    def test_changed_ontology_source_blocks_run(self):
        self.scope();self.admit()
        path=self.data/'workstation'/WORKER_ID/'ontology-v1'/'ontology_worker.py'
        path.write_text(path.read_text()+'\n# altered\n')
        with self.assertRaisesRegex(ValueError,'changed'):
            self.bridge.execute('ontology-job',allow_local_execution=True)
        self.assertEqual(self.runtime.state('ontology-job').status,'READY')

    def test_stale_parent_blocks_reverify(self):
        self.scope();self.admit()
        run_job(data_dir=self.data,job_id='ontology-job',confirm_execute='ontology-job')
        scope_path=self.data/'workstation'/SCOPE_ID/'scope-v1'/'nih_scope_source.py'
        scope_path.write_text(scope_path.read_text()+'\n# stale\n')
        with self.assertRaisesRegex(ValueError,'changed'):
            reverify_job(data_dir=self.data,job_id='ontology-job')

    def test_restart_reverify_does_not_append_job_event(self):
        self.scope();self.admit()
        run_job(data_dir=self.data,job_id='ontology-job',confirm_execute='ontology-job')
        old=(self.data/'runtime.jsonl').read_bytes()
        output=run_job(data_dir=self.data,job_id='ontology-job',confirm_execute='ontology-job')
        self.assertTrue(output['reverified'])
        self.assertEqual(old,(self.data/'runtime.jsonl').read_bytes())

    def test_wrong_confirmation_blocks_execution(self):
        self.scope();self.admit()
        with self.assertRaises(PermissionError):run_job(data_dir=self.data,job_id='ontology-job',confirm_execute='wrong')
        self.assertEqual(self.runtime.state('ontology-job').status,'READY')

if __name__=='__main__':unittest.main()