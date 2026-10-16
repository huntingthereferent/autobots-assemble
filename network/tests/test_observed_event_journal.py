import tempfile
import unittest
from pathlib import Path

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from runtime.handoff import Handoff, HandoffEvent
from systems.workspace.main_referent_selector import Capability, Witness
from systems.workspace.observed_event_journal import (
    ObservedEventJournal, SourceAdapter, LOCAL_PASS, START, OBSERVED, OPEN, STOP)


class ObservedJournalTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / 'actual-runtime.jsonl'
        self.executed = []
        self.native_receipts = {'receipt://valid': ('ci-native', 'rev1', 'native CI observed')}

    def adapter(self, name='ci-native', edition='rev1', relation='native CI observed',
                raw='receipt://valid', authorized=True):
        cap = Capability(name, edition, (relation,), authorized)
        def exec_(cap):
            self.executed.append(cap.name)
            if raw == 'RAISE':
                raise RuntimeError('actual native error')
            return raw
        def obs(cap, receipt):
            verified = self.native_receipts.get(receipt) == (cap.name, cap.edition, relation)
            return Witness('SUPPORTED' if verified else 'UNKNOWN', cap.edition,
                           (relation,) if verified else (), receipt, verified)
        return SourceAdapter(cap, exec_, obs)

    def make(self, *sources, verifier=None, attempts=8, relation='native CI observed'):
        journal = ObservedEventJournal(self.path, adapters=tuple(sources),
                   verify_local_pass=verifier or (lambda h,e: e.actor_id=='local-test-runner' and e.data.get('suite')=='ok'),
                   max_attempts=attempts)
        rt = HandoffRuntime(event_store=journal)
        if 'fixture-handoff' not in rt._handoffs:
            rt.submit(Handoff(handoff_id='fixture-handoff', referent='B9 source verification',
                              from_actor='test', to_actor='native-source-owner',
                              required_relation=relation))
        return rt, journal

    def local(self, journal, *, actor='local-test-runner', suite='ok'):
        return journal.append(HandoffEvent.create(handoff_id='fixture-handoff',
                           event_type=LOCAL_PASS, actor_id=actor, data={'suite': suite}))

    def test_local_pass_event_automatically_attempts_without_selector_call(self):
        rt,j = self.make(self.adapter())
        self.local(j)
        self.assertEqual(j.projection('fixture-handoff')['state'],'CROSSED')
        self.assertEqual(self.executed,['ci-native'])
        self.assertEqual(rt.state('fixture-handoff').status,'READY')  # not fake Handoff COMPLETE

    def test_rejected_trigger_does_not_execute(self):
        rt,j = self.make(self.adapter())
        self.local(j,actor='impostor')
        self.assertEqual(self.executed,[])
        self.assertEqual(j.projection('fixture-handoff')['state'],'OPEN')
        self.assertEqual(j.for_handoff('fixture-handoff')[-1].data['cause'],'unverified local-result event')

    def test_local_result_is_not_native_receipt(self):
        rt,j = self.make(self.adapter(raw='receipt://not-native'))
        self.local(j)
        self.assertEqual(j.projection('fixture-handoff')['state'],'OPEN')
        self.assertEqual(j.projection('fixture-handoff')['source_evidence'],[])

    def test_real_failure_then_alternative_attempt(self):
        first = self.adapter(name='a-broken',raw='RAISE')
        second = self.adapter(name='ci-native')
        rt,j = self.make(first,second)
        self.local(j)
        self.assertEqual(self.executed,['a-broken','ci-native'])
        self.assertEqual(j.projection('fixture-handoff')['state'],'CROSSED')
        self.assertEqual([e.data['observed'] for e in j.for_handoff('fixture-handoff') if e.event_type==OBSERVED],['ATTEMPT_ERROR','SUPPORTED'])

    def test_multiple_local_passes_do_not_repeat_external_action(self):
        rt,j = self.make(self.adapter())
        self.local(j); self.local(j)
        self.assertEqual(self.executed,['ci-native'])
        self.assertEqual(j.projection('fixture-handoff')['attempts_started'],1)

    def test_unresolved_source_not_retried_on_new_local_pass(self):
        rt,j = self.make(self.adapter(raw='receipt://missing'))
        self.local(j); self.local(j)
        self.assertEqual(self.executed,['ci-native'])
        self.assertEqual(j.projection('fixture-handoff')['state'],'OPEN')

    def test_no_unauthorized_execution(self):
        rt,j = self.make(self.adapter(authorized=False))
        self.local(j)
        self.assertEqual(self.executed,[])
        self.assertEqual(j.projection('fixture-handoff')['state'],'OPEN')

    def test_no_candidate_relation_match(self):
        rt,j = self.make(self.adapter(relation='different output'))
        self.local(j)
        self.assertEqual(self.executed,[])

    def test_persists_source_observation_on_restart_without_reexecuting(self):
        rt,j = self.make(self.adapter())
        self.local(j)
        rt2,j2 = self.make(self.adapter())
        self.assertEqual(j2.projection('fixture-handoff')['state'],'CROSSED')
        self.local(j2)
        self.assertEqual(self.executed,['ci-native'])

    def test_started_unobserved_native_action_requires_reconciliation(self):
        rt,j = self.make(self.adapter())
        RuntimeJournal.append(j, HandoffEvent.create(handoff_id='fixture-handoff', event_type=START,
                    actor_id='observed-continuation',data={'name':'ci-native','edition':'rev1'}))
        rt2,j2=self.make(self.adapter())
        self.local(j2)
        self.assertEqual(self.executed,[])
        self.assertEqual(j2.projection('fixture-handoff')['state'],'RECOVERY_REQUIRED')
        self.assertEqual(j2.for_handoff('fixture-handoff')[-1].event_type,STOP)

    def test_restart_recovers_durable_pass_without_started_attempt(self):
        _, j = self.make(self.adapter())
        persisted = HandoffEvent.create(handoff_id='fixture-handoff',
            event_type=LOCAL_PASS, actor_id='local-test-runner', data={'suite':'ok'})
        # Crash window: durable journal write committed, hook never entered.
        RuntimeJournal.append(j, persisted)
        self.assertEqual(self.executed, [])
        _, reopened = self.make(self.adapter())
        self.assertEqual(self.executed, ['ci-native'])
        self.assertEqual(reopened.projection('fixture-handoff')['state'], 'CROSSED')
        self.assertEqual(len(reopened.recover_pending()), 0)
        _, reopened_again = self.make(self.adapter())
        self.assertEqual(self.executed, ['ci-native'])
        self.assertEqual(reopened_again.projection('fixture-handoff')['state'], 'CROSSED')

    def test_restart_does_not_replay_interrupted_external_action(self):
        _, j = self.make(self.adapter())
        persisted = HandoffEvent.create(handoff_id='fixture-handoff',
            event_type=LOCAL_PASS, actor_id='local-test-runner', data={'suite':'ok'})
        RuntimeJournal.append(j, persisted)
        RuntimeJournal.append(j, HandoffEvent.create(
            handoff_id='fixture-handoff',event_type=START,actor_id='observed-continuation',
            data={'name':'ci-native','edition':'rev1', 'trigger_id': persisted.event_id}))
        _, reopened = self.make(self.adapter())
        self.assertEqual(self.executed, [])
        self.assertEqual(reopened.projection('fixture-handoff')['state'], 'RECOVERY_REQUIRED')

    def test_restart_rejects_unverified_durable_pass(self):
        _, j = self.make(self.adapter())
        persisted = HandoffEvent.create(handoff_id='fixture-handoff',
            event_type=LOCAL_PASS, actor_id='impostor', data={'suite':'ok'})
        RuntimeJournal.append(j, persisted)
        _, reopened = self.make(self.adapter())
        self.assertEqual(self.executed, [])
        self.assertEqual(reopened.projection('fixture-handoff')['state'], 'OPEN')
        self.assertEqual(reopened.for_handoff('fixture-handoff')[-1].event_type, OPEN)
        _, reopened_again = self.make(self.adapter())
        self.assertEqual(self.executed, [])
        self.assertEqual(sum(e.event_type==OPEN for e in reopened_again.for_handoff('fixture-handoff')),1)

    def test_attempt_bound_keeps_remaining_open(self):
        rt,j = self.make(self.adapter(name='a-broken',raw='RAISE'), self.adapter(), attempts=1)
        self.local(j)
        self.assertEqual(self.executed,['a-broken'])
        self.assertEqual(j.projection('fixture-handoff')['state'],'OPEN')

    def test_native_mismatch_stays_open(self):
        rt,j = self.make(self.adapter(raw='receipt://unregistered'))
        self.local(j)
        self.assertEqual(j.projection('fixture-handoff')['state'],'OPEN')

    def test_duplicate_capability_source_edition_refused(self):
        a=self.adapter()
        with self.assertRaises(ValueError):
            self.make(a,a)

    def test_duplicated_event_identity_refused(self):
        rt,j = self.make()
        e=HandoffEvent.create(handoff_id='fixture-handoff',event_type='UNRELATED',actor_id='fixture')
        j.append(e)
        with self.assertRaises(ValueError):
            j.append(e)

    def test_external_forged_success_is_rejected(self):
        rt,j = self.make(self.adapter())
        e=HandoffEvent.create(handoff_id='fixture-handoff', event_type=OBSERVED,
            actor_id='forger', data={'name':'ci-native','edition':'rev1',
            'relations_admitted':['native CI observed']})
        with self.assertRaises(ValueError):
            j.append(e)
        self.assertEqual(j.projection('fixture-handoff')['state'], 'OPEN')

    def test_failed_local_verifier_does_not_allow_source_execution(self):
        rt,j = self.make(self.adapter(), verifier=lambda h,e: (_ for _ in ()).throw(RuntimeError('bad local receipt')))
        self.local(j)
        self.assertEqual(self.executed, [])
        self.assertEqual(j.projection('fixture-handoff')['state'], 'OPEN')

    def test_unrelated_event_does_not_trigger(self):
        rt,j = self.make(self.adapter())
        j.append(HandoffEvent.create(handoff_id='fixture-handoff',event_type='RESULT_NOT_LOCAL_PASS',actor_id='fixture'))
        self.assertEqual(self.executed,[])

    def test_native_observer_raises_and_next_provider_is_tried(self):
        first_cap=Capability('a','rev1',('native CI observed',),True)
        broken=SourceAdapter(first_cap,lambda cap:'raw',lambda cap,raw:(_ for _ in ()).throw(OSError('source unreachable')))
        rt,j=self.make(broken,self.adapter())
        self.local(j)
        self.assertEqual(j.projection('fixture-handoff')['state'],'CROSSED')
        verdicts=[e.data['observed'] for e in j.for_handoff('fixture-handoff') if e.event_type==OBSERVED]
        self.assertEqual(verdicts,['OBSERVATION_ERROR','SUPPORTED'])

    def test_complete_requires_actual_observation_not_success_label(self):
        cap=Capability('ci-native','rev1',('native CI observed',),True)
        f=SourceAdapter(cap,lambda c:'local PASS',lambda c,x:Witness('SUPPORTED',c.edition,c.claims,'',False))
        rt,j=self.make(f)
        self.local(j)
        self.assertEqual(j.projection('fixture-handoff')['state'],'OPEN')


if __name__=='__main__': unittest.main()
