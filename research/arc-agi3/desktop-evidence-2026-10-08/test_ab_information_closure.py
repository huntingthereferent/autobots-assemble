from ab_family_all_minima import Occurrence
from ab_information_closure import info_ab_group

# C alone is sufficient but uniquely identifies every occurrence.
# A alone and B alone both fail.
# A+B jointly is sufficient with only three blocks, so it preserves less
# irrelevant information than C.
xs=[
 Occurrence("R",(("A",0),("B",0),("C","u")),"L"),
 Occurrence("R",(("A",0),("B",0),("C","v")),"L"),
 Occurrence("R",(("A",0),("B",1),("C","w")),"R"),
 Occurrence("R",(("A",1),("B",0),("C","z")),"R"),
]
s=info_ab_group(xs)
print("STATE",s)
assert len(s.proofs)==1
p=s.proofs[0]
assert ("A","B") in p.sources
assert ("C",) not in p.sources
assert sorted(map(len,p.partition))==[1,1,2]
print("PASS direct information-minimal A/B closure")
