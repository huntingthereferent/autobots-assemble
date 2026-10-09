# Extend DC22/CD82 one layer and test whether previously equivalent minimal source paths stay equivalent.
import runpy
from collections import defaultdict
from ab_family_all_minima import ab_family_all,predictive_class_map

for name,path in [
 ("DC22",r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\dc22_ab_all_minima.py"),
 ("CD82",r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\cd82_ab_all_minima.py"),
]:
 ns=runpy.run_path(path)
 occ=ns["occ"]
 states=ab_family_all(occ)
 groups=defaultdict(list)
 for o in occ:groups[o.referent].append(o)
 print(name)
 diverged=0
 for ref,s in states.items():
  if len(s.minimal_separator_sets)<=1:continue
  maps=predictive_class_map(groups[ref],s)
  # Compare induced future partitions pairwise over witnessed occurrences.
  sigs=[]
  for subset,m in maps:
   sig=[]
   for o in groups[ref]:
    rel=dict(o.relations);key=tuple((n,rel[n]) for n in subset)
    sig.append(repr(m[key]))
   sigs.append((subset,tuple(sig)))
  base=sigs[0][1]
  same=all(sig==base for _,sig in sigs[1:])
  print(" ",ref,"SOURCES",s.minimal_separator_sets,"SAME_PARTITION",same)
  if not same:diverged+=1
 print("DIVERGED",diverged)
