"""Public-only hypothesis elimination for CN04 Level 1.

Observations:
- marker identities are tracked only by public action-state continuity;
- overlap is public color 3;
- success is public levels_completed increment.

We compare completion hypotheses rather than reading latent marker labels.
"""

from itertools import product

# Publicly tracked marker identities:
# A0,A1 belong to initially selected object.
# B0,B1 belong to the other object's action-state cycle.
markers=("A0","A1","B0","B1")

# Interventions reconstructed from public frames:
# successful full alignment (action5 state 1): B0->A1, B1->A0
# unsuccessful full alignment (action5 state 3): B0->A0, B1->A1
experiments=[
    ("success", {frozenset(("A1","B0")),frozenset(("A0","B1"))}, True),
    ("failure", {frozenset(("A0","B0")),frozenset(("A1","B1"))}, False),
]

def predicts_untyped(pairs):
    # completion iff all markers are geometrically paired
    touched=set().union(*pairs)
    return touched==set(markers)

def predicts_typed(pairs,labels):
    touched=set()
    for pair in pairs:
        a,b=tuple(pair)
        if labels[a]!=labels[b]:
            return False
        touched|=pair
    return touched==set(markers)

print("UNTYPED")
for name,pairs,outcome in experiments:
    pred=predicts_untyped(pairs)
    print(name,"pred",pred,"obs",outcome)
print("UNTYPED_SURVIVES",all(predicts_untyped(p)==o for _,p,o in experiments))

# Learn smallest hidden labeling (up to global label swap) consistent with outcomes.
survivors=[]
for bits in product((0,1),repeat=len(markers)):
    lab=dict(zip(markers,bits))
    if all(predicts_typed(pairs,lab)==outcome for _,pairs,outcome in experiments):
        survivors.append(lab)

print("TYPED_SURVIVORS",len(survivors))
for s in survivors:print(s)

# Quotient away global 0<->1 renaming by fixing A0=0.
canon=[s for s in survivors if s["A0"]==0]
print("CANONICAL",canon)
assert len(canon)==1
learned=canon[0]
assert learned=={"A0":0,"A1":1,"B0":1,"B1":0}
print("PASS: public interventions identify two latent marker classes up to label permutation")
