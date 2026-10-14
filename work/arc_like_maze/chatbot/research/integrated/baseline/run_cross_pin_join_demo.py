"""Reproduce compatible and incompatible joins across independent owner snapshots."""
import json
from ab_chatbot_cross_pin_join import CrossPinJoin
from ab_chatbot_discovered_correspondence import DOMAIN
from ab_chatbot_http_snapshot import SourceOwnedHTTP,LoopbackHTTP,RemoteObserver
from ab_chatbot_language_bridge import LanguageBridge
from ab_chatbot_owner_pin_contract import OwnerPinRegistry
from ab_chatbot_stability_witness import TransportedLaw
from finite_cross_pin_join import join
from finite_goal_priority import Law


def example(oldlaw,newlaw,words):
    owner=SourceOwnedHTTP(TransportedLaw(oldlaw,tuple(DOMAIN)))
    with LoopbackHTTP(owner) as server:
        def observe():
            return LanguageBridge(RemoteObserver(server.url,bound_loopback=server),
                                  owner=owner,edge_budget=54)
        old=observe();registry=OwnerPinRegistry();previous=registry.issue(old)
        owner.replace(TransportedLaw(newlaw,tuple(DOMAIN)))
        new=observe();current=registry.issue(new,predecessor=previous.token)
        agent=CrossPinJoin(old,new,{'required_owner_pins':{'old':previous.token,'new':current.token},
                             'join_words':list(words)},registry=registry)
        initial=agent.advance(max_new_edges=0)
        for attempt in range(32):
            result=agent.advance(max_new_edges=2)
            if result.status!='SEARCHING':break
        ref=join(Law(oldlaw),Law(newlaw),tuple(words))
        assert result.status==ref.status
        assert result.state_pairs==ref.state_pairs
        assert result.admitted_edges==ref.admitted_edges
        if result.obstruction:
            x=result.obstruction
            assert (x.previous_word,x.incoming_word,x.cause)==ref.contradiction[:3]
            witness={'cause':x.cause,'old_words':[x.previous_word,x.incoming_word],
                     'old_endpoints':[list(x.old_endpoints[0]),list(x.old_endpoints[1])],
                     'new_endpoints':[list(x.new_endpoints[0]),list(x.new_endpoints[1])],
                     'old_equal':x.old_equal,'new_equal':x.new_equal}
        else:witness=None
        result_zero=agent.advance(max_new_edges=0)
        assert result_zero.status==result.status
        return {'old_phi':oldlaw,'new_phi':newlaw,'words':words,
                'initial_zero_budget_status':initial.status,
                'status':result.status,'zero_read_replay_status':result_zero.status,
                'old_revision':result.versions[0][1],'new_revision':result.versions[1][1],
                'observed_old':result.old_observed,'observed_new':result.new_observed,
                'state_pairs':len(result.state_pairs),'admitted_edges':len(result.admitted_edges),
                'obstruction':witness,'finite_reference_agrees':True,
                'cache_objects_distinct':old.snapshot.edges is not new.snapshot.edges}


def run():
    return {'compatible':example((0,0,0),(0,1,2),('A','BAA')),
            'source_collision':example((0,0,0),(0,1,2),('A','BAB')),
            'target_collision':example((0,0,1),(0,0,0),('B','ABBABA')),
            'scope':'Finite separately pinned local owner histories, no full conjugacy or off-path edge claims.'}

if __name__=='__main__':print(json.dumps(run(),indent=2))
