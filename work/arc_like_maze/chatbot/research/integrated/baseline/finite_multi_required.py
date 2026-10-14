"""Standalone complete-law verifier for conjunctions of finite required edges.

Unlike snapshot-backed chatbot, full transition laws are given. Rejection is
relative to a candidate's fixed seed mapping and explicitly declared edges.
"""
from finite_goal_priority import Law, ROOT
from finite_required_edge_guard import seed_map

CANDIDATES=(
 ('ABAA','ABBABA'),('ABAA','AAABB','BAAAB'),('ABAA','BAAAB'),
 ('AAABB','BAAAB'),('ABAA','AAABB'),('ABBABA',),
 ('BB','ABAA'),('AAABB',),('BAAAB',),('ABAA',),('BB',)
)

def inspect_all(old, new, words, requirements):
    if not requirements or len(set(requirements))!=len(requirements):
        raise ValueError('explicit distinct edge requirements necessary')
    fwd=seed_map(old,new,words)
    reverse={n:s for s,n in fwd.items()}
    outcomes=[]
    for source, action in requirements:
        if source not in fwd:
            outcomes.append((source,action,'UNDECIDED',None))
            continue
        old_target=old.step(source,action)
        new_target=new.step(fwd[source],action)
        if old_target in fwd and fwd[old_target]!=new_target:
            cause='SOURCE_COLLISION'
        elif new_target in reverse and reverse[new_target]!=old_target:
            cause='TARGET_COLLISION'
        else:
            cause=None
        if cause:
            certificate=(cause,source,action,old_target,fwd[source],new_target,
                         fwd.get(old_target),reverse.get(new_target))
            outcomes.append((source,action,'CONTRADICTED',certificate))
        else:
            outcomes.append((source,action,'NOT_CONTRADICTED',None))
    return tuple(outcomes)

def classify(old, new, candidates, requirements):
    kept=[];rejected=[]
    for words in candidates:
        results=inspect_all(old,new,words,requirements)
        conflicts=tuple(item for item in results if item[2]=='CONTRADICTED')
        if conflicts:
            rejected.append((words,conflicts))
        else:
            kept.append((words,results))
    return tuple(kept),tuple(rejected)

if __name__=='__main__':
    a,b=Law((0,0,1)),Law((0,0,0))
    for requirements in [((ROOT,'B'),((0,1,0),'B')),
                         ((ROOT,'B'),((1,2,0),'B'))]:
        good,bad=classify(a,b,CANDIDATES,requirements)
        print('required',requirements,'candidates',len(CANDIDATES),
              'retained',len(good),'excluded',len(bad),
              'individual certificates',sum(len(c) for _,c in bad))
