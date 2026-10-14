"""Source comparison and gated preference do not transfer proof or schedule work."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import shutil
import unittest

from systems.workspace.promotion import PreferredEditions, compare_editions, preference_view
from systems.workspace.workstation import ProcessWorkstation
from systems.workspace.controls import promote_edition, preferred_versions, compare_versions
from systems.workspace.process_handoff import WORKER_ID as FCP
from systems.workspace.factory_machine_bridge import WORKER_ID as FACTORY
from systems.workspace.controls import admit_finite, run_job
from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal

ROOT = Path(__file__).resolve().parents[2]
INPUT = {"old_phi":[0,0,1],"new_phi":[0,0,0],"candidate_words":[["ABAA","ABBABA"]],"required_state":[0,0,0],"required_action":"B"}


class PreferredEditionTests(unittest.TestCase):
    def setUp(self):
        temp=TemporaryDirectory(); self.addCleanup(temp.cleanup)
        self.root=Path(temp.name); self.data=self.root/'private'
        source=self.root/'source'; source.mkdir()
        for name in ('finite_goal_priority.py','finite_required_edge_guard.py'):
            shutil.copyfile(ROOT/'work/arc_like_maze/chatbot'/name,source/name)
        self.desk=ProcessWorkstation(self.data/'workstation')
        self.desk.copy_source(source,worker_id=FCP,version_id='v1')
        self.desk.branch(worker_id=FCP,parent_version='v1',version_id='v2')
        self.inputs=self.root/'input.json'; self.inputs.write_text(json.dumps(INPUT))
        self.ledger=PreferredEditions(self.data/'preferred_editions.jsonl')

    def job(self,version='v2',job_id='proof-1'):
        admit_finite(data_dir=self.data,version_id=version,inputs_file=self.inputs,
                     job_id=job_id,confirm_admit=job_id,from_actor='tester')
        run_job(data_dir=self.data,job_id=job_id,confirm_execute=job_id)
        return job_id

    def promote(self,version='v2',job_id='proof-1',fingerprint=None):
        fingerprint=fingerprint or self.desk.inspect(worker_id=FCP,version_id=version)['current_fingerprint']
        return promote_edition(data_dir=self.data,worker_id=FCP,version_id=version,
                               supporting_job_id=job_id,confirm_version=version,
                               confirm_fingerprint=fingerprint,actor_id='tester')

    def test_compare_is_hash_based_and_read_only(self):
        before=self.data.joinpath('preferred_editions.jsonl').exists()
        result=compare_versions(data_dir=self.data,worker_id=FCP,left_version='v1',right_version='v2')
        self.assertTrue(result['same_contents']);self.assertFalse(result['tests_transferred'])
        self.assertEqual(before,False)
        target=self.data/'workstation'/FCP/'v2'/'finite_required_edge_guard.py'
        target.write_text(target.read_text()+'\n# only v2\n')
        result=compare_editions(self.desk,worker_id=FCP,left_version='v1',right_version='v2')
        self.assertEqual(result['modified'],['finite_required_edge_guard.py'])
        self.assertFalse(result['same_contents'])
        self.assertEqual((self.data/'workstation'/FCP/'v1'/'finite_required_edge_guard.py').read_text().endswith('# only v2\n'),False)

    def test_unverified_copy_cannot_be_promoted(self):
        with self.assertRaises(KeyError): self.promote()
        self.assertFalse(self.ledger.path.exists())

    def test_ready_job_cannot_support_selection(self):
        admit_finite(data_dir=self.data,version_id='v2',inputs_file=self.inputs,
                    job_id='proof-1',confirm_admit='proof-1',from_actor='tester')
        with self.assertRaises(ValueError): self.promote()
        self.assertFalse(self.ledger.path.exists())

    def test_promotion_uses_native_replay_and_does_not_execute_or_merge(self):
        self.job()
        before=(self.data/'runtime.jsonl').read_bytes()
        output=self.promote()
        self.assertEqual(output['version_id'],'v2')
        self.assertEqual((self.data/'runtime.jsonl').read_bytes(),before)
        self.assertEqual(self.ledger.current()[FCP]['supporting_job_id'],'proof-1')
        self.assertEqual(preference_view(self.ledger,self.desk)[0]['source_state'],'MATCHES_SELECTION')
        self.assertEqual(self.promote()['already_selected'],True)
        self.assertEqual(len(self.ledger.history()),1)
        self.assertFalse((self.data/'workstation'/FCP/'v1'/'_worker_version.json').read_text().find('proof-1')>=0)

    def test_wrong_job_version_and_fingerprint_rejected(self):
        self.job(version='v1')
        with self.assertRaises(ValueError): self.promote('v2')
        with self.assertRaises(PermissionError):
            promote_edition(data_dir=self.data,worker_id=FCP,version_id='v1',
                            supporting_job_id='proof-1',confirm_version='v2',
                            confirm_fingerprint='0'*64,actor_id='tester')
        with self.assertRaises(PermissionError):
            promote_edition(data_dir=self.data,worker_id=FCP,version_id='v1',
                            supporting_job_id='proof-1',confirm_version='v1',
                            confirm_fingerprint='0'*64,actor_id='tester')
        self.assertFalse(self.ledger.path.exists())

    def test_source_change_after_completed_job_fails_promotion(self):
        self.job()
        p=self.data/'workstation'/FCP/'v2'/'finite_required_edge_guard.py'
        p.write_text(p.read_text()+'\n# changed\n')
        with self.assertRaises(ValueError): self.promote()
        self.assertFalse(self.ledger.path.exists())

    def test_stale_selection_stays_visible_and_new_jobs_not_auto_admitted(self):
        self.job(); self.promote()
        p=self.data/'workstation'/FCP/'v2'/'finite_required_edge_guard.py'
        p.write_text(p.read_text()+'\n# edited\n')
        rows=preferred_versions(data_dir=self.data)
        self.assertEqual(rows[0]['source_state'],'SOURCE_CHANGED')
        self.assertEqual(len(HandoffRuntime(event_store=RuntimeJournal(self.data/'runtime.jsonl')).snapshot()),1)

    def test_selection_is_append_only_and_old_witness_not_transferable(self):
        self.job(); self.promote()
        self.job(version='v1',job_id='proof-2')
        fp=self.desk.inspect(worker_id=FCP,version_id='v1')['current_fingerprint']
        promote_edition(data_dir=self.data,worker_id=FCP,version_id='v1',
                        supporting_job_id='proof-2',confirm_version='v1',
                        confirm_fingerprint=fp,actor_id='tester')
        a=self.ledger.history()
        self.assertEqual(len(a),2)
        self.assertEqual(a[1]['previous_event_id'],a[0]['event_id'])
        self.assertEqual(self.ledger.current()[FCP]['version_id'],'v1')

    def test_corrupt_history_is_not_ignored(self):
        self.job()
        self.ledger.path.parent.mkdir(parents=True,exist_ok=True)
        self.ledger.path.write_text('{invalid\n')
        with self.assertRaises(ValueError): preferred_versions(data_dir=self.data)
        with self.assertRaises(ValueError): self.promote()

    def test_cross_worker_evidence_does_not_promote(self):
        self.job()
        factory_source=self.root/'factory'; factory_source.mkdir()
        shutil.copyfile(ROOT/'systems/workspace/factory_machine_worker.py',
                        factory_source/'factory_machine_worker.py')
        self.desk.copy_source(factory_source,worker_id=FACTORY,version_id='v2')
        fp=self.desk.inspect(worker_id=FACTORY,version_id='v2')['current_fingerprint']
        with self.assertRaises(ValueError):
            promote_edition(data_dir=self.data,worker_id=FACTORY,version_id='v2',
                            supporting_job_id='proof-1',confirm_version='v2',
                            confirm_fingerprint=fp,actor_id='tester')

    def test_mismatched_edition_type_compare_rejected(self):
        with self.assertRaises(KeyError):
            compare_versions(data_dir=self.data,worker_id=FACTORY,left_version='v1',right_version='v2')

if __name__=='__main__': unittest.main()
