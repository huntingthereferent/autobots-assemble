"""Standalone independent finite reference for joining witnessed word histories.

Uses explicitly declared complete finite old/new laws, NOT owner authentication.
Only transitions actually traversed by the submitted words are admitted.
"""
from dataclasses import dataclass
from finite_goal_priority import Law, ROOT

@dataclass(frozen=True)
class JoinedResult:
    status: str
    words: tuple
    state_pairs: tuple
    admitted_edges: tuple
    contradiction: tuple | None


def join(old: Law, new: Law, words: tuple[str, ...]):
    if not (isinstance(old,Law) and isinstance(new,Law) and type(words) is tuple
            and 2<=len(words)<=8 and len(set(words))==len(words)
            and all(type(w) is str and 1<=len(w)<=12 and set(w)<={'A','B'}
                    for w in words)):
        raise ValueError('two finite laws and 2..8 distinct nonempty action words required')
    forward,reverse,old_prefix,new_prefix={}, {},{},{}
    edges={}
    for word in words:
        state,image=ROOT,ROOT
        states=[state]; images=[image]
        for action in word:
            state=old.step(state,action);image=new.step(image,action)
            states.append(state);images.append(image)
        for i,(s,t) in enumerate(zip(states,images)):
            prefix=word[:i]
            if s in forward and forward[s]!=t:
                witness=(old_prefix[s],prefix,'SOURCE_STATE_CONFLICT',
                         (s,s),(forward[s],t),True,False)
                assert old.follow(witness[0])==old.follow(witness[1])
                assert new.follow(witness[0])!=new.follow(witness[1])
                return JoinedResult('JOINT_RELATION_CONFLICT_WITNESSED',words,(),(),witness)
            if t in reverse and reverse[t]!=s:
                witness=(new_prefix[t],prefix,'TARGET_STATE_CONFLICT',
                         (reverse[t],s),(t,t),False,True)
                assert old.follow(witness[0])!=old.follow(witness[1])
                assert new.follow(witness[0])==new.follow(witness[1])
                return JoinedResult('JOINT_RELATION_CONFLICT_WITNESSED',words,(),(),witness)
            forward[s]=t;reverse[t]=s
            old_prefix.setdefault(s,prefix);new_prefix.setdefault(t,prefix)
            if i<len(word):
                edge=(s,word[i],states[i+1],t,images[i+1])
                key=(s,word[i])
                if key in edges and edges[key]!=edge:
                    raise AssertionError('same source/action replayed inconsistently')
                edges[key]=edge
    for s,a,u,t,v in edges.values():
        assert forward[s]==t and forward[u]==v
        assert old.step(s,a)==u and new.step(t,a)==v
    return JoinedResult('JOINT_PARTIAL_CORRESPONDENCE_WITNESSED',words,
                        tuple(sorted(forward.items())),tuple(sorted(edges.values())),None)

if __name__=='__main__':
    old,new=Law((0,0,0)),Law((0,1,2))
    for words in (('A','BAA'),('A','BAB')):
        r=join(old,new,words)
        print(words,r.status,'pairs',len(r.state_pairs),'edges',len(r.admitted_edges),
              'collision',r.contradiction)
