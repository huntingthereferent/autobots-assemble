from ab_family_closure import Occurrence,ab_family,project

# One relation sufficient.
xs=[
 Occurrence("O",(("x",0),("y",9)),"A"),
 Occurrence("O",(("x",1),("y",9)),"B"),
]
s=ab_family(xs)["O"]
print("ONE",s)
assert s.retained_names==("x",)

# Neither x nor y alone is sufficient. Their joint relation is.
xor=[
 Occurrence("Q",(("x",0),("y",0)),"even"),
 Occurrence("Q",(("x",0),("y",1)),"odd"),
 Occurrence("Q",(("x",1),("y",0)),"odd"),
 Occurrence("Q",(("x",1),("y",1)),"even"),
]
q=ab_family(xor)["Q"]
print("JOINT",q)
assert q.retained_names==("x","y")

proj=[project(o,q) for o in xor]
print("PROJECTED",proj)
assert len(set(proj))==4

# Reuse the A/B output as the next referent.
next_occ=[
 Occurrence(proj[0],(("z","L"),),"next0"),
 Occurrence(proj[0],(("z","R"),),"next1"),
]
n=ab_family(next_occ)[proj[0]]
print("RECURSE",n)
assert n.retained_names==("z",)

print("PASS family A/B closure including joint relation sets")
