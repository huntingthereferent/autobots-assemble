"""Standalone finite checker for typed edge/path/destination requirements.

Takes a completed witness from finite_conflict_guidance and checks each kind
by its own mathematical relation. Does not model HTTP owners or natural language.
"""
from finite_goal_priority import ROOT, Law
from finite_conflict_guidance import extend


def inspect(old: Law, new: Law, seed_words, *, edges=(), paths=(), destinations=()):
    witness=extend(old,new,tuple(seed_words))
    forward=dict(witness.mapping)
    admitted={(s,a):(t,ns,nt) for s,a,t,ns,nt in witness.admitted}
    results=[]
    for state,action in edges:
        results.append(('EDGE',(state,action),(state,action) in admitted))
    for source,image in destinations:
        results.append(('DESTINATION',(source,image),forward.get(source)==image))
    for word,old_end,new_end in paths:
        s=ns=ROOT
        valid=True
        for action in word:
            step=admitted.get((s,action))
            if step is None or step[1]!=ns:
                valid=False
                break
            s,ns=step[0],step[2]
        valid=valid and (s,ns)==(old_end,new_end) and (old.follow(word),new.follow(word))==(old_end,new_end)
        results.append(('PATH',(word,old_end,new_end),valid))
    return witness,tuple(results)


def verdict(old,new,seed_words,**kwargs):
    witness,checks=inspect(old,new,seed_words,**kwargs)
    return 'ALL_REQUIRED_WITNESSED' if all(r[2] for r in checks) else 'REQUIREMENTS_UNPROVED',witness,checks


if __name__=='__main__':
    old,new=Law((0,0,1)),Law((0,0,0))
    obligations=dict(edges=((ROOT,'A'),),
        paths=(('ABAA',(0,2,0),(0,2,0)),('ABBABA',(0,1,1),(0,1,0))),
        destinations=(((0,1,1),(0,1,0)),))
    for words in (('ABAA','ABBABA'),('BB','ABAA')):
        status,witness,checks=verdict(old,new,words,**obligations)
        print(words,status,'pairs',len(witness.mapping),'edges',len(witness.admitted),checks)
