from causal_affine_kernel import infer_integer_affine_relation
from causal_generator_promotion import from_relation

# x relation learned from Level-2 interventions
rx=infer_integer_affine_relation(
 base_q=7,
 base_controls={"axis":12,"payload":17},
 probes={"axis":(1,2),"payload":(1,-1)},
)
gx=from_relation("x",rx,"axis","payload")
fx=gx.affine_map(12)
assert fx((17,8))==(7,8)
assert fx(fx((17,8)))==(17,8)

# y relation with the same measured gains
ry=infer_integer_affine_relation(
 base_q=2,
 base_controls={"axis":8,"payload":14},
 probes={"axis":(1,2),"payload":(1,-1)},
)
gy=from_relation("y",ry,"axis","payload")
fy=gy.affine_map(8)
assert fy((5,14))==(5,2)
assert fy(fy((5,14)))==(5,14)

# Learned x/y operators commute.
p=(17,14)
assert fx(fy(p))==fy(fx(p))
print("PASS learned generators",fx,fy,"orbit", {p,fx(p),fy(p),fx(fy(p))})
