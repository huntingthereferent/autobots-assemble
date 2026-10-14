"""Small standalone checker for RECORDED, not freshly rerun, policy results.

The full comparison needs the local integrated chatbot package. This file
only makes its published 18-pair summary checkable and replays key finite words.
"""
from finite_goal_priority import Law

SOURCE=(0,0,1)
CASE_LAWS=((1,0,1),(1,0,1),(0,0,0),(0,0,0),(0,1,0),(2,1,0))
CASE_GOALS=(
    ((0,1,0),(0,1,1)), ((0,1,1),(0,2,0)),
    ((0,1,0),(0,1,1)), ((0,1,1),(0,2,0)),
    ((0,1,0),(0,1,1)), ((1,1,0),(1,1,2)),
)
# budget, case index, fixed goals, guided goals, fixed edges, guided edges,
# fixed owner observations, guided owner observations, guided attempts.
# Evidence snapshot from 18 executed paired runs in the full local package.
ROWS=(
 (2,0,2,2,41,41,108,108,1), (2,1,2,2,41,41,108,108,1),
 (2,2,1,1,15,15,46,46,1),   (2,3,2,2,13,13,44,44,1),
 (2,4,2,2,42,42,108,108,0), (2,5,1,1,11,11,60,60,0),
 (3,0,2,2,41,41,108,108,2), (3,1,2,2,41,41,108,108,2),
 (3,2,1,1,15,15,46,46,2),   (3,3,2,2,13,13,44,46,2),
 (3,4,2,2,42,42,108,108,0), (3,5,1,1,11,11,60,60,0),
 (4,0,2,2,42,41,108,108,3), (4,1,2,2,41,41,108,108,3),
 (4,2,1,1,15,15,46,46,2),   (4,3,2,2,13,13,44,46,3),
 (4,4,2,2,42,42,108,108,0), (4,5,1,1,11,11,60,60,0),
)

def counts():
    result={'goal_ties':0,'edge_fixed_wins':0,'edge_guided_wins':0,
            'observation_fixed_wins':0,'observation_guided_wins':0,
            'fixed_reads':0,'guided_reads':0,'guided_attempts':0}
    for budget, case, fg, gg, fe, ge, fq, gq, attempts in ROWS:
        assert budget in (2,3,4) and 0 <= case < 6
        result['goal_ties'] += fg==gg
        result['edge_fixed_wins'] += fe>ge
        result['edge_guided_wins'] += ge>fe
        result['observation_fixed_wins'] += fq<gq
        result['observation_guided_wins'] += gq<fq
        result['fixed_reads'] += fq
        result['guided_reads'] += gq
        result['guided_attempts'] += bool(attempts)
    return result

def gate():
    # Conservative no-regression promotion rule; finite sample only.
    better=any(gg>fg or ge>fe or gq<fq for _,_,fg,gg,fe,ge,fq,gq,_ in ROWS)
    no_regression=all(gg>=fg and ge>=fe and gq<=fq
                      for _,_,fg,gg,fe,ge,fq,gq,_ in ROWS)
    return 'EVIDENCE_SUPPORTS_GUIDANCE_ON_DECLARED_CASES' if better and no_regression else 'KEEP_FIXED_DEFAULT'

def replay_negative_controls():
    a=Law(SOURCE)
    b=Law((1,0,1))
    assert (a.follow('B'),b.follow('B'))==((0,1,0),(0,1,1))
    assert (a.follow('BBBB'),b.follow('BBBB'))==((0,1,1),(0,1,0))
    c=Law((0,0,0))
    assert (a.follow('ABBABA'),c.follow('ABBABA'))==((0,1,1),(0,1,0))
    assert (a.follow('ABAA'),c.follow('ABAA'))==((0,2,0),(0,2,0))
    return True

if __name__ == '__main__':
    replay_negative_controls()
    print(gate(),counts())
