"""Independent complete-law reference for two separately declared finite revisions.

This is NOT an owner authentication mechanism; it checks only formal word
relations and keeps original/changed histories separate.
"""
from dataclasses import dataclass
from finite_goal_priority import Law,ROOT

@dataclass(frozen=True)
class RevisionHistory:
    revision: int
    word: str
    states: tuple

@dataclass(frozen=True)
class RelationCheck:
    pair: tuple
    old_histories: tuple[RevisionHistory,...]
    new_histories: tuple[RevisionHistory,...]
    old_equal: bool
    new_equal: bool
    status: str

def path(law,version,word):
    if type(version) is not int or version<0 or type(word) is not str or len(word)>12 or any(x not in 'AB' for x in word):
        raise ValueError('finite revision and A/B action word required')
    states=[ROOT]
    for a in word:states.append(law.step(states[-1],a))
    return RevisionHistory(version,word,tuple(states))

def compare(old:Law,new:Law,old_version:int,new_version:int,pairs):
    if (type(pairs) is not tuple or not pairs or
        any(type(p) is not tuple or len(p)!=2 or p[0]==p[1] for p in pairs)):
        raise ValueError('explicit pair list required')
    if type(old_version) is not int or type(new_version) is not int or old_version==new_version:
        raise ValueError('separately declared finite revisions required')
    checks=[]
    for w1,w2 in pairs:
        history_old=tuple(path(old,old_version,w) for w in (w1,w2))
        history_new=tuple(path(new,new_version,w) for w in (w1,w2))
        eq_old=history_old[0].states[-1]==history_old[1].states[-1]
        eq_new=history_new[0].states[-1]==history_new[1].states[-1]
        status=('RELATION_CHANGED' if eq_old!=eq_new else
                'EQUALITY_PRESERVED' if eq_old else 'NONIDENTITY_PRESERVED')
        checks.append(RelationCheck((w1,w2),history_old,history_new,eq_old,eq_new,status))
    return tuple(checks)

if __name__=='__main__':
    old,new=Law((0,0,0)),Law((0,1,2))
    for c in compare(old,new,0,1,(('','AAA'),('BA','ABB'))):
        print(c.pair,c.status,c.old_histories[0].states[-1],c.new_histories[0].states[-1])
