from causal_affine_kernel import infer_integer_affine_relation
# AR25 Level-2 black-box component-centroid evidence:
# base dependent copy q=7, axis a=12, payload p=17
# axis +1 -> q +2; payload +1 -> q -1
r=infer_integer_affine_relation(
    base_q=7,
    base_controls={"axis":12,"payload":17},
    probes={"axis":(1,2),"payload":(1,-1)},
)
print(r)
assert r.predict(axis=12,payload=17)==7
assert r.predict(axis=11,payload=17)==5
assert r.predict(axis=13,payload=17)==9
assert r.predict(axis=12,payload=16)==8
assert r.predict(axis=12,payload=18)==6
assert dict(r.gains)=={"axis":2,"payload":-1}
assert r.constant==0
print("PASS causal relation q = 2*axis - payload")
