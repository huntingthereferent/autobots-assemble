"""Focused component tests; comparison and closure admission are simulated."""
import unittest
from runtime.activation import ActivationRegistry, ActivationRoute
from runtime.engine import HandoffRuntime
from runtime.handoff import EvidenceRecord, ExecutionResult
from runtime.agent_lineage import AgentLineage, AgentMove


def witness(kind="simulation"):
    return EvidenceRecord(condition="movement witness", kind=kind,
                          source="simulated-comparison", ref="SIM-1", depth="simulated")


def ab_move(next_ref="", *, closes=(), closure_ref="", closure_evidence=(), status="COMPLETE", output=None):
    return AgentMove(
        result=ExecutionResult(status=status, output=output or {},
                               evidence=(witness(),) if status=="COMPLETE" else ()),
        next_referent=next_ref, closes=closes, closure_evidence=closure_evidence,
        closure_birth_referent=closure_ref,
    )


def routes():
    return ActivationRegistry((
        ActivationRoute("ACT-TEST",("begin comparison",),"test-operator", "R0","agent_lineage"),
        ActivationRoute("ACT-OTHER",("ohayo",),"james", "James / current day","day_attention"),
    ))


class LineageTests(unittest.TestCase):
    def test_one_agent_born_per_explicit_activation_instance(self):
        runtime=HandoffRuntime()
        lineage=AgentLineage(runtime,routes(),evaluate=lambda h,s: ab_move(),max_births=6)
        self.assertIsNone(lineage.activate("ohayo",actor_id="james",instance_id="1"))
        self.assertIsNone(lineage.activate("begin comparison",actor_id="anyone",instance_id="1"))
        self.assertEqual(len(runtime._handoffs),0)
        root=lineage.activate("begin comparison",actor_id="test-operator",instance_id="1")
        self.assertEqual(lineage.activate("begin comparison",actor_id="test-operator",instance_id="1"),root)
        self.assertEqual(len(runtime._handoffs),1)
        self.assertEqual(runtime.state(root).status,"READY")

    def test_three_generations_close_first_and_closure_bears_fourth(self):
        runtime=HandoffRuntime()
        def evaluator(h,s):
            gen=h.metadata['generation']
            if gen==1:return ab_move('R1',output={'result':'first comparison'})
            if gen==2:return ab_move('R2',output={'result':'second comparison'})
            if gen==3:return ab_move(closes=(root,),closure_ref='closure raised new referent', closure_evidence=(EvidenceRecord(condition='ancestor closure',kind='simulation',source='simulated-closure',ref='SIM-1',depth='simulated'),), output={'result':'third comparison'})
            return ab_move(output={'result':'closure born compared'})
        def admit(agent,ancestor,evidence):
            return agent.metadata['generation']==3 and ancestor.handoff_id==root and any(e.ref=='SIM-1' for e in evidence)
        lineage=AgentLineage(runtime,routes(),evaluate=evaluator,admit_closure=admit)
        root=lineage.activate("begin comparison",actor_id="test-operator",instance_id="proof")
        trace=lineage.run_until_idle(root)
        agents=lineage._members(root)
        self.assertEqual(len(agents),4)
        self.assertEqual([a.metadata['generation'] for a in agents],[1,2,3,4])
        self.assertEqual(agents[-1].metadata['birth_reason'],'closure')
        self.assertEqual([runtime.state(a.handoff_id).status for a in agents],['COMPLETE']*4)
        self.assertEqual(lineage.loop_status(root),'CLOSED')
        self.assertEqual(lineage.loop_status(agents[1].handoff_id),'OPEN')
        self.assertTrue(any(root in s.closed for s in trace))
        self.assertEqual(len([e for e in runtime.event_store.for_handoff(root) if e.event_type=='AGENT_LOOP_CLOSED']),1)
        self.assertEqual(lineage.run_until_idle(root),())
        self.assertEqual(len(lineage._members(root)),4)

    def test_invalid_closure_never_creates_closure_child(self):
        runtime=HandoffRuntime()
        def evaluator(h,s):
            if h.metadata['generation']==1:return ab_move('R1')
            return ab_move(closes=(root,),closure_ref='not admitted',closure_evidence=(EvidenceRecord(condition='ancestor closure',kind='simulation',source='claim'),))
        lineage=AgentLineage(runtime,routes(),evaluate=evaluator,admit_closure=lambda a,t,e:False)
        root=lineage.activate('begin comparison',actor_id='test-operator',instance_id='rejected')
        lineage.run_until_idle(root)
        self.assertEqual(len(lineage._members(root)),2)
        self.assertEqual(lineage.loop_status(root),'OPEN')

    def test_same_input_cycles_do_not_spawn_forever(self):
        runtime=HandoffRuntime()
        lineage=AgentLineage(runtime,routes(),evaluate=lambda h,s:ab_move('R0',output={'unchanged':True}))
        root=lineage.activate('begin comparison',actor_id='test-operator',instance_id='cycle')
        lineage.run_until_idle(root)
        self.assertEqual(len(lineage._members(root)),2)

    def test_missing_evidence_rejects_complete_without_children(self):
        runtime=HandoffRuntime()
        lineage=AgentLineage(runtime,routes(),evaluate=lambda h,s:AgentMove(
            ExecutionResult(status='COMPLETE',output={'claim':'unwitnessed'}),next_referent='R1'))
        root=lineage.activate('begin comparison',actor_id='test-operator',instance_id='missing')
        with self.assertRaisesRegex(ValueError,'movement witness'):
            lineage.step(root)
        self.assertEqual(len(lineage._members(root)),1)
        self.assertEqual(runtime.state(root).status,'READY')

    def test_wall_preserved_and_not_mistaken_for_closure(self):
        runtime=HandoffRuntime()
        lineage=AgentLineage(runtime,routes(),evaluate=lambda h,s:ab_move('should not spawn',status='BLOCKED'),max_births=5)
        root=lineage.activate('begin comparison',actor_id='test-operator',instance_id='blocked')
        trace=lineage.run_until_idle(root)
        self.assertEqual(len(trace),1)
        self.assertEqual(runtime.state(root).status,'BLOCKED')
        self.assertEqual(lineage.loop_status(root),'OPEN')
        self.assertEqual(len(lineage._members(root)),1)

    def test_branch_cap_preserves_finished_work(self):
        runtime=HandoffRuntime()
        lineage=AgentLineage(runtime,routes(),evaluate=lambda h,s:ab_move('R'+str(h.metadata['generation'])),max_births=3)
        root=lineage.activate('begin comparison',actor_id='test-operator',instance_id='cap')
        lineage.run_until_idle(root)
        self.assertEqual(len(lineage._members(root)),3)
        self.assertTrue(all(runtime.state(a.handoff_id).status=='COMPLETE' for a in lineage._members(root)))

    def test_cannot_close_unrelated_lineage(self):
        runtime=HandoffRuntime()
        stranger=None
        def evaluator(h,s):
            if h.metadata['generation']==1:return ab_move('child')
            return ab_move(closes=(stranger,),closure_ref='cross',closure_evidence=(EvidenceRecord(condition='ancestor closure',kind='simulation',source='claim'),))
        lineage=AgentLineage(runtime,routes(),evaluate=evaluator,admit_closure=lambda a,t,e:True)
        stranger=lineage.activate('begin comparison',actor_id='test-operator',instance_id='stranger')
        root=lineage.activate('begin comparison',actor_id='test-operator',instance_id='target')
        lineage.run_until_idle(root)
        self.assertEqual(lineage.loop_status(stranger),'OPEN')
        self.assertEqual(len(lineage._members(root)),2)

    def test_closure_claim_without_distinct_evidence_cannot_close(self):
        runtime=HandoffRuntime()
        def evaluator(h,s):
            if h.metadata['generation']==1:return ab_move('R1')
            return ab_move(closes=(root,),closure_ref='unproven closure')
        lineage=AgentLineage(runtime,routes(),evaluate=evaluator,admit_closure=lambda a,t,e:True)
        root=lineage.activate('begin comparison',actor_id='test-operator',instance_id='no-proof')
        lineage.run_until_idle(root)
        self.assertEqual(lineage.loop_status(root),'OPEN')
        self.assertEqual(len(lineage._members(root)),2)

    def test_retry_after_closure_event_but_before_child_birth(self):
        runtime=HandoffRuntime()
        def evaluator(h,s):
            if h.metadata['generation']==1:return ab_move('R1')
            return ab_move(closes=(root,),closure_ref='new research',
                closure_evidence=(EvidenceRecord(condition='ancestor closure',kind='simulation',source='synthetic',ref='OK'),))
        lineage=AgentLineage(runtime,routes(),evaluate=evaluator,admit_closure=lambda a,t,e:True)
        root=lineage.activate('begin comparison',actor_id='test-operator',instance_id='replay')
        original_spawn=runtime.spawn
        def interrupted(*args,**kwargs):
            raise OSError('simulated crash before child submission')
        # First pass creates generation two; then failure occurs after closure.
        lineage.step(root)
        runtime.spawn=interrupted
        with self.assertRaisesRegex(OSError,'simulated crash'):
            lineage.step(root)
        self.assertEqual(lineage.loop_status(root),'CLOSED')
        runtime.spawn=original_spawn
        lineage.run_until_idle(root)
        self.assertEqual(len([a for a in lineage._members(root) if a.metadata['birth_reason']=='closure']),1)
        self.assertEqual(len([e for e in runtime.event_store.for_handoff(root) if e.event_type=='AGENT_LOOP_CLOSED']),1)

if __name__=='__main__':unittest.main()
