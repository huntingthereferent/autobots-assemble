from ab_family_all_minima import Occurrence,ab_family_all,predictive_class_map

# x and y are perfectly correlated; either one is a minimal separator.
xs=[
 Occurrence("O",(("x",0),("y","L"),("noise",9)),"A"),
 Occurrence("O",(("x",1),("y","R"),("noise",9)),"B"),
]
s=ab_family_all(xs)["O"]
print("TIE",s.minimal_separator_sets)
assert s.minimal_separator_sets==(("x",),("y",))
maps=predictive_class_map(xs,s)
print("MAPS",maps)

# XOR requires the joint set; there is no one-relation alternative.
xor=[
 Occurrence("Q",(("x",0),("y",0)),"even"),
 Occurrence("Q",(("x",0),("y",1)),"odd"),
 Occurrence("Q",(("x",1),("y",0)),"odd"),
 Occurrence("Q",(("x",1),("y",1)),"even"),
]
q=ab_family_all(xor)["Q"]
print("JOINT",q.minimal_separator_sets)
assert q.minimal_separator_sets==(("x","y"),)
print("PASS all-minimal A/B witness provenance")
