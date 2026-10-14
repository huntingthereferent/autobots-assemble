"""Run pinned historical/live-revision equality comparison with local owners."""
import json
from ab_chatbot_discovered_correspondence import DOMAIN
from ab_chatbot_http_snapshot import SourceOwnedHTTP,LoopbackHTTP,RemoteObserver
from ab_chatbot_language_bridge import LanguageBridge
from ab_chatbot_owner_pin_contract import OwnerPinRegistry
from ab_chatbot_cross_pin_comparison import CrossPinComparison
from ab_chatbot_stability_witness import TransportedLaw

def run():
    owner=SourceOwnedHTTP(TransportedLaw((0,0,0),tuple(DOMAIN)))
    with LoopbackHTTP(owner) as server:
        def observer():return LanguageBridge(RemoteObserver(server.url,bound_loopback=server),owner=owner,edge_budget=54)
        old=observer();reg=OwnerPinRegistry();prior=reg.issue(old)
        owner.replace(TransportedLaw((0,1,2),tuple(DOMAIN)))
        fresh=observer();current=reg.issue(fresh,predecessor=prior.token)
        req={'required_owner_pins':{'old':prior.token,'new':current.token},
             'compare_words':[['','AAA'],['BA','ABB']]}
        agent=CrossPinComparison(old,fresh,req,registry=reg)
        initial=agent.advance(max_new_edges=0)
        for i in range(64):
            report=agent.advance(max_new_edges=2)
            if report.status!='SEARCHING':break
        assert report.status=='RELATION_CHANGED_WITNESSED',report.status
        result={'status':report.status,'old_revision':report.old_version[1],
            'new_revision':report.new_version[1],
            'prior_pin_remains_historical':current.predecessor==prior.token,
            'fresh_initial_observations':0,
            'old_observed':report.old_observed,'new_observed':report.new_observed,
            'relations':[{'words':x.words,'old_equal':x.old_equal,'new_equal':x.new_equal,
               'old_endpoints':[list(p.states[-1]) for p in x.old_paths],
               'new_endpoints':[list(p.states[-1]) for p in x.new_paths]}
                for x in report.comparisons],
            'old_and_new_cache_disjoint':old.snapshot.edges is not fresh.snapshot.edges,
            'zero_new_budget_result':initial.status,
            'status_after_replay':agent.advance(max_new_edges=0).status,
            'scope':'Explicit finite action-word comparison; local in-process source owner only.'}
        assert all((x['old_equal']==x['new_equal'])== (i==0) for i,x in enumerate(result['relations']))
        return result
if __name__=='__main__':print(json.dumps(run(),indent=2))
