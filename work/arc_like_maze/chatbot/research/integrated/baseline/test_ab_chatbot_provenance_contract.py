"""Proof-of-source obligations stay separate from finite equation witnesses."""
import copy
import unittest
from ab_chatbot_provenance_contract import (ProvenanceTaskSession,read_provenance_task,LOCAL)
from test_ab_chatbot_mixed_obligations import TASK,completed
import test_ab_chatbot_evidence_prefilter as fixture

BOTH={**TASK,'required_provenance':{'old':LOCAL,'new':LOCAL}}

class ProvenanceContractTests(unittest.TestCase):
    def make(self, **kwargs):
        fx=fixture.EvidencePrefilterTests()
        self.addCleanup(fx.doCleanups)
        return fx.make(**kwargs)

    def test_intake_keeps_requested_source_side_and_task_fingerprint(self):
        i=read_provenance_task(BOTH)
        self.assertEqual(i.status,'TASK_ACCEPTED')
        self.assertEqual([r.side for r in i.contract.required],['old','new'])
        reverse=copy.deepcopy(BOTH)
        reverse['required_paths'].reverse()
        reverse['required_destinations'].reverse()
        reverse['required_provenance']={'new':LOCAL,'old':LOCAL}
        self.assertEqual(i.contract.fingerprint,read_provenance_task(reverse).contract.fingerprint)
        other={**TASK,'required_provenance':{'old':LOCAL}}
        self.assertNotEqual(i.contract.fingerprint,read_provenance_task(other).contract.fingerprint)
        self.assertIn('required_provenance',i.contract.original_input)

    def test_math_plus_both_source_proofs_in_same_result(self):
        old,new=self.make()
        session=ProvenanceTaskSession(old,new,BOTH,**fixture.OPTIONS)
        for _ in range(48):
            r=session.advance()
            if r.status not in ('SEARCHING','EVALUATING'): break
        self.assertEqual(r.status,'GOALS_CARRIED_WITNESSED')
        self.assertEqual(len(r.base_outcome.report.selected.carried),2)
        self.assertTrue(all(x.satisfied for x in r.source_proofs))
        self.assertEqual([x.side for x in r.source_proofs],['old','new'])
        self.assertEqual((len(old.snapshot.edges),len(new.snapshot.edges)),(28,18))
        self.assertEqual(session.advance(max_new_edges=0).status,'GOALS_CARRIED_WITNESSED')

    def test_unverified_new_owner_blocks_before_transitions(self):
        old,new=self.make(remote_new=True)
        sess=ProvenanceTaskSession(old,new,BOTH,**fixture.OPTIONS)
        result=sess.advance()
        self.assertEqual(result.status,'PROVENANCE_UNPROVED')
        self.assertIsNone(result.base_outcome)
        self.assertEqual((len(old.snapshot.edges),len(new.snapshot.edges)),(0,0))
        self.assertTrue(result.source_proofs[0].satisfied)
        self.assertFalse(result.source_proofs[1].satisfied)

    def test_one_side_only_cannot_upgrade_remote_claim(self):
        old,new=self.make(remote_new=True)
        task={**TASK,'required_provenance':{'old':LOCAL}}
        sess=ProvenanceTaskSession(old,new,task,**fixture.OPTIONS)
        for _ in range(48):
            r=sess.advance()
            if r.status not in ('SEARCHING','EVALUATING'):break
        self.assertEqual(r.status,'GOALS_CARRIED_REMOTE_REPORTED')
        self.assertEqual(len(r.source_proofs),1)
        self.assertTrue(r.source_proofs[0].satisfied)

    def test_live_binding_removed_revokes_completed_result(self):
        old,new=self.make()
        sess=ProvenanceTaskSession(old,new,BOTH,**fixture.OPTIONS)
        for _ in range(48):
            r=sess.advance()
            if r.status not in ('SEARCHING','EVALUATING'):break
        self.assertEqual(r.status,'GOALS_CARRIED_WITNESSED')
        # Underlying claimed HTTP version and observations are unchanged;
        # only the explicit in-process owner binding is withdrawn.
        new.owner=None
        failed=sess.advance(max_new_edges=0)
        self.assertEqual(failed.status,'PROVENANCE_UNPROVED')
        self.assertIsNone(failed.base_outcome)
        self.assertFalse(failed.source_proofs[1].satisfied)

    def test_revision_change_revokes_even_if_binding_was_local(self):
        old,new=self.make()
        sess=ProvenanceTaskSession(old,new,BOTH,**fixture.OPTIONS)
        sess.advance(max_new_edges=0)
        old.snapshot.revision+=1
        r=sess.advance(max_new_edges=0)
        self.assertEqual(r.status,'UNKNOWN_VERSION')
        self.assertIsNone(r.base_outcome)

    def test_forged_cached_edge_is_still_a_wall(self):
        old,new=self.make()
        sess=ProvenanceTaskSession(old,new,BOTH,**fixture.OPTIONS)
        for _ in range(48):
            r=sess.advance()
            if r.status not in ('SEARCHING','EVALUATING'):break
        self.assertEqual(r.status,'GOALS_CARRIED_WITNESSED')
        old.snapshot.edges[((0,0,0),'A')]=(2,2,2)
        r=sess.advance(max_new_edges=0)
        self.assertEqual(r.status,'WALL_OBSERVATION')
        self.assertIsNone(r.base_outcome.report.selected)

    def test_strict_schema_rejects_unjustified_or_self_claimed_proof(self):
        for claim in ({}, {'old':'REMOTE_ORIGIN_UNVERIFIED'},
                      {'old':'LOCAL_OWNER_VERIFIED','third':'LOCAL_OWNER_VERIFIED'},
                      {'old':True}, {'new':['LOCAL_OWNER_VERIFIED']},'LOCAL_OWNER_VERIFIED'):
            with self.subTest(claim=claim):
                bad=read_provenance_task({**TASK,'required_provenance':claim})
                self.assertEqual(bad.status,'INVALID_TASK')
        bad=read_provenance_task({**TASK,'required_provenance':{'old':LOCAL},'fake':'yes'})
        self.assertEqual(bad.status,'UNSUPPORTED_TASK')

    def test_provenance_only_task_uses_existing_solver(self):
        old,new=self.make()
        task={'goals':[[0,1,1],[0,2,0]],'required_provenance':{'old':LOCAL}}
        session=ProvenanceTaskSession(old,new,task,**fixture.OPTIONS)
        self.assertEqual(session.intake.status,'TASK_ACCEPTED')
        for _ in range(48):
            r=session.advance()
            if r.status not in ('SEARCHING','EVALUATING'):break
        self.assertEqual(r.status,'GOALS_CARRIED_WITNESSED')
        self.assertEqual(len(r.base_outcome.report.selected.carried),2)

    def test_legacy_exact_text_not_changed(self):
        old,new=self.make()
        for text in ('goals: (0,1,1), (0,2,0)',
                     'goals: (0,1,1), (0,2,0); require: edge (0,0,0) B',
                     'goals: (0,1,1), (0,2,0); require: edges (0,0,0) B, (0,1,0) B'):
            with self.subTest(text=text):
                self.assertEqual(read_provenance_task(text).status,'NOT_PROVENANCE')
                s=ProvenanceTaskSession(old,new,text,**fixture.OPTIONS)
                self.assertIsNotNone(s.base)
                self.assertNotEqual(s.advance(max_new_edges=0).status,'PROVENANCE_UNPROVED')

    def test_ambiguous_prose_never_spends_observations(self):
        old,new=self.make()
        sess=ProvenanceTaskSession(old,new,'please use verified sources',**fixture.OPTIONS)
        self.assertEqual(sess.advance().status,'UNKNOWN_TASK')
        self.assertEqual((len(old.snapshot.edges),len(new.snapshot.edges)),(0,0))

    def test_zero_budget_resumes_with_stable_proof(self):
        old,new=self.make()
        sess=ProvenanceTaskSession(old,new,BOTH,**fixture.OPTIONS)
        r=sess.advance(max_new_edges=0)
        self.assertEqual(r.status,'SEARCHING')
        self.assertEqual((len(old.snapshot.edges),len(new.snapshot.edges)),(0,0))
        self.assertTrue(all(c.satisfied for c in r.source_proofs))
        for _ in range(48):
            r=sess.advance()
            if r.status not in ('SEARCHING','EVALUATING'):break
        self.assertEqual(r.status,'GOALS_CARRIED_WITNESSED')


    def test_unrequired_side_loses_local_label_after_binding_withdrawn(self):
        old,new=self.make()
        task={**TASK,'required_provenance':{'old':LOCAL}}
        s=ProvenanceTaskSession(old,new,task,**fixture.OPTIONS)
        for _ in range(48):
            r=s.advance()
            if r.status not in ('SEARCHING','EVALUATING'):break
        self.assertEqual(r.status,'GOALS_CARRIED_WITNESSED')
        new.owner=None
        again=s.advance(max_new_edges=0)
        self.assertEqual(again.status,'GOALS_CARRIED_REMOTE_REPORTED')
        self.assertEqual(len(again.source_proofs),1)
        self.assertTrue(again.source_proofs[0].satisfied)

    def test_remote_initial_origin_not_upgraded_without_new_pin(self):
        old,new=self.make(remote_new=True)
        # The initial remote origin cannot become verified from an asserted
        # label or late owner field; the only permitted route is a new pin.
        s=ProvenanceTaskSession(old,new,{**TASK,'required_provenance':{'new':LOCAL}},**fixture.OPTIONS)
        self.assertEqual(s.advance().status,'PROVENANCE_UNPROVED')
        new.origin_scope='LOCAL_OWNER_VERIFIED'
        self.assertEqual(s.advance().status,'PROVENANCE_UNPROVED')
        self.assertEqual((len(old.snapshot.edges),len(new.snapshot.edges)),(0,0))

if __name__=='__main__': unittest.main()
