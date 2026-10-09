import pickle
from collections import defaultdict
from ab_horizon_normalized import horizon_signatures

with open(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\ar25_full_tree_nodes.pkl","rb") as f:
    nodes=pickle.load(f)
ACTIONS=[1,2,3,4,5,7]
hs=horizon_signatures(nodes,ACTIONS,2)

# Compare H1 and H2 only on occurrences admitted at H2.
groups=defaultdict(list)
for p in hs[2]:
    groups[nodes[p]["obs"]].append(p)

growth=[]
print("H2_SAME_SUPPORT_COMPARISON")
for obs,paths in groups.items():
    c1=len({hs[1][p] for p in paths})
    c2=len({hs[2][p] for p in paths})
    if c1>1 or c2>1:
        print(obs,"N",len(paths),"H1",c1,"H2",c2)
    if c2>c1:growth.append((obs,c1,c2,paths))

print("GENUINE_GROWTH",len(growth))
for x in growth:print(x)
