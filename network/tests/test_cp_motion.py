import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from systems.workspace.coordinator_window import CoordinatorIndex
from systems.workspace.cp_motion import (
    GRAPH, Checkpoint, admit_research, checkpoint_frontier, validate_graph,
    one_cp_handoff, handoff_markdown, attach_native_cp_contracts)


def native(cp, *, status='COMPLETE', source_state='MATCHES_ADMISSION',
           verification='natively-reverified', verdict='PASS',missing=(), verifier=None):
    verifier=verifier or f'cp-checker:{cp}'
    return {'job_id':f'{cp}-job', 'worker_id':'source-owned-worker', 'version_id':'v1',
            'status':status, 'source_state':source_state, 'verification':verification,
            'missing_witnesses':list(missing),'blocked_by':[],
            'checkpoint_contract':cp,'native_verifier':verifier,
            'result':{'checkpoint_contract':cp, 'checkpoint_verdict':verdict,
                      'checkpoint_worker_role':next(x.worker_role for x in GRAPH if x.id==cp),
                      'native_verifier':verifier}}


class CPMotionTests(unittest.TestCase):
    def setUp(self):
        tmp=TemporaryDirectory();self.addCleanup(tmp.cleanup)
        self.index=CoordinatorIndex(Path(tmp.name)/'coordinator-windows.jsonl')

    def test_bootstrap_is_automatic_and_idempotent(self):
        self.assertEqual(admit_research(self.index), len(GRAPH))
        self.assertEqual(admit_research(self.index),0)
        lanes,links=self.index.definition('complete-stack')
        self.assertEqual(set(lanes),{'game','correspondence','nih'})
        self.assertEqual(sum(map(len,links.values())),len(GRAPH))

    def test_intake_pins_existing_research_artifact_without_fabricating_worker(self):
        with TemporaryDirectory() as tmp:
            source=Path(tmp)/'nih_source.zip'
            source.write_bytes(b'historical-contract')
            added=admit_research(self.index,source_zip=source)
            self.assertEqual(added,len(GRAPH)+1)
            _,links=self.index.definition('complete-stack')
            intake=next(x for x in links['nih'] if x['slot']=='nih-intake')
            self.assertEqual(intake['source_kind'],'artifact')
            self.assertEqual(admit_research(self.index,source_zip=source),0)

    def test_intake_opens_phase1_and_game_parallel(self):
        f=checkpoint_frontier({'jobs':[]})
        self.assertEqual(set(f['frontier']),{'NIH-P1-SCOPE','GAME-W13-WORLDS'})
        self.assertEqual(f['started_workers'],0)

    def test_phase1_can_move_without_completed_game_engine(self):
        jobs=[native('NIH-P1-SCOPE')]
        f=checkpoint_frontier({'jobs':jobs})
        self.assertIn('NIH-P1-ONTOLOGY',f['frontier'])
        self.assertNotIn('NIH-P2-TEST',f['frontier'])
        self.assertIn('GAME-W13-WORLDS',f['frontier'])

    def test_verified_phase1_and_prototype_do_not_skip_engine(self):
        cps=['NIH-P1-SCOPE','NIH-P1-ONTOLOGY','NIH-P1-REASONING','NIH-P1-PACKET','NIH-P2-PROTOTYPE']
        f=checkpoint_frontier({'jobs':[native(x) for x in cps]})
        phase2=next(x for x in f['checkpoints'] if x['checkpoint']=='NIH-P2-TEST')
        self.assertEqual(phase2['state'],'BLOCKED')
        self.assertEqual(phase2['blocked_by'],['GAME-WORKER-READY'])

    def test_finished_engine_unlocks_phase2_test_not_official_submission(self):
        cps=['NIH-P1-SCOPE','NIH-P1-ONTOLOGY','NIH-P1-REASONING','NIH-P1-PACKET',
             'NIH-P2-PROTOTYPE','GAME-W13-WORLDS','GAME-NATIVE-VERIFIER','GAME-WORKER-READY']
        f=checkpoint_frontier({'jobs':[native(x) for x in cps]})
        self.assertIn('NIH-P2-TEST',f['frontier'])
        self.assertNotIn('NIH-P2-SUBMISSION',f['frontier'])

    def test_cp30_generic_success_cannot_become_nih_witness(self):
        job=native('NIH-P1-SCOPE',verifier='integrated-cp30-synthetic-route-audit-v1')
        f=checkpoint_frontier({'jobs':[job]})
        self.assertEqual(f['witnessed'],[])
        self.assertEqual(len(f['refused_claims']),1)

    def test_future_checkpoint_cannot_skip_ancestry(self):
        f=checkpoint_frontier({'jobs':[native('GAME-WORKER-READY')]})
        self.assertEqual(f['witnessed'],[])
        self.assertNotIn('NIH-P2-TEST',f['frontier'])
        self.assertTrue(any(r['reason']=='missing certified checkpoint ancestry' for r in f['refused_claims']))

    def test_native_freshness_fail_closed(self):
        for changes in ({'status':'READY'},{'source_state':'SOURCE_CHANGED'},
                        {'verification':'recorded-not-reverified'},{'verdict':'UNPROVED'},
                        {'missing':('required-ontology',)}):
            with self.subTest(changes=changes):
                f=checkpoint_frontier({'jobs':[native('NIH-P1-SCOPE',**changes)]})
                self.assertEqual(f['witnessed'],[])

    def test_result_cannot_self_assign_contract_without_handoff(self):
        job=native('NIH-P1-SCOPE');job.pop('checkpoint_contract');job.pop('native_verifier')
        handoff=SimpleNamespace(handoff_id=job['job_id'],metadata={
            'worker_id':'source-owned-worker','worker_version':'v1',
            'native_evidence_verifier':'cp-checker:OTHER',
            'checkpoint_contract':'NIH-P1-SCOPE'})
        attached=attach_native_cp_contracts({'jobs':[job]},[handoff])
        self.assertFalse(checkpoint_frontier(attached)['witnessed'])

    def test_result_requires_handoff_native_contract(self):
        job=native('NIH-P1-SCOPE');job.pop('checkpoint_contract');job.pop('native_verifier')
        handoff=SimpleNamespace(handoff_id=job['job_id'],metadata={
            'worker_id':'source-owned-worker','worker_version':'v1',
            'native_evidence_verifier':'cp-checker:NIH-P1-SCOPE',
            'checkpoint_contract':'NIH-P1-SCOPE'})
        attached=attach_native_cp_contracts({'jobs':[job]},[handoff])
        self.assertEqual(checkpoint_frontier(attached)['witnessed'],['NIH-P1-SCOPE'])

    def test_external_nih_award_cannot_be_inferred(self):
        f=checkpoint_frontier({'jobs':[native('NIH-P1-AWARD')]})
        self.assertNotIn('NIH-P1-AWARD',f['witnessed'])
        with self.assertRaisesRegex(ValueError,'independent authority'):
            checkpoint_frontier({'jobs':[]},official_proofs=['NIH-P1-AWARD'])

    def test_cycle_and_unknown_dependencies_rejected(self):
        with self.assertRaisesRegex(ValueError,'cycle'):
            validate_graph((Checkpoint('a','nih','a',('b',),'x'),Checkpoint('b','nih','b',('a',),'x')))
        with self.assertRaisesRegex(ValueError,'unknown'):
            validate_graph((Checkpoint('a','nih','a',('b',),'x'),))

    def test_unlinked_native_job_cannot_advance_this_window(self):
        admit_research(self.index)
        job=native('NIH-P1-SCOPE')
        packet=one_cp_handoff(self.index,'complete-stack',{'jobs':[job]})
        self.assertEqual(packet['cp_automation']['witnessed'],[])
        # Binding requires a genuine native admission in the real CLI; this
        # unit test exercises the index/CP projection against a fixture.
        self.index.bind_planned('complete-stack','nih',slot='cp-nih-p1-scope',
                                job_id=job['job_id'],worker_id=job['worker_id'],
                                version_id=job['version_id'])
        witnessed=one_cp_handoff(self.index,'complete-stack',{'jobs':[job]})
        self.assertEqual(witnessed['cp_automation']['witnessed'],['NIH-P1-SCOPE'])

    def test_one_packet_contains_all_workers_and_frontier(self):
        admit_research(self.index)
        status=one_cp_handoff(self.index,'complete-stack',{'jobs':[]})
        self.assertEqual(len(status['workers']),len(GRAPH)+1) # correspondence lane has no planned slots
        self.assertIn('NIH-P1-SCOPE',handoff_markdown(status))
        self.assertFalse(status['execution_triggered'])


if __name__=='__main__':unittest.main()