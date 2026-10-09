from ab_relation_synthesis import synthesize_relation,apply_synthesized
from ab_family_all_minima import Occurrence

# CD82-shaped witness: best old vocabulary gives 8 blocks; futures need 4.
proof=((0,),(1,),(2,),(3,6),(4,7),(5,8),(9,),(10,))
fut=((0,1),(2,),(3,4,6,7,9,10),(5,8))

# Build future labels exactly matching fut.
lab={}
for k,b in enumerate(fut):
 for i in b:lab[i]=f"F{k}"
group=[Occurrence("R",(),lab[i]) for i in range(11)]

r=synthesize_relation("R",proof,group)
print("SYNTH",r)
assert r.continuation_partition==fut
classes=[apply_synthesized(r,i) for i in range(11)]
print("CLASSES",classes)
assert classes[0]==classes[1]
assert classes[3]==classes[4]==classes[6]==classes[7]==classes[9]==classes[10]
assert classes[5]==classes[8]
print("PASS synthesized A/B relation closes surplus distinctions")
