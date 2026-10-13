"""Pure identity model; does not claim actual HTTP authentication."""
import unittest
from finite_owner_pin_identity import Ledger,Snapshot

class FiniteOwnerPinTests(unittest.TestCase):
    def setUp(self):
        self.ledger=Ledger();self.owner=object()
        self.snapshot=Snapshot('same-source',0,'a'*64)
        self.pin=self.ledger.issue_from_verified_local_binding(self.owner,self.snapshot)

    def test_exact_objects_admitted(self):
        self.assertTrue(self.ledger.check(self.pin.token,self.owner,self.snapshot))

    def test_duplicate_claims_different_owner_denied(self):
        self.assertFalse(self.ledger.check(self.pin.token,object(),self.snapshot))
        self.assertFalse(self.ledger.check(self.pin.token,self.owner,self.snapshot))

    def test_same_fields_new_snapshot_revokes_pin(self):
        other=Snapshot('same-source',0,'a'*64)
        self.assertFalse(self.ledger.check(self.pin.token,self.owner,other))
        self.assertFalse(self.ledger.check(self.pin.token,self.owner,self.snapshot))

    def test_explicit_repin_is_new_record_even_if_labels_equal(self):
        self.assertTrue(self.ledger.check(self.pin.token,self.owner,self.snapshot))
        new=Snapshot('same-source',1,'a'*64)
        reissued=self.ledger.issue_from_verified_local_binding(
                self.owner,new,predecessor=self.pin.token)
        self.assertNotEqual(self.pin.token,reissued.token)
        self.assertEqual(reissued.predecessor,self.pin.token)
        self.assertFalse(self.ledger.check(self.pin.token,self.owner,new))
        self.assertTrue(self.ledger.check(reissued.token,self.owner,new))

    def test_unknown_predecessor_and_revocation(self):
        with self.assertRaises(ValueError):
            self.ledger.issue_from_verified_local_binding(self.owner,self.snapshot,
                    predecessor='f'*48)
        self.ledger.revoke(self.pin.token)
        self.assertFalse(self.ledger.check(self.pin.token,self.owner,self.snapshot))

if __name__=='__main__':unittest.main()
