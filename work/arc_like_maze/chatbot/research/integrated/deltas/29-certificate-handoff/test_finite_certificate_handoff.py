import unittest
from dataclasses import replace
from finite_certificate_handoff import issue,accept,fixture_handoff,FiniteReceipt
from finite_shared_route_certificate import Task

class FiniteHandoffTests(unittest.TestCase):
    def setUp(self):
        self.r,self.t,self.l,self.p=fixture_handoff()
        self.token=issue(self.r,self.l,self.p)
    def run_case(self,**kw):
        r=kw.get('route',self.r);t=kw.get('tasks',self.t)
        l=kw.get('law',self.l);before=kw.get('before',self.p);after=kw.get('after',self.p)
        token=kw.get('receipt',self.token)
        return accept(token,r,t,l,before,after)
    def test_roundtrip(self):
        res=self.run_case()
        self.assertEqual(res.status,'HANDOFF_FRESHLY_REVALIDATED')
        self.assertEqual(res.fresh_audits,1)
        self.assertEqual([s for n,s in res.tasks],['TASK_COMPLETED_ON_SELECTED_ROUTE']*2)
    def test_prior_untrusted_receipt_is_not_one_pass_proof(self):
        self.assertEqual(self.run_case().fresh_audits,1)
    def test_unproved_task_independent(self):
        t=dict(self.t);t['bad']=Task('left','left-pinned',(('r0','B'),))
        out=self.run_case(tasks=t)
        self.assertEqual(dict(out.tasks)['bad'],'ROUTE_TASK_REQUIREMENTS_UNPROVED')
        self.assertEqual(dict(out.tasks)['a'],'TASK_COMPLETED_ON_SELECTED_ROUTE')
    def test_task_route_mismatch_is_individual(self):
        t=dict(self.t);t['bad']=Task('right','right-pinned',(('s0','B'),))
        self.assertEqual(dict(self.run_case(tasks=t).tasks)['bad'],'HANDOFF_ROUTE_MISMATCH')
    def test_pin_revoked(self):
        before=dict(self.p);before['left_middle']='v2'
        self.assertEqual(self.run_case(before=before,after=before).status,'HANDOFF_REAUDIT_UNPROVED')
    def test_pin_changed_during_audit(self):
        after=dict(self.p);after['left_middle']='v2'
        self.assertEqual(self.run_case(after=after).status,'SOURCE_MOVED_DURING_HANDOFF')
    def test_missing_law(self):
        self.assertEqual(self.run_case(law=(('s0','B'),)).status,'HANDOFF_REAUDIT_UNPROVED')
    def test_different_fingerprint(self):
        r=replace(self.r,fingerprint='new')
        self.assertEqual(self.run_case(route=r).status,'HANDOFF_ROUTE_MISMATCH')
    def test_forged_old_edges_digest(self):
        token=replace(self.token,edges_digest='0'*64)
        self.assertEqual(self.run_case(receipt=token).status,'HANDOFF_EVIDENCE_CHANGED')
    def test_pinned_source_object_changed(self):
        r=replace(self.r,pins=(('donor','v1'),('left_middle','v2'),('final','v1')))
        p=dict(self.p);p['left_middle']='v2'
        self.assertEqual(self.run_case(route=r,before=p,after=p).status,'HANDOFF_EVIDENCE_CHANGED')
    def test_admitted_edges_changed(self):
        r=replace(self.r,admitted=(('s0','B'),))
        self.assertEqual(self.run_case(route=r).status,'HANDOFF_EVIDENCE_CHANGED')
    def test_sender_revoked_wont_issue(self):
        p=dict(self.p);p['donor']='v2'
        self.assertIsNone(issue(self.r,self.l,p))
    def test_sender_invalid_law_wont_issue(self):
        self.assertIsNone(issue(self.r,(),self.p))
    def test_invalid_older_task_fails(self):
        t={'bad':Task('left','left-pinned',())}
        with self.assertRaises(ValueError):self.run_case(tasks=t)
    def test_invalid_receipt_type_fails(self):
        with self.assertRaises(ValueError):self.run_case(receipt={'route':'left'})
    def test_reissues_after_new_pin(self):
        r=replace(self.r,pins=(('donor','v2'),('left_middle','v1'),('final','v1')))
        p=dict(self.p);p['donor']='v2'
        new=issue(r,self.l,p)
        self.assertIsNotNone(new)
        self.assertEqual(self.run_case(route=r,before=p,after=p,receipt=new).status,'HANDOFF_FRESHLY_REVALIDATED')

if __name__=='__main__':unittest.main()
