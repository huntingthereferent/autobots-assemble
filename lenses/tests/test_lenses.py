from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from network import Relation, RelationLedger
from lenses import available_lenses, render


class LensTests(unittest.TestCase):
    def test_lenses_are_read_only_projections(self):
        ledger = RelationLedger()
        snap = ledger.append(Relation("x", "status", "ready", "test"))
        before = tuple(r.relation_id for r in snap.relations)

        for lens in available_lenses():
            output = render(snap, lens)
            self.assertIsInstance(output, str)
            self.assertTrue(output)

        after = tuple(r.relation_id for r in snap.relations)
        self.assertEqual(before, after)
        self.assertEqual(ledger.freeze().relations, snap.relations)

    def test_expected_builtin_lenses_exist(self):
        self.assertEqual(set(available_lenses()), {"raw","json","english"})


if __name__ == "__main__":
    unittest.main()
