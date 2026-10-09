G=frozenset({"G"})
R=frozenset({"R"})
E=frozenset()
GR=G|R

def ab_axes(a,b):
    return a&b,a-b,b-a

tests=[
 ("E_G",E,G,(E,E,G)),
 ("E_R",E,R,(E,E,R)),
 ("G_GR",G,GR,(G,E,R)),
 ("R_GR",R,GR,(R,E,G)),
 ("G_R",G,R,(E,G,R)),
]
for name,a,b,want in tests:
    got=ab_axes(a,b)
    print(name,"GOT",tuple(sorted(x) for x in got),"WANT",tuple(sorted(x) for x in want))
    assert got==want
print("PASS")
