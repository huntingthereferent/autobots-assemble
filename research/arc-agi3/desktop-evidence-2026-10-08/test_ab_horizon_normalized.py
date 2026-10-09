from ab_horizon_normalized import horizon_signatures
nodes={
 ():{"obs":"A","immediate":((1,"X",0,"NOT_FINISHED"),),"children":{1:(1,)}},
 (9,):{"obs":"A","immediate":((1,"X",0,"NOT_FINISHED"),),"children":{1:(9,1)}},
 (1,):{"obs":"X","immediate":((1,"Y",0,"NOT_FINISHED"),),"children":{1:(1,1)}},
 # second branch not expanded equally far
 (9,1):{"obs":"X","immediate":((1,"Y",0,"NOT_FINISHED"),),"children":{1:(9,1,1)}},
 (1,1):{"obs":"Y","immediate":((1,"Z",0,"NOT_FINISHED"),),"children":{}},
}
h=horizon_signatures(nodes,[1],3)
print({k:sorted(v) for k,v in h.items()})
assert h[1][()]==h[1][(9,)]
# Only the branch with three witnessed response steps is admitted at horizon 3.
# The unequal-evidence pair therefore cannot be compared at that horizon.
assert () in h[3] and (9,) not in h[3]
print("PASS horizon-normalized A/B evidence contract")
