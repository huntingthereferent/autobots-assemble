import runpy
from collections import defaultdict
from ab_information_closure import info_ab_group

for name,path in [
 ("DC22",r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\dc22_partition_provenance.py"),
 ("CD82",r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\cd82_information_minimal_provenance.py"),
]:
 ns=runpy.run_path(path)
 occ=ns["occ"]
 groups=defaultdict(list)
 for o in occ:groups[o.referent].append(o)
 print("\nGAME",name)
 for ref,g in groups.items():
  futures={o.future for o in g}
  if len(futures)<=1:continue
  s=info_ab_group(g)
  # Canonical continuation-equivalence partition.
  fb={}
  for i,o in enumerate(g):
   fb.setdefault(repr(o.future),[]).append(i)
  future_partition=tuple(sorted(tuple(v) for v in fb.values()))
  print("REF",ref)
  print(" FUTURE_PART",future_partition)
  for p in s.proofs:
   print(" PART",p.partition,"SOURCES",p.sources,"EXACT_FUTURE",p.partition==future_partition)
  assert all(p.partition==future_partition for p in s.proofs), (name,ref,s.proofs,future_partition)
 print("DONE",name)
