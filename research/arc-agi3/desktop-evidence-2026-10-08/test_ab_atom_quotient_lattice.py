from itertools import combinations
from ab_witness_antichain import WitnessAntichain

# Current A/B atom quotient from real cross-game evidence:
# A2 ~ O1
qmap={"A1":"X","A2":"Y","O1":"Y","O2":"Z"}

atoms=("A1","A2","O1","O2")
subs=[()]
for n in range(1,5):subs+=list(combinations(atoms,n))

all4=set()
for mask in range(1<<len(subs)):
    edges=[subs[i] for i in range(len(subs)) if (mask>>i)&1]
    all4.add(WitnessAntichain.make(edges))

def quotient(a):
    edges=[]
    for e in a.edges:
        edges.append(tuple(sorted({qmap[x] for x in e})))
    return WitnessAntichain.make(edges)

Q={quotient(a) for a in all4}
print("FOUR_NAME_STATES",len(all4))
print("QUOTIENT_STATES",len(Q))

# Independently enumerate the canonical 3-generator witness space.
atoms3=("X","Y","Z")
subs3=[()]
for n in range(1,4):subs3+=list(combinations(atoms3,n))
all3=set()
for mask in range(1<<len(subs3)):
    all3.add(WitnessAntichain.make([subs3[i] for i in range(len(subs3)) if (mask>>i)&1]))

print("THREE_GENERATOR_STATES",len(all3))
assert Q==all3
assert len(Q)==20
print("PASS A/B atom quotient: 168 named states -> complete 20-state 3-class witness space")
