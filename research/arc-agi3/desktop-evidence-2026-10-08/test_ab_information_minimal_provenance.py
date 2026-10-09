from ab_family_all_minima import Occurrence,ab_family_all
from ab_information_minimal_provenance import information_minimal_provenance

# A/B are aliases with the coarsest sufficient split.
# C uniquely identifies every occurrence, therefore predicts the future but
# contains extra distinctions and should be removed.
xs=[
 Occurrence("R",(("A",0),("B","x"),("C","u")),"L"),
 Occurrence("R",(("A",0),("B","x"),("C","v")),"L"),
 Occurrence("R",(("A",1),("B","y"),("C","w")),"R"),
 Occurrence("R",(("A",1),("B","y"),("C","z")),"R"),
]
s=ab_family_all(xs)["R"]
ref,classes=information_minimal_provenance(xs,s)
print("MIN_INFO",classes)
assert len(classes)==1
assert set(classes[0].sources)=={("A",),("B",)}
print("PASS information-minimal A/B provenance")
