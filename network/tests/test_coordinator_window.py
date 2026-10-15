from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import hashlib
import json
import unittest
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from systems.workspace.coordinator_window import CoordinatorIndex,one_window_status,markdown_handoff,freshly_reverify_linked_jobs,run_exact_linked_job


class CoordinatorWindowTests(unittest.TestCase):
    def setUp(self):
        td=TemporaryDirectory(); self.addCleanup(td.cleanup)
        self.root=Path(td.name)
        self.journal=self.root/'index.jsonl'
        self.index=CoordinatorIndex(self.journal)
        self.index.create_window('one-window')
        self.good_view={'jobs':[{'job_id':'cp30-job','worker_id':'finite-correspondence-integrated',
            'version_id':'cp30-original','status':'COMPLETE','source_state':'MATCHES_ADMISSION',
            'verification':'recorded-not-reverified','missing_witnesses':[],
            'blocked_by':[],'events':[{'event_type':'RESULT'}]}]}

    def test_empty_window_does_not_invent_jobs(self):
        s=one_window_status(self.index,'one-window',self.good_view)
        self.assertEqual([r['status'] for r in s['workers']],['NOT_ADMITTED']*3)
        self.assertFalse(s['complete'])
        self.assertFalse(s['triggered_execution'])

    def test_native_exact_link_read_from_existing_status(self):
        self.index.link_runtime('one-window','correspondence',job_id='cp30-job',worker_id='finite-correspondence-integrated',version_id='cp30-original')
        s=one_window_status(self.index,'one-window',self.good_view)
        r=next(x for x in s['workers'] if x['lane']=='correspondence')
        self.assertEqual(r['status'],'COMPLETE')
        self.assertEqual(r['verification'],'recorded-not-reverified')
        self.assertFalse(s['complete'])

    def test_native_status_follows_live_view(self):
        self.index.link_runtime('one-window','correspondence',job_id='cp30-job',worker_id='finite-correspondence-integrated',version_id='cp30-original')
        for state in ['WAITING','READY','ACTIVE','BLOCKED','FAILED','COMPLETE']:
            view=json.loads(json.dumps(self.good_view));view['jobs'][0]['status']=state
            self.assertEqual(one_window_status(self.index,'one-window',view)['workers'][1]['status'],state)

    def test_worker_identity_mismatch_rejected(self):
        self.index.link_runtime('one-window','correspondence',job_id='cp30-job',worker_id='finite-correspondence-integrated',version_id='cp30-original')
        view={'jobs':[dict(self.good_view['jobs'][0],version_id='different')]}
        self.assertEqual(one_window_status(self.index,'one-window',view)['workers'][1]['status'],'IDENTITY_MISMATCH')

    def test_unknown_runtime_job_never_completed(self):
        self.index.link_runtime('one-window','correspondence',job_id='cp30-job',worker_id='finite-correspondence-integrated',version_id='cp30-original')
        self.assertEqual(one_window_status(self.index,'one-window',{'jobs':[]})['workers'][1]['status'],'UNAVAILABLE')

    def test_artifact_is_history_not_live_worker(self):
        data=b'original W12 signed test evidence'
        (self.root/'W12.zip').write_bytes(data)
        self.index.link_artifact('one-window','game',locator='W12.zip',
            sha256_hex=hashlib.sha256(data).hexdigest(),historical_note='local pass')
        row=one_window_status(self.index,'one-window',{'jobs':[]},artifact_dir=self.root)['workers'][0]
        self.assertEqual(row['artifact_integrity'],'MATCH')
        self.assertEqual(row['status'],'HISTORICAL_ONLY')
        self.assertNotEqual(row['verification'],'natively-reverified')
        self.assertFalse(one_window_status(self.index,'one-window',{'jobs':[]},artifact_dir=self.root)['complete'])

    def test_modified_artifact_flagged(self):
        p=self.root/'W12.zip';p.write_text('before')
        self.index.link_artifact('one-window','game',locator=p.name,
            sha256_hex=hashlib.sha256(p.read_bytes()).hexdigest(),historical_note='test')
        p.write_text('after')
        row=one_window_status(self.index,'one-window',{'jobs':[]},artifact_dir=self.root)['workers'][0]
        self.assertEqual(row['artifact_integrity'],'MISMATCH')

    def test_artifact_cannot_escape_root(self):
        self.index.link_artifact('one-window','game',locator='../secret.txt',
            sha256_hex='0'*64,historical_note='test')
        outside=self.root.parent/'secret.txt'; outside.write_text('do not read')
        try:
            row=one_window_status(self.index,'one-window',{'jobs':[]},artifact_dir=self.root)['workers'][0]
            self.assertEqual(row['artifact_integrity'],'UNAVAILABLE')
        finally:outside.unlink()

    def test_hash_chain_tampering_is_refused(self):
        self.index.link_planned('one-window','nih',next_movement='W02')
        rows=self.journal.read_text().splitlines()
        edited=json.loads(rows[1]);edited['event']['next_movement']='fake pass'
        rows[1]=json.dumps(edited)
        self.journal.write_text('\n'.join(rows)+'\n')
        with self.assertRaisesRegex(ValueError,'history mismatch'):
            CoordinatorIndex(self.journal)

    def test_duplicate_lane_link_rejected(self):
        self.index.link_planned('one-window','nih',next_movement='W02')
        with self.assertRaisesRegex(ValueError,'repeated'):
            self.index.link_planned('one-window','nih',next_movement='replaced')

    def test_preserve_native_witness_missing(self):
        self.index.link_runtime('one-window','correspondence',job_id='cp30-job',worker_id='finite-correspondence-integrated',version_id='cp30-original')
        view={'jobs':[dict(self.good_view['jobs'][0], verification='natively-reverified',missing_witnesses=['source-owner'])]}
        r=one_window_status(self.index,'one-window',view)['workers'][1]
        self.assertEqual(r['missing_witnesses'],['source-owner'])
        self.assertFalse(one_window_status(self.index,'one-window',view)['complete'])

    def test_stale_source_never_promoted(self):
        self.index.link_runtime('one-window','correspondence',job_id='cp30-job',worker_id='finite-correspondence-integrated',version_id='cp30-original')
        view={'jobs':[dict(self.good_view['jobs'][0],verification='natively-reverified',source_state='SOURCE_CHANGED')]}
        self.assertFalse(one_window_status(self.index,'one-window',view)['complete'])

    def test_multiple_workers_same_lane(self):
        self.index.link_runtime('one-window','game',job_id='game-1',worker_id='game-engine',version_id='w13',slot='build')
        self.index.link_runtime('one-window','game',job_id='game-2',worker_id='game-witness',version_id='w13',slot='witness')
        v={'jobs':[dict(self.good_view['jobs'][0],job_id='game-1',worker_id='game-engine',version_id='w13',status='READY'),
                   dict(self.good_view['jobs'][0],job_id='game-2',worker_id='game-witness',version_id='w13',status='COMPLETE')]}
        a=one_window_status(self.index,'one-window',v)
        g=[r for r in a['workers'] if r['lane']=='game']
        self.assertEqual({r['slot'] for r in g},{'build','witness'})
        self.assertEqual({r['status'] for r in g},{'READY','COMPLETE'})
        self.assertIn('game',a['unresolved_lanes'])

    def test_native_reverify_checker_can_promote_recorded_check_only(self):
        self.index.link_runtime('one-window','correspondence',job_id='cp30-job',worker_id='finite-correspondence-integrated',version_id='cp30-original')
        fresh=freshly_reverify_linked_jobs(self.index,'one-window',self.good_view,
            lambda name: {'job_id':name,'status':'COMPLETE','reverified':True,'executed':False})
        self.assertEqual(fresh['jobs'][0]['verification'],'natively-reverified')
        self.assertEqual(self.good_view['jobs'][0]['verification'],'recorded-not-reverified')

    def test_forged_native_reverify_is_rejected(self):
        self.index.link_runtime('one-window','correspondence',job_id='cp30-job',worker_id='finite-correspondence-integrated',version_id='cp30-original')
        forged=freshly_reverify_linked_jobs(self.index,'one-window',self.good_view,
            lambda name: {'job_id':name,'status':'COMPLETE','reverified':True,'executed':True})
        self.assertEqual(forged['jobs'][0]['verification'],'reverification-failed')

    def test_native_reverify_not_called_on_ready_job(self):
        self.index.link_runtime('one-window','correspondence',job_id='cp30-job',worker_id='finite-correspondence-integrated',version_id='cp30-original')
        view={'jobs':[dict(self.good_view['jobs'][0],status='READY')]}
        def fail(_):raise AssertionError('should not call')
        fresh=freshly_reverify_linked_jobs(self.index,'one-window',view,fail)
        self.assertEqual(fresh['jobs'][0]['verification'],'recorded-not-reverified')

    def test_native_dispatch_exact_approved_ready_job(self):
        self.index.link_runtime('one-window','correspondence',job_id='cp30-job',worker_id='finite-correspondence-integrated',version_id='cp30-original',slot='worker-a')
        view={'jobs':[dict(self.good_view['jobs'][0],status='READY')]}
        calls=[]
        result=run_exact_linked_job(self.index,'one-window','correspondence','worker-a','cp30-job',view,
                                    lambda job,confirm: calls.append((job,confirm)) or {'job_id':job,'status':'COMPLETE'})
        self.assertEqual(calls,[('cp30-job','cp30-job')])
        self.assertEqual(result['status'],'COMPLETE')

    def test_native_dispatch_refuses_no_confirmation(self):
        self.index.link_runtime('one-window','correspondence',job_id='cp30-job',worker_id='finite-correspondence-integrated',version_id='cp30-original',slot='worker-a')
        with self.assertRaises(PermissionError):
            run_exact_linked_job(self.index,'one-window','correspondence','worker-a','wrong',self.good_view,
                                 lambda job,confirm: self.fail('must not dispatch'))

    def test_native_dispatch_refuses_stale_source(self):
        self.index.link_runtime('one-window','correspondence',job_id='cp30-job',worker_id='finite-correspondence-integrated',version_id='cp30-original',slot='worker-a')
        view={'jobs':[dict(self.good_view['jobs'][0],status='READY',source_state='SOURCE_CHANGED')]}
        with self.assertRaisesRegex(ValueError,'source'):
            run_exact_linked_job(self.index,'one-window','correspondence','worker-a','cp30-job',view,
                                 lambda job,confirm: self.fail('must not dispatch'))

    def test_native_dispatch_refuses_historical_slot(self):
        self.index.link_planned('one-window','game',slot='world',next_movement='W13')
        with self.assertRaisesRegex(ValueError,'not a linked native'):
            run_exact_linked_job(self.index,'one-window','game','world','game-01',self.good_view,
                                 lambda job,confirm: self.fail('must not dispatch'))

    def test_native_dispatch_refuses_unsupported_state(self):
        self.index.link_runtime('one-window','correspondence',job_id='cp30-job',worker_id='finite-correspondence-integrated',version_id='cp30-original',slot='worker-a')
        view={'jobs':[dict(self.good_view['jobs'][0],status='ACTIVE')]}
        with self.assertRaisesRegex(ValueError,'not ready'):
            run_exact_linked_job(self.index,'one-window','correspondence','worker-a','cp30-job',view,
                                 lambda job,confirm: self.fail('must not dispatch'))

    def test_bind_planned_slot_to_native_worker_preserves_original_movement(self):
        self.index.link_planned('one-window','correspondence',slot='cp-one',next_movement='witness source')
        self.index.bind_planned('one-window','correspondence',slot='cp-one',job_id='cp30-job',
                                worker_id='finite-correspondence-integrated',version_id='cp30-original')
        replay=CoordinatorIndex(self.journal)
        link=replay.definition('one-window')[1]['correspondence'][0]
        self.assertEqual(link['source_kind'],'runtime-job')
        self.assertEqual(link['original_planned_movement'],'witness source')
        row=next(x for x in one_window_status(replay,'one-window',self.good_view)['workers']
                 if x['lane']=='correspondence')
        self.assertEqual(row['status'],'COMPLETE')
        self.assertEqual(row['slot'],'cp-one')
        self.assertEqual([e['event']['kind'] for e in replay.events],['WINDOW','LINK','BIND'])

    def test_binding_requires_existing_unbound_planned_slot(self):
        with self.assertRaisesRegex(ValueError,'unbound planned'):
            self.index.bind_planned('one-window','correspondence',slot='missing',job_id='cp30-job',
                                     worker_id='finite-correspondence-integrated',version_id='cp30-original')
        self.index.link_planned('one-window','correspondence',slot='cp-one',next_movement='start')
        self.index.bind_planned('one-window','correspondence',slot='cp-one',job_id='cp30-job',
                                 worker_id='finite-correspondence-integrated',version_id='cp30-original')
        with self.assertRaisesRegex(ValueError,'unbound planned'):
            self.index.bind_planned('one-window','correspondence',slot='cp-one',job_id='cp30-job',
                                     worker_id='finite-correspondence-integrated',version_id='cp30-original')

    def test_binding_wrong_identity_never_executes(self):
        self.index.link_planned('one-window','correspondence',slot='cp-one',next_movement='start')
        self.index.bind_planned('one-window','correspondence',slot='cp-one',job_id='cp30-job',
                                 worker_id='finite-correspondence-integrated',version_id='wrong-version')
        with self.assertRaisesRegex(ValueError,'edition changed'):
            run_exact_linked_job(self.index,'one-window','correspondence','cp-one','cp30-job',
                                 self.good_view,lambda *_:self.fail('must not dispatch'))

    def test_recovered_history(self):
        self.index.link_planned('one-window','game',next_movement='W13')
        replay=CoordinatorIndex(self.journal)
        self.assertEqual(replay.definition('one-window')[1]['game'][0]['next_movement'],'W13')
        self.assertEqual(self.journal.read_bytes(),self.journal.read_bytes())

    def test_markdown_is_one_handoff_and_not_scheduler(self):
        txt=markdown_handoff(one_window_status(self.index,'one-window',self.good_view))
        self.assertIn('Single-window return packet',txt)
        self.assertIn('game',txt)
        self.assertIn('correspondence',txt)
        self.assertIn('nih',txt)
        self.assertIn('no worker was started',txt)

    def test_all_lanes_must_be_freshly_reverified(self):
        self.index.link_runtime('one-window','game',job_id='game-1',worker_id='game-engine',version_id='w13')
        self.index.link_runtime('one-window','correspondence',job_id='cp30-job',worker_id='finite-correspondence-integrated',version_id='cp30-original')
        self.index.link_runtime('one-window','nih',job_id='nih-1',worker_id='nih-temporal',version_id='w02')
        jobs=[dict(self.good_view['jobs'][0],job_id=jid,worker_id=wid,version_id=ver,
                   verification='natively-reverified') for jid,wid,ver in [('game-1','game-engine','w13'),('cp30-job','finite-correspondence-integrated','cp30-original'),('nih-1','nih-temporal','w02')]]
        self.assertTrue(one_window_status(self.index,'one-window',{'jobs':jobs})['complete'])
        jobs[2]['verification']='recorded-not-reverified'
        self.assertFalse(one_window_status(self.index,'one-window',{'jobs':jobs})['complete'])


if __name__=='__main__':unittest.main()