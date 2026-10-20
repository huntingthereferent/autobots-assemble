"""Compatibility tests for evidence-preserving, non-publishing board staging."""
import json
import tempfile
import unittest
from pathlib import Path
from itertools import product
from research.continuity_engine import ContinuityEngine
from research.continuity_board_bridge import stage_checkpoint
from runtime.research_board import load_research_board
from work.arc_like_maze.cyclic_action_engine import CyclicActionEngine
from work.arc_like_maze.window_two import WindowProcess

Z = (0,) * 9
Q0 = tuple(int(v == 2) for u, v in product(range(3), repeat=2))
Q1 = tuple(int(u == 2 and v == 2) for u, v in product(range(3), repeat=2))
D = tuple((2 * v) % 3 for v in Q1)
W9 = WindowProcess(1, (Q0, Z), (Z,))
W27 = WindowProcess(1, (Q0, Q1), (Z,))
W27S = WindowProcess(1, (Q0, D), (Z,))
CARRIER = CyclicActionEngine.fiber(5)
ROOT = Path(__file__).resolve().parents[2] / 'research' / 'questions'

class BoardBridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name) / 'candidate'
        self.initial_bytes = (ROOT / 'freeze-2026-10-09.json').read_bytes()
        self.initial_index_bytes = (ROOT / 'index.json').read_bytes()
        self.before = load_research_board(root=ROOT)
        self.engine = ContinuityEngine()

    def tearDown(self):
        self.assertEqual(self.initial_bytes, (ROOT / 'freeze-2026-10-09.json').read_bytes())
        self.assertEqual(self.initial_index_bytes, (ROOT / 'index.json').read_bytes())

    def stage(self, record, **extra):
        opts = dict(handoff=record.serialize(), question_id='CE-001',
                    question='Are these restricted B-actions conjugate?',
                    source_board_root=ROOT, candidate_directory=self.dir,
                    frozen_date='2026-10-09', expected_question_id=record.question_id)
        opts.update(extra)
        return stage_checkpoint(**opts)

    def test_undocumented_positive_remains_review(self):
        result = self.engine.start_cyclic(W27, W27S, CARRIER, 27)
        proposal = self.stage(result)
        self.assertEqual(proposal.board_status, 'REVIEW')
        board = load_research_board(root=self.dir)
        self.assertEqual(board['questions'][:-1], self.before['questions'])
        self.assertEqual(board['questions'][-1]['engine_status'], 'B_ONLY_CONJUGACY_WITNESSED')
        self.assertEqual(board['questions'][-1]['status'], 'REVIEW')
        self.assertIn('81-state', board['questions'][-1]['scope'])

    def test_locatable_witness_allows_scoped_publication(self):
        result = self.engine.start_cyclic(W27, W27S, CARRIER, 27)
        self.stage(result, witness_url='https://example.org/fixture',
                   witness_label='Test-only published witness fixture',
                   derived_from=('Q-001',))
        row = load_research_board(root=self.dir)['questions'][-1]
        self.assertEqual(row['status'], 'ANSWERED')
        self.assertIn('B-intertwining', row['answer'])
        self.assertIn('A/B untested', row['scope'])
        self.assertEqual(row['derived_from'], ['Q-001'])

    def test_negative_proof_has_explicit_scope(self):
        result = self.engine.start_cyclic(W9, W27, CARRIER, 9)
        self.stage(result, witness_url='https://example.org/fixture')
        row = load_research_board(root=self.dir)['questions'][-1]
        self.assertEqual(row['status'], 'ANSWERED')
        self.assertTrue(row['answer'].startswith('No:'))
        self.assertIn('A/B untested', row['scope'])

    def test_unknown_does_not_promote_with_a_url(self):
        result = self.engine.start_cyclic(W9, W27, CARRIER, 8)
        self.stage(result, witness_url='https://example.org/fixture')
        row = load_research_board(root=self.dir)['questions'][-1]
        self.assertEqual((row['status'],row['answer']), ('UNKNOWN', ''))
        self.assertIn('budget exhausted', row['boundary'])

    def test_replay_precedes_board_construction(self):
        r = self.engine.start_cyclic(W9, W27, CARRIER, 8)
        raw = json.loads(r.serialize())
        raw['snapshots'][0]['payload'] = '{}'
        with self.assertRaises(ValueError):
            self.stage(r, handoff=json.dumps(raw))
        self.assertFalse(self.dir.exists())

    def test_missing_anchored_question_cannot_publish(self):
        r = self.engine.start_cyclic(W9, W27, CARRIER, 9)
        with self.assertRaises(ValueError):
            self.stage(r, expected_question_id='different')
        self.assertFalse(self.dir.exists())

    def test_no_replacement_of_existing_question(self):
        r = self.engine.start_cyclic(W9, W27, CARRIER, 8)
        with self.assertRaises(ValueError):
            self.stage(r, question_id='Q-001')
        self.assertFalse(self.dir.exists())

    def test_invalid_witness_url_rejected(self):
        r = self.engine.start_cyclic(W9, W27, CARRIER, 9)
        with self.assertRaises(ValueError):
            self.stage(r, witness_url='http://example.org/not-secure')
        self.assertFalse(self.dir.exists())

    def test_duplicate_candidate_not_overwritten(self):
        r = self.engine.start_cyclic(W9, W27, CARRIER, 9)
        self.stage(r)
        with self.assertRaises(FileExistsError):
            self.stage(r)

    def test_new_checkpoint_does_not_mutate_freeze(self):
        r = self.engine.start_cyclic(W9, W27, CARRIER, 8)
        self.stage(r)
        current = load_research_board(root=self.dir)
        original = load_research_board(root=self.dir, checkpoint=self.before['checkpoint']['id'])
        self.assertEqual(original['questions'], self.before['questions'])
        self.assertEqual(len(current['questions']), len(self.before['questions']) + 1)

if __name__ == '__main__':
    unittest.main()
