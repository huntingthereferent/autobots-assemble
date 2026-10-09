"""A/B quotient of depth-5 relation atoms by witnessed higher-order roles."""

# Unique real minimal-witness families from depth-5 scans.
families={
"DC_R": (("A2",),("O1",),("O2",)),
"DC_U": (("A4",),("O1",),("O2",),("O3",),("O4",)),
"DC_V": (("A4",),("O1",),("O3",),("O4",)),
"CD_J": (("A1","A2"),("A1","O1"),("A1","O2")),
"CD_G": (("A1",),),

"SK_1": (
("A1","A3"),("A1","O2"),("A1","O3"),
("A2","A3"),("A2","O2"),("A2","O3"),
("A3","O1"),("O1","O2"),("O1","O3")),
"SK_2": (
("A1","A3"),("A1","O2"),
("A2","A3"),("A2","O2"),("A2","O3"),
("A3","O1"),("O1","O2")),
"SK_3": (
("A1","A3"),("A1","O2"),
("A2","A3"),("A2","O2"),("A2","O3"),
("A3","O1"),("O1","O2"),("O1","O3")),
"SK_4": (
("A1","A3"),("A1","O2"),
("A2","O2"),
("A3","O1"),("O1","O2"),("O1","O3")),
"SK_5": (("A1","O2"),("A1","O3")),
"SK_6": (("A1","O3"),),
"SK_7": (("A1",),("A2",),("O1",)),
"SK_8": (("A1",),("A3",),("O1",),("O2",),("O3",)),
"SK_9": (("A1",),("O1",)),
"SK_10": (("A1",),),
"SK_11": (("A3",),("O2",)),
"SK_12": (("A4",),("O3",),("O4",)),
}

atoms=sorted({a for edges in families.values() for e in edges for a in e})
print("ATOMS",atoms)

def signature(atom):
    # Structural role only: for each witnessed family, record sorted sizes of
    # minimal edges containing this atom. Names of the atom itself are not used.
    return tuple(
        (fname,tuple(sorted(len(e) for e in edges if atom in e)))
        for fname,edges in sorted(families.items())
    )

groups={}
for a in atoms:
    sig=signature(a)
    groups.setdefault(sig,[]).append(a)

print("EQUIV_CLASSES")
for g in groups.values():
    print(" ",g)
    for a in g: print("   ",a,signature(a))

print("N_ATOMS",len(atoms),"N_CLASSES",len(groups))
assert len(atoms)==8

# The shallow A2~O1 class must now be split.
assert not any(set(g)>={"A2","O1"} for g in groups.values())
print("PASS deeper evidence A/B-splits shallow A2/O1 quotient")
