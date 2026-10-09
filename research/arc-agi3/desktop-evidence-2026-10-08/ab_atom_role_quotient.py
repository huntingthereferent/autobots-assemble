"""A/B the relation atoms themselves by their roles in witnessed source families."""

atoms=("A1","A2","O1","O2")

# Canonical observed higher-order source families.
families={
 "G":  (("A1",),),
 "R":  (("A2",),("O1",),("O2",)),
 "S":  (("A1",),("A2",),("O1",)),
 "CD": (("A1","A2"),("A1","O1"),("A1","O2")),
}

# Role signature for an atom:
# for each family, record the multiset of edge sizes in which that atom occurs
# and total occurrence count.  This ignores the atom's vocabulary/name itself.
def signature(atom):
 out=[]
 for name,edges in sorted(families.items()):
  sizes=tuple(sorted(len(e) for e in edges if atom in e))
  out.append((name,sizes))
 return tuple(out)

groups={}
for a in atoms:
 sig=signature(a)
 groups.setdefault(sig,[]).append(a)
 print(a,sig)

print("EQUIV_CLASSES",list(groups.values()))

# Under current evidence A2 and O1 are structurally indistinguishable.
assert any(set(g)=={"A2","O1"} for g in groups.values())
# A1 and O2 have distinct roles.
assert all(not ({"A1","O2"}<=set(g)) for g in groups.values())

print("PASS A/B atom quotient under current cross-game evidence")
