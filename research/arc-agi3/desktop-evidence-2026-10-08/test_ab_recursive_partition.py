from ab_recursive_partition import ab_fixed_point
# Tiny chain where two equal immediate states split one layer later.
nodes={
 ():{"obs":"S","immediate":((1,"X",0,"N"),),"children":{1:(1,)}},
 (9,):{"obs":"S","immediate":((1,"X",0,"N"),),"children":{1:(9,1)}},
 (1,):{"obs":"X","immediate":((1,"A",0,"N"),),"children":{}},
 (9,1):{"obs":"X","immediate":((1,"B",0,"N"),),"children":{}},
}
c,h=ab_fixed_point(nodes)
print("ROUNDS",len(h)-1,"SIZES",[len(x) for x in h])
assert c[()]!=c[(9,)]
print("PASS generic recursive A/B fixed point")
