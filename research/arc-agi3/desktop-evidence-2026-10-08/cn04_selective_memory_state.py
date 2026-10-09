"""Selective predictive-state update for CN04 public observations.

State is normally O_t.
If O_t has incompatible observed futures, split it by predecessor O_{t-1}.
"""
from collections import defaultdict

# Full branch vectors for the repeated Level-5 observation.
rows=[
('4d05e51626ea',None),
('8dfb16618370',None),
('61ecd26f48f6',None),
('a9bd5d03cc26',None),
('0de2f6eb7460',None),
('8bfd417ca711',None),
('c55059ee42d4',None),
('f540c3aa6488',None),
('748f8bfc8dd2',None),
('290e41e7246a',None),
('c785f27b0ec2',None),
('b8e5aebd8004',('217b4569119f','537f35ac70f9','fcd942bc34af','978ce0c5be14','1b8305baa319')),
('1b8305baa319',None),
('b8e5aebd8004',('c1808cd545e2','6310ca21b783','5213bc42b8c7','8ad62d5e48b6','d00943ccf2e2')),
('d00943ccf2e2',None),
]

# Discover ambiguous observation classes from incompatible outcome vectors.
future=defaultdict(set)
for o,v in rows:
 if v is not None:future[o].add(v)
amb={o for o,vs in future.items() if len(vs)>1}
print("AMBIGUOUS_OBSERVATIONS",amb)

def encode(prev,cur):
 return ("split",prev,cur) if cur in amb else ("plain",cur)

encoded=[]
for t,(cur,v) in enumerate(rows):
 prev=rows[t-1][0] if t else None
 encoded.append(encode(prev,cur))
 print(t,cur,"=>",encoded[-1])

assert encoded[11]!=encoded[13]
assert encoded[11][-1]==encoded[13][-1]=="b8e5aebd8004"

# Online update needs only prior public observation plus the learned ambiguity set.
def update(state,last_obs,new_obs):
 return encode(last_obs,new_obs)

# At the collision, predecessor context is sufficient to choose the right response vector.
responses={
 encoded[11]:rows[11][1],
 encoded[13]:rows[13][1],
}
assert len(responses)==2
assert responses[encoded[11]]!=responses[encoded[13]]
print("BRANCH_11",encoded[11],responses[encoded[11]])
print("BRANCH_13",encoded[13],responses[encoded[13]])
print("PASS selective-memory predictive state")
