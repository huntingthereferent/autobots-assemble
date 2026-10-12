"""Finite-law oracle for optional must-admit A/B edge requirements.

This is a standalone mathematical checker, NOT the snapshot-owning chatbot.
A rejection applies to a particular seed pairing and explicit task requirement.
"""
from finite_goal_priority import ROOT

def seed_map(old, new, words):
    forward, reverse = {ROOT: ROOT}, {ROOT: ROOT}
    for word in words:
        s = t = ROOT
        for action in word:
            s, t = old.step(s, action), new.step(t, action)
            if ((s in forward and forward[s] != t) or
                    (t in reverse and reverse[t] != s)):
                raise ValueError('incompatible seed paths')
            forward[s], reverse[t] = t, s
    return forward

def preflight(old, new, words, required):
    source, action = required
    forward = seed_map(old, new, words)
    if source not in forward:
        return 'UNDECIDED'
    old_target = old.step(source, action)
    new_target = new.step(forward[source], action)
    reverse = {value: key for key, value in forward.items()}
    if ((old_target in forward and forward[old_target] != new_target) or
            (new_target in reverse and reverse[new_target] != old_target)):
        return 'CONTRADICTED'
    return 'NOT_CONTRADICTED'

if __name__ == '__main__':
    from finite_goal_priority import Law
    old, new = Law((0,0,1)), Law((0,0,0))
    seeds = (
        ('ABAA','ABBABA'), ('ABAA','AAABB','BAAAB'), ('ABAA','BAAAB'),
        ('AAABB','BAAAB'), ('ABAA','AAABB'), ('ABBABA',),
        ('BB','ABAA'), ('AAABB',), ('BAAAB',), ('ABAA',), ('BB',)
    )
    verdicts = [preflight(old,new,w,(ROOT,'B')) for w in seeds]
    print('candidates',len(verdicts),'contradicted',verdicts.count('CONTRADICTED'),
          'remaining',len(verdicts)-verdicts.count('CONTRADICTED'))
