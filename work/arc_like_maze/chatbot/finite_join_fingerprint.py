"""Independent finite-law reference: digest and consume exact observed joins.

No owner authentication: revision names here are caller-declared context.
"""
from hashlib import sha256
import json
from finite_goal_priority import Law
from finite_cross_pin_join import join
from finite_joint_task_consumer import consume


def witnessed_digest(old, new, words, *, source_id='finite-old-v0', target_id='finite-new-v1'):
    """Hash a fully replayed finite partial relation and explicit source referents."""
    witness=join(old,new,tuple(words))
    if witness.status!='JOINT_PARTIAL_CORRESPONDENCE_WITNESSED':
        return None, witness
    fields={'format':'finite-joined-witness/v1', 'old_phi':old.phi,
            'new_phi':new.phi, 'source_ref':source_id,'target_ref':target_id,
            'words':witness.words, 'pairs':witness.state_pairs,
            'admitted':witness.admitted_edges}
    return sha256(json.dumps(fields,sort_keys=True,separators=(',',':')).encode()).hexdigest(),witness


def compare_task(old, new, task, candidates):
    """Each candidate supplies (label, words, expected_digest); never union results."""
    if (type(candidates) is not tuple or not 2<=len(candidates)<=8 or
            len({row[0] for row in candidates})!=len(candidates)):
        raise ValueError('two to eight independently declared distinct witnesses required')
    results=[]
    for label,words,expected in candidates:
        actual,witness=witnessed_digest(old,new,words)
        if actual is None:
            results.append((label,'JOINT_RELATION_CONFLICT_WITNESSED',0,0,expected,actual))
        elif expected!=actual:
            results.append((label,'WITNESS_FINGERPRINT_MISMATCH',0,0,expected,actual))
        else:
            status,checks,_=consume(old,new,witness,**task)
            results.append((label,status,sum(x[2] for x in checks),len(checks),expected,actual))
    winners=tuple(r[0] for r in results if r[1]=='TASK_COMPLETED_ON_JOINT_WITNESS')
    return ('TASK_COMPLETED_BY_INDEPENDENT_WITNESS' if winners else
            'TASK_UNPROVED_ACROSS_TESTED_WITNESSES',tuple(results),winners)

if __name__=='__main__':
    a,b=Law((0,0,0)),Law((0,1,2))
    words=(('A','BAA'),('B','ABB'))
    options=tuple((str(i),w,witnessed_digest(a,b,w)[0]) for i,w in enumerate(words))
    for task in ({'edges':(((1,1,0),'A'),)},
                 {'edges':(((1,1,0),'A'),((1,0,0),'B'))}):
        print(compare_task(a,b,task,options))
