from ab_recursive_closure import Witness,ab

# One relation is enough.
A=Witness("O",(("r1","same"),("r2","L"),("r3",0)),"F1")
B=Witness("O",(("r1","same"),("r2","R"),("r3",0)),"F2")
x,y=ab(A,B)
print("L1",x,y)
assert x.retained==( ("r2","L"), )
assert y.retained==( ("r2","R"), )

# Because x != y, that distinction itself is already a valid next referent.
X=Witness(x,(("s1",0),("s2","left")),"G1")
Y=Witness(y,(("s1",0),("s2","right")),"G2")
x2,y2=ab(X,Y)
print("DISTINCTION_SURVIVES_AS_REFERENT",x2,y2)
assert x2.referent==x and y2.referent==y
assert x2.retained==() and y2.retained==()

# Harder recursive case: the SAME refined output is reused, and later develops
# incompatible futures. A/B must split again using the new relation layer.
S=x
C=Witness(S,(("s1",0),("s2","left")),"G1")
D=Witness(S,(("s1",0),("s2","right")),"G2")
c,d=ab(C,D)
print("SAME_OUTPUT_SPLITS_AGAIN",c,d)
assert c.retained==( ("s2","left"), )
assert d.retained==( ("s2","right"), )

# Family accumulation: x separates one pair; y separates another pair later.
A1=Witness("Q",(("x",0),("y",0)),"A")
B1=Witness("Q",(("x",1),("y",0)),"B")
u,v=ab(A1,B1)
assert u.retained==( ("x",0), ) and v.retained==( ("x",1), )

C1=Witness(u,(("y",0),),"C0")
D1=Witness(u,(("y",1),),"C1")
u2,w=ab(C1,D1)
print("FAMILY_RECURSION",u,v,u2,w)
assert u2.retained==( ("y",0), )
assert w.retained==( ("y",1), )

print("PASS recursive A/B closure")
