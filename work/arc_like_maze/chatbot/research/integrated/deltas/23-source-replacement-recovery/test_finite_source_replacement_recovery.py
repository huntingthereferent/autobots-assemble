import unittest
from finite_source_replacement_recovery import reassess
from test_finite_two_route_comparison import setup,M1,M2,AL,AR


def run(middle=M1,maps=AL,**kwargs):
    inputs=dict(baseline=setup(),replacement_middle=middle,replacement_maps=maps,
        old_middle_ref='historic-pin-1',replacement_middle_ref='fresh-pin-2',
        old_right_valid=False,left_valid=True)
    inputs.update(kwargs)
    return reassess(**inputs)

class FiniteReplacementTests(unittest.TestCase):
    def test_old_conflict_replaced_by_new_agreement(self):
        r=run()
        self.assertEqual(r.historical.status,'ROUTE_COMPOSED_MAP_CONFLICT')
        self.assertEqual(r.status,'RECOVERY_AGREEMENT_WITNESSED')
        self.assertEqual(r.replacement.status,'ROUTES_AGREE_ON_SELECTED_EDGE')
        self.assertFalse(r.replacement.disagreements)
    def test_new_conflict_kept_as_evidence(self):
        r=run(middle=M2,maps=AR)
        self.assertEqual(r.status,'RECOVERY_CONFLICT_WITNESSED')
        self.assertEqual(len(r.replacement.disagreements),4)
    def test_wrong_map_is_not_recovery(self):
        altered=list(AL)
        altered[3]=(((1,0,0),(1,0,0)),((1,2,0),(1,2,0)))
        r=run(maps=tuple(altered))
        self.assertEqual(r.status,'REPLACEMENT_UNPROVED')
        self.assertEqual(r.replacement.status,'ROUTE_EVIDENCE_UNPROVED')
    def test_old_proof_still_live_requires_no_recovery(self):
        r=run(old_right_valid=True)
        self.assertEqual(r.status,'RECOVERY_NOT_NEEDED')
        self.assertIsNone(r.replacement)
    def test_unaffected_left_missing_blocks_promotion(self):
        r=run(left_valid=False)
        self.assertEqual(r.status,'UNAFFECTED_ROUTE_UNPROVED')
        self.assertIsNone(r.replacement)
    def test_same_source_referent_not_new_evidence(self):
        with self.assertRaises(ValueError):run(replacement_middle_ref='historic-pin-1')
    def test_historical_observations_not_mutated(self):
        a=run()
        b=run(middle=M2,maps=AR)
        self.assertEqual(a.historical,b.historical)
        self.assertNotEqual(a.replacement,b.replacement)
if __name__=='__main__':unittest.main()
