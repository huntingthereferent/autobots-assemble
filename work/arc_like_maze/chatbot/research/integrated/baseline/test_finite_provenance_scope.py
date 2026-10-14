"""Independent pure-source-scope controls, not authentication or HTTP CI."""
import unittest
from finite_provenance_scope import (SourceHandle,ProofRequest,
    LOCAL,REMOTE,verified_scope,decide)

class SourceScopeTests(unittest.TestCase):
    def setUp(self):
        self.owner=SourceHandle(1,'a'*64)

    def scope(self,bound,**kwargs):
        options={'owner':self.owner,'bound_owner':bound,'active':True,
                 'claimed_revision':1,'claimed_digest':'a'*64}
        options.update(kwargs)
        return verified_scope(**options)

    def test_verified_local_binding_satisfies_both_sides(self):
        scope=self.scope(self.owner)
        self.assertEqual(scope,LOCAL)
        self.assertEqual(decide(ProofRequest(True,True),scope,scope),'PROVENANCE_ADMITTED')

    def test_matching_remote_self_claim_is_not_owner_identity(self):
        forged=SourceHandle(1,'a'*64)
        self.assertIsNot(forged,self.owner)
        self.assertEqual(self.scope(forged),REMOTE)
        self.assertEqual(decide(ProofRequest(True,True),LOCAL,REMOTE),'PROVENANCE_UNPROVED')
        self.assertEqual(decide(ProofRequest(True,False),LOCAL,REMOTE),'PROVENANCE_ADMITTED')

    def test_stale_or_inactive_binding_not_verified(self):
        self.assertEqual(self.scope(self.owner,active=False),REMOTE)
        self.assertEqual(self.scope(self.owner,claimed_revision=2),REMOTE)
        self.assertEqual(self.scope(self.owner,claimed_digest='b'*64),REMOTE)
        self.assertEqual(self.scope(self.owner,claimed_revision=True),REMOTE)

    def test_no_undeclared_or_improper_scope(self):
        with self.assertRaises(ValueError):decide(ProofRequest(False,False),LOCAL,LOCAL)
        with self.assertRaises(ValueError):decide(ProofRequest(True,False),'TRUSTED_BY_LABEL',REMOTE)

if __name__=='__main__':unittest.main()
