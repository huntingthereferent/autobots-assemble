"""Executable demonstration using separately pinned local snapshot owners."""
import json
from test_ab_chatbot_cross_pin_join import JoinCrossPinTests
from ab_chatbot_cross_pin_join import CrossPinJoin
from ab_chatbot_joint_witness_binding import BoundJointTask,current_digest,JointWitnessTaskComparison

def settle(joint):
    for _ in range(40):
        out=joint.advance(max_new_edges=3)
        if out.status!='SEARCHING':return out
    raise RuntimeError('finite join failed to settle under declared observation cap')

fixture=JoinCrossPinTests()
a,old,new,owner,registry,p,q=fixture.join(('A','BAA'))
sa=settle(a)
b=CrossPinJoin(old,new,{'required_owner_pins':{'old':p.token,'new':q.token},
                  'join_words':['B','ABB']},registry=registry)
sb=settle(b)
observation_counts=(len(old.snapshot.edges),len(new.snapshot.edges))

def run(edges):
    contract={'required_edges':[{'state':list(s),'action':action} for s,action in edges]}
    x=BoundJointTask(a,{'witness_fingerprint':current_digest(a),**contract})
    y=BoundJointTask(b,{'witness_fingerprint':current_digest(b),**contract})
    report=JointWitnessTaskComparison((('join_A_BAA',x),('join_B_ABB',y))).advance()
    return {'status':report.status,'completed_by':report.completed_by,
            'candidates':[{'label':r.label,'status':r.status,'admitted':r.admitted_obligations,
                           'required':r.total_obligations,'expected_digest':r.expected_digest,
                           'observed_digest':r.observed_digest} for r in report.candidates]}

result={'baseline':{'first_join':{'status':sa.status,'states':len(sa.state_pairs),'edges':len(sa.admitted_edges)},
                     'second_join':{'status':sb.status,'states':len(sb.state_pairs),'edges':len(sb.admitted_edges)}},
        'one_completed':run((((1,1,0),'A'),)),
        'not_combined':run((((1,1,0),'A'),((1,0,0),'B'))),
        'old_new_owner_observations_before_task':observation_counts,
        'old_new_owner_observations_after_task':(len(old.snapshot.edges),len(new.snapshot.edges))}
assert result['one_completed']['status']=='TASK_COMPLETED_BY_INDEPENDENT_WITNESS'
assert result['not_combined']['status']=='TASK_UNPROVED_ACROSS_TESTED_WITNESSES'
assert result['old_new_owner_observations_before_task']==result['old_new_owner_observations_after_task']
with open('JOINT_WITNESS_BINDING_RESULTS.json','w') as stream:
    json.dump(result,stream,indent=2)
print(json.dumps(result,indent=2))
