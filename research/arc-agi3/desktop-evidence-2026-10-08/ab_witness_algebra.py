"""Algebra over A/B minimal-witness antichains.

OR = alternative sufficient witness sets.
AND = joint requirement, distributively combining minimal witness sets.
"""
from ab_witness_antichain import WitnessAntichain

def ab_or(a,b):
    return WitnessAntichain.make(list(a.edges)+list(b.edges))

def ab_and(a,b):
    if not a.edges or not b.edges:
        return WitnessAntichain.make([])
    prod=[]
    for x in a.edges:
        for y in b.edges:
            prod.append(tuple(sorted(set(x)|set(y))))
    return WitnessAntichain.make(prod)

def atom(name):
    return WitnessAntichain.make([(name,)])
