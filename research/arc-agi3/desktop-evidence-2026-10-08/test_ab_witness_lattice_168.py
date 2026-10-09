from itertools import combinations
from ab_witness_algebra import ab_or,ab_and
from ab_witness_antichain import WitnessAntichain

atoms=("A1","A2","O1","O2")
subsets=[()]
for n in range(1,len(atoms)+1):
    subsets += list(combinations(atoms,n))

allc=set()
for mask in range(1<<len(subsets)):
    edges=[subsets[i] for i in range(len(subsets)) if (mask>>i)&1]
    allc.add(WitnessAntichain.make(edges))

FALSE=WitnessAntichain.make([])
TRUE=WitnessAntichain.make([()])
print("TOTAL_CANONICAL",len(allc))
print("FALSE",FALSE)
print("TRUE",TRUE)

# Boundary laws.
for x in allc:
    assert ab_or(x,FALSE)==x
    assert ab_and(x,TRUE)==x
    assert ab_or(x,TRUE)==TRUE
    assert ab_and(x,FALSE)==FALSE

assert len(allc)==168
print("PASS complete 4-generator monotone witness lattice: 168 states")
