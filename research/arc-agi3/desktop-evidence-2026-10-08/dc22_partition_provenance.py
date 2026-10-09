from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib,copy
from collections import defaultdict
from ab_family_all_minima import Occurrence,ab_family_all
from ab_partition_provenance import source_alias_classes
from ab_information_minimal_provenance import information_minimal_provenance

def fh(r):
 if not getattr(r,"frame",None):return "EMPTY"
 return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]

a=Arcade(operation_mode=OperationMode.NORMAL);root=a.make("dc22")
nodes=[(root,"START",(),())];occ=[]
for depth in range(5):
 nxt=[]
 for env,obs,oh,ah in nodes:
  outs=[]
  for z in [1,2,3,4,5]:
   q=copy.deepcopy(env)
   try:r=q.step(GameAction.from_id(z),data={});outs.append((z,fh(r),r.levels_completed,r.state.name))
   except Exception as ex:outs.append((z,"ERR",type(ex).__name__,None))
  rel=[]
  for i in range(1,6):
   rel += [(f"A{i}",ah[-i] if len(ah)>=i else None),(f"O{i}",oh[-i] if len(oh)>=i else None)]
  occ.append(Occurrence(obs,tuple(rel),tuple(outs)))
  for z in [1,2,3,4,5]:
   q=copy.deepcopy(env)
   try:r=q.step(GameAction.from_id(z),data={})
   except:continue
   if r.state.name=="NOT_FINISHED":nxt.append((q,fh(r),oh+(obs,),ah+(z,)))
 nodes=nxt[:40]

st=ab_family_all(occ);groups=defaultdict(list)
for o in occ:groups[o.referent].append(o)

for ref,s in st.items():
 if s.minimal_separator_sets==((),):continue
 q=source_alias_classes(groups[ref],s)
 print("REF",ref)
 print(" MIN",s.minimal_separator_sets)
 print(" CLASSES",tuple(c.sources for c in q.alias_classes))
 _,mi=information_minimal_provenance(groups[ref],s)
 print(" INFO_MIN",tuple(c.sources for c in mi))

# Regression on the stable shallow-R referents.
rrefs=[(ref,s) for ref,s in st.items() if s.minimal_separator_sets==( ("A2",),("O1",),("O2",) )]
assert rrefs
for ref,s in rrefs:
 q=source_alias_classes(groups[ref],s)
 classes=[set(c.sources) for c in q.alias_classes]
 assert {("A2",),("O1",)} in classes
 assert {("O2",)} in classes
 assert len(classes)==2
print("PASS real DC22 partition-aware A/B provenance")
