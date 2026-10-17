"""Independent Engine-2 Boundary Math probe: minimal quotient-trace change.

Compare two admitted finite-field coupling laws over F3^5, with the same
base coupling q0, gain g=1, offsets k=0, fifth coupling q2=0, and with
Q=(0,0,0) versus Q=(0,0,1). No claims across other mathematical grammars.

WATCH: fixed points of B, B^3 and B^9; lower centralizer order. Prove
nonconjugacy by explicit B^3 invariant and show the rooted origin collision.
"""
from itertools import product
import json

F3 = (0, 1, 2)
BASE_Q0 = (0, 1, 2, 0, 2, 1, 1, 1, 1)
ALPHA = (0, 1, 1)
Q_LEFT = (0, 0, 0)
Q_RIGHT = (0, 0, 1)
STATES = tuple(product(F3, repeat=5))


def step(state, action, Q):
    u,v,z,y,t = state
    if action == 'A':
        return ((u + 1) % 3,v,z,y,t)
    if action != 'B':
        raise ValueError('action must be A or B')
    return (u,(v+u+1)%3,(z+BASE_Q0[3*u+v])%3,
            (y+Q[(z+ALPHA[v])%3])%3,t)


def symmetry(state, Q):
    u,v,z,y,t = state
    w = (z+ALPHA[v])%3
    return (u,v,(z+1)%3,(y+Q[w]-Q[0])%3,t)


def power(state, operation, Q, n):
    for _ in range(n):
        state = operation(state,Q)
    return state


def counts(Q):
    B = lambda s, Q: step(s,'B',Q)
    return {f'B^{n}':sum(power(s,B,Q,n)==s for s in STATES)
            for n in (1,3,9)}


def investigate():
    B = lambda s,Q: step(s,'B',Q)
    assert sum(Q_LEFT)%3 == 0 and sum(Q_RIGHT)%3 == 1
    for Q in (Q_LEFT,Q_RIGHT):
        assert all(symmetry(step(s,act,Q),Q)==step(symmetry(s,Q),act,Q)
                   for s in STATES for act in 'AB')
        assert all(power(s,symmetry,Q,9)==s for s in STATES)
        assert all(power(s,B,Q,9)==s for s in STATES)
    before=counts(Q_LEFT)
    after=counts(Q_RIGHT)
    assert before=={'B^1':0,'B^3':243,'B^9':243}
    assert after=={'B^1':0,'B^3':0,'B^9':243}
    assert all(power(s,B,Q_LEFT,3)==s for s in STATES)
    assert all(power(s,B,Q_RIGHT,3)==(s[:3]+((s[3]+1)%3,)+s[4:]) for s in STATES)
    origin=(0,0,0,0,0)
    assert power(origin,B,Q_LEFT,3)==origin
    assert power(origin,B,Q_RIGHT,3)==(0,0,0,1,0)
    return {
        'watch':'B^n fixed-point count and lower centralizer cyclic order',
        'same_base_q0':BASE_Q0, 'same_gain':1,
        'same_offsets':(0,0,0),'same_fifth_coupling':(0,)*9,
        'before':{'quotient':Q_LEFT,'trace':0,'symmetry_order':3,'fixed':before},
        'after':{'quotient':Q_RIGHT,'trace':1,'symmetry_order':9,'fixed':after},
        'one_entry_changed':'Q(2): 0 -> 1',
        'number_of_states':len(STATES),
        'root_word_witness':{'word':'BBB',
                             'before_image':power(origin,B,Q_LEFT,3),
                             'after_image':power(origin,B,Q_RIGHT,3)},
        'native_full_state_obstruction': 'Fix(BBB) differs, 243 vs 0: no labeled A/B full-state conjugacy',
        'inherited_scope':'two selected admissible fifth-coordinate families, F3^5 only; no claimed universal bridge',
        'status':'WITNESSED_BOUNDARY'
    }

if __name__=='__main__':
    print(json.dumps(investigate(), indent=2))