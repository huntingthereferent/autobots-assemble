from ab_witness_algebra import atom,ab_or,ab_and
from ab_witness_antichain import WitnessAntichain,ab_compare

A1=atom("A1");A2=atom("A2");O1=atom("O1");O2=atom("O2")

K=ab_or(A2,O1)
R=ab_or(K,O2)
S=ab_or(A1,K)
CD=ab_and(A1,R)

print("K",K)
print("R",R)
print("S",S)
print("CD",CD)

assert K==WitnessAntichain.make([("A2",),("O1",)])
assert R==WitnessAntichain.make([("A2",),("O1",),("O2",)])
assert S==WitnessAntichain.make([("A1",),("A2",),("O1",)])
assert CD==WitnessAntichain.make([("A1","A2"),("A1","O1"),("A1","O2")])

# A/B(R,S) exposes K directly as their shared minimal witness subfamily.
cmp=ab_compare(R,S)
assert cmp.shared_edges==K
assert cmp.left_only==O2
assert cmp.right_only==A1

# Recursive reuse of K reconstructs both parents and the joint CD82 family.
assert ab_or(K,O2)==R
assert ab_or(A1,K)==S
assert ab_and(A1,R)==CD

# Distributive closure is exactly the minimal-source semantics.
dist=ab_or(ab_and(A1,A2),ab_and(A1,O1))
fact=ab_and(A1,K)
print("DISTRIBUTIVE",dist,fact)
assert dist==fact

print("PASS recursive A/B witness algebra")
