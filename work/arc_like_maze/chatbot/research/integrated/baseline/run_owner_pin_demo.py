"""Runnable, locally owned evidence referent demo; not a remote attestation."""
import json
from ab_chatbot_owner_pin_contract import OwnerPinRegistry,ExactOwnerTaskSession
from ab_chatbot_language_bridge import LanguageBridge
from test_ab_chatbot_mixed_obligations import TASK
from test_ab_chatbot_evidence_prefilter import EvidencePrefilterTests,OPTIONS

def run():
    fixture=EvidencePrefilterTests()
    try:
        old,new=fixture.make()
        registry=OwnerPinRegistry()
        old_pin=registry.issue(old)
        new_pin=registry.issue(new)
        raw={**TASK,'required_owner_pins':{'old':old_pin.token,'new':new_pin.token}}
        session=ExactOwnerTaskSession(old,new,raw,registry=registry,**OPTIONS)
        for _ in range(48):
            before=session.advance()
            if before.status not in ('SEARCHING','EVALUATING'):
                break
        assert before.status=='GOALS_CARRIED_WITNESSED'
        counts=(len(old.snapshot.edges),len(new.snapshot.edges))
        history=(old_pin.revision,old_pin.digest)
        # A new snapshot over the same owner is a new referent, not the old pin.
        reentered=LanguageBridge(old.remote,owner=old.owner,edge_budget=54)
        rejected=ExactOwnerTaskSession(reentered,new,raw,registry=registry,**OPTIONS).advance()
        assert rejected.status=='OWNER_PIN_UNPROVED'
        updated=registry.issue(reentered,predecessor=old_pin.token)
        raw2={**TASK,'required_owner_pins':{'old':updated.token,'new':new_pin.token}}
        new_task=ExactOwnerTaskSession(reentered,new,raw2,registry=registry,**OPTIONS)
        fresh=new_task.advance(max_new_edges=0)
        assert fresh.status=='SEARCHING'
        return dict(initial_status=before.status,initial_edges=counts,
                    previous_version={'revision':history[0],'digest':history[1]},
                    inherited_old_pin_status=rejected.status,
                    re_pinned_status=fresh.status,new_pin_has_predecessor=True,
                    fresh_old_observations=len(reentered.snapshot.edges),
                    historic_old_observations=len(old.snapshot.edges),
                    repeated_pin_token=False,
                    note='Local identity/revision bookkeeping only; no remote-origin authentication.')
    finally:
        fixture.doCleanups()

if __name__=='__main__':print(json.dumps(run(),indent=2))
