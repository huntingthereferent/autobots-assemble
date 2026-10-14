"""Live pinned local owner demonstration of consuming a witnessed join."""
import json
from ab_chatbot_cross_pin_join import CrossPinJoin
from ab_chatbot_joint_evidence_task import JointEvidenceTask
from ab_chatbot_discovered_correspondence import DOMAIN
from ab_chatbot_http_snapshot import SourceOwnedHTTP, LoopbackHTTP, RemoteObserver
from ab_chatbot_language_bridge import LanguageBridge
from ab_chatbot_owner_pin_contract import OwnerPinRegistry
from ab_chatbot_stability_witness import TransportedLaw
from finite_goal_priority import Law
from finite_cross_pin_join import join
from finite_joint_task_consumer import consume


def example(words, task_inputs, *, oldlaw=(0,0,0), newlaw=(0,1,2)):
    owner = SourceOwnedHTTP(TransportedLaw(oldlaw, tuple(DOMAIN)))
    with LoopbackHTTP(owner) as server:
        def observe():
            return LanguageBridge(RemoteObserver(server.url, bound_loopback=server),
                                  owner=owner, edge_budget=54)
        old=observe();registry=OwnerPinRegistry();oldpin=registry.issue(old)
        owner.replace(TransportedLaw(newlaw,tuple(DOMAIN)))
        new=observe();newpin=registry.issue(new,predecessor=oldpin.token)
        joint=CrossPinJoin(old,new,{
            'required_owner_pins':{'old':oldpin.token,'new':newpin.token},
            'join_words':list(words)},registry=registry)
        waiting=joint.advance(max_new_edges=0)
        for _ in range(30):
            completed=joint.advance(max_new_edges=2)
            if completed.status!='SEARCHING':break
        else:raise AssertionError('bounded join did not complete')
        reference=join(Law(oldlaw),Law(newlaw),tuple(words))
        assert completed.status==reference.status
        assert (completed.state_pairs,completed.admitted_edges)==(reference.state_pairs,reference.admitted_edges)
        observed_before=(len(old.snapshot.edges),len(new.snapshot.edges))
        answers=[]
        for task_input in task_inputs:
            agent=JointEvidenceTask(joint,task_input)
            result=agent.advance()
            checks=[{'kind':c.kind,'requirement':repr(c.requirement),'admitted':c.admitted,
                     'witness':repr(c.witness)} for c in result.obligations]
            answers.append({'status':result.status,'fingerprint':result.fingerprint,
                            'obligations':checks,'goals_carried':result.goals_carried,
                            'joint_obstruction':repr(result.joint.obstruction) if result.joint.obstruction else None})
        observed_after=(len(old.snapshot.edges),len(new.snapshot.edges))
        assert observed_before==observed_after
        return {'words':words,'first_zero_read_status':waiting.status,
                'joint_status':completed.status,'joint_state_pairs':len(completed.state_pairs),
                'joint_admitted_edges':len(completed.admitted_edges),
                'owner_observations_before_tasks':observed_before,
                'owner_observations_after_tasks':observed_after,
                'extra_observations':sum(observed_after)-sum(observed_before),
                'tasks':answers}


def run():
    good={'goals':[[1,0,0],[2,1,0]],
          'required_edges':[{'state':[0,0,0],'action':'A'},
                            {'state':[1,1,0],'action':'A'}],
          'required_paths':[{'word':'BAA','old_end':[2,1,0],'new_end':[2,1,0]}],
          'required_destinations':[{'source':[1,0,0],'image':[1,0,0]}]}
    missing={'goals':[[1,0,0]],'required_edges':[{'state':[1,0,0],'action':'B'}]}
    missing_path={'goals':[[1,0,0]],'required_paths':[{'word':'AB',
                  'old_end':[1,1,0],'new_end':[1,1,0]}]}
    collision=example(('A','BAB'),[good])
    completed=example(('A','BAA'),[good,missing,missing_path])
    check=consume(Law((0,0,0)),Law((0,1,2)),
                  join(Law((0,0,0)),Law((0,1,2)),('A','BAA')),
                  goals=((1,0,0),(2,1,0)),
                  edges=(((0,0,0),'A'),((1,1,0),'A')),
                  paths=(('BAA',(2,1,0),(2,1,0)),),
                  destinations=(((1,0,0),(1,0,0)),))
    assert completed['tasks'][0]['status']==check[0]
    return {'completed':completed,'collision':collision,
            'independent_finite_reference':check[0],
            'scope':'Already independently pinned and observed partial correspondence; no unobserved edge admitted.'}

if __name__=='__main__':print(json.dumps(run(),indent=2))
