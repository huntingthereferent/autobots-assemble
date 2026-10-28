import copy
import json
import tempfile
import unittest
from pathlib import Path

from . import cp_record as cp


class CheckpointHarnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'checkpoints').mkdir()
        (self.root / 'PROVENANCE.md').write_text('# Earlier provenance\n\nHistorical CPs remain here.\n', encoding='utf-8')
        self.sample = json.loads((Path(__file__).parent/'CP-0027.json').read_text(encoding='utf-8'))
        cp.record(self.root, self._input(self.sample))

    def _input(self,m):
        target = self.root / f'incoming-{m["cp"]}.json'
        target.write_text(json.dumps(m),encoding='utf-8')
        return target

    def next_cp(self):
        m = copy.deepcopy(self.sample)
        m['cp'] = 28
        m['title'] = 'New pinned observation'
        m['summary'] = 'An independent route was replayed under the selected owner pin.'
        m['record'] = 'NEW_PIN_2026-10-13.md'
        return m

    def test_seed_consistent(self):
        self.assertEqual(cp.check(self.root),1)

    def test_two_views_recorded(self):
        cp.record(self.root,self._input(self.next_cp()))
        self.assertEqual(cp.check(self.root),2)
        self.assertIn('**CP-0028', (self.root/'ABOUT_ME.md').read_text())
        self.assertIn('CP-0027', (self.root/'PROVENANCE.md').read_text())
        self.assertIn('CP-0028', (self.root/'PROVENANCE.md').read_text())

    def test_no_false_automatic_git_push(self):
        self.assertIn('conversation-local',(self.root/'PROVENANCE.md').read_text())
        self.assertNotIn('https://example.com/ab_chatbot_multi_task_dependency', (self.root/'PROVENANCE.md').read_text())

    def test_historical_provenance_prefix_preserved(self):
        cp.record(self.root,self._input(self.next_cp()))
        self.assertTrue((self.root/'PROVENANCE.md').read_text().startswith('# Earlier provenance\n\nHistorical CPs remain here.\n'))

    def test_repeated_same_cp_is_idempotent(self):
        old = (self.root/'PROVENANCE.md').read_bytes()
        self.assertEqual(cp.record(self.root,self._input(self.sample)),'already-recorded')
        self.assertEqual(old,(self.root/'PROVENANCE.md').read_bytes())

    def test_conflicting_same_cp_fails(self):
        m=copy.deepcopy(self.sample);m['summary']='Different assertion'
        with self.assertRaises(cp.CheckpointError):cp.record(self.root,self._input(m))
        self.assertEqual(cp.check(self.root),1)

    def test_gap_fails_without_mutation(self):
        m=self.next_cp();m['cp']=29
        with self.assertRaises(cp.CheckpointError):cp.record(self.root,self._input(m))
        self.assertFalse((self.root/'checkpoints'/'CP-0029.json').exists())
        self.assertEqual(cp.check(self.root),1)

    def test_overlong_public_text_fails(self):
        m=self.next_cp();m['summary']='a' * 501
        with self.assertRaises(cp.CheckpointError):cp.record(self.root,self._input(m))
        self.assertEqual(cp.check(self.root),1)

    def test_bad_sha_fails(self):
        m=self.next_cp();m['archive']['sha256']='123'
        with self.assertRaises(cp.CheckpointError):cp.record(self.root,self._input(m))
        self.assertEqual(cp.check(self.root),1)

    def test_path_escape_fails(self):
        m=self.next_cp();m['record']='../../profile/README.md'
        with self.assertRaises(cp.CheckpointError):cp.record(self.root,self._input(m))

    def test_source_manifest_edit_detected(self):
        f=self.root/'checkpoints'/'CP-0027.json'
        m=json.loads(f.read_text());m['summary']='Changed after witnessing'
        f.write_text(json.dumps(m))
        with self.assertRaises(cp.CheckpointError):cp.check(self.root)

    def test_about_edit_detected(self):
        f=self.root/'ABOUT_ME.md';f.write_text(f.read_text()+'Oops\n')
        with self.assertRaises(cp.CheckpointError):cp.check(self.root)

    def test_provenance_edit_detected(self):
        f=self.root/'PROVENANCE.md';f.write_text(f.read_text().replace('CP-0027','CP-9999'))
        with self.assertRaises(cp.CheckpointError):cp.check(self.root)

    def test_markers_corruption_detected(self):
        f=self.root/'PROVENANCE.md';f.write_text(f.read_text().replace(cp.END,''))
        with self.assertRaises(cp.CheckpointError):cp.check(self.root)
        with self.assertRaises(cp.CheckpointError):cp.sync(self.root)

    def test_refresh_preserves_hist_and_rebuilds_both(self):
        f=self.root/'ABOUT_ME.md';f.write_text('bad')
        cp.sync(self.root)
        self.assertEqual(cp.check(self.root),1)
        self.assertIn('Historical CPs remain here.',(self.root/'PROVENANCE.md').read_text())

    def test_research_name_is_application_independent(self):
        about = (self.root/'ABOUT_ME.md').read_text()
        self.assertTrue(about.startswith('# Finite Correspondence Research — About Me\n'))
        self.assertIn('Its subject is evidence-bound correspondence, independent of any particular application.', about)
        self.assertIn('witnessed finite transitions', about)

    def test_no_implicit_claim_of_current_proof(self):
        about=(self.root/'ABOUT_ME.md').read_text()
        self.assertIn('Local test execution is distinct from GitHub CI',about)
        self.assertIn('cached',about)

    def test_invalid_reported_test_count(self):
        m=self.next_cp();m['tests']['passed']=128
        with self.assertRaises(cp.CheckpointError):cp.record(self.root,self._input(m))


    def test_handoff_carries_original_cp_history_without_automatic_work(self):
        cp.record(self.root, self._input(self.next_cp()))
        paths = (self.root/'ABOUT_ME.md', self.root/'PROVENANCE.md',
                 self.root/'checkpoints'/'CP-0027.json',
                 self.root/'checkpoints'/'CP-0028.json')
        before = [p.read_bytes() for p in paths]
        context = cp.continuation(self.root, 'recheck the same selected route')
        self.assertEqual(context['current_referent'], 'recheck the same selected route')
        self.assertEqual(context['latest_checkpoint'], 'CP-0028')
        self.assertEqual(context['schema'], 'finite-correspondence-cp-continuation/v1')
        self.assertEqual([x['cp'] for x in context['history']], ['CP-0027','CP-0028'])
        self.assertEqual(context['history'][0]['preserved'], self.sample['preserved'])
        self.assertEqual(context['history'][1]['boundary'], self.next_cp()['boundary'])
        self.assertFalse(context['task_admitted'])
        self.assertFalse(context['worker_executed'])
        self.assertEqual(context['current_native_verification'], 'NOT_PERFORMED')
        self.assertEqual(before, [p.read_bytes() for p in paths])

    def test_handoff_refuses_missing_referent_and_unsynced_views(self):
        for bad in ('', '  ', None, 'x\ny'):
            with self.subTest(bad=bad):
                with self.assertRaises(cp.CheckpointError):
                    cp.continuation(self.root, bad)
        (self.root/'ABOUT_ME.md').write_text('stale', encoding='utf-8')
        with self.assertRaisesRegex(cp.CheckpointError, 'out of sync'):
            cp.continuation(self.root, 'same current task')

    def test_handoff_does_not_promote_historical_next_to_task(self):
        request = 'inspect missing source evidence before changing anything'
        handoff = cp.continuation(self.root, request)
        self.assertEqual(handoff['current_referent'], request)
        self.assertNotEqual(handoff['current_referent'], self.sample['next'])
        self.assertEqual(handoff['next_possible_not_an_assignment'], self.sample['next'])
        self.assertEqual(handoff['archive_identity']['availability'], 'conversation-local')


if __name__=='__main__':
    unittest.main()
