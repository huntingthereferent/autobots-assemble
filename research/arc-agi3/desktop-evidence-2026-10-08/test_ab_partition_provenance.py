from ab_family_all_minima import Occurrence,ab_family_all
from ab_partition_provenance import source_alias_classes

# A and B are aliases: same occurrence split, different names.
# C is a genuinely different proof partition, but all predict the same future.
xs=[
 Occurrence("R",(("A",0),("B","x"),("C","u")),"L"),
 Occurrence("R",(("A",0),("B","x"),("C","v")),"L"),
 Occurrence("R",(("A",1),("B","y"),("C","w")),"R"),
 Occurrence("R",(("A",1),("B","y"),("C","z")),"R"),
]
s=ab_family_all(xs)["R"]
print("MIN",s.minimal_separator_sets)
q=source_alias_classes(xs,s)
print("Q",q)

classes=[set(c.sources) for c in q.alias_classes]
assert {("A",),("B",)} in classes
assert {("C",)} in classes
assert len(classes)==2
print("PASS partition-aware provenance quotient")
