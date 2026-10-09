"""Check whether equivalent A/B source atoms induce the same occurrence partition or only the same future partition."""

# Re-run bounded depth-5 DC22 and collect raw witness relation values.
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib,copy
from collections import defaultdict
from ab_family_all_minima import Occurrence,ab_family_all

def fh(r):
 if not getattr(r,"frame",None):return "EMPTY"
 return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]

def collect(game):
 a=Arcade(operation_mode=OperationMode.NORMAL);root=a.make(game)
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
 return occ

def partition(group,name):
 buckets=defaultdict(list)
 for i,o in enumerate(group):
  buckets[dict(o.relations)[name]].append(i)
 return frozenset(frozenset(v) for v in buckets.values())

def future_partition(group,name):
 buckets=defaultdict(set)
 for o in group:
  buckets[dict(o.relations)[name]].add(o.future)
 return {k:len(v) for k,v in buckets.items()}

for game in ["dc22","sk48"]:
 occ=collect(game);st=ab_family_all(occ)
 groups=defaultdict(list)
 for o in occ:groups[o.referent].append(o)
 print("\nGAME",game)
 for ref,s in st.items():
  if s.minimal_separator_sets==((),):continue
  atoms=sorted({x for edge in s.minimal_separator_sets for x in edge if len(edge)==1})
  # compare every singleton minimal source pair.
  single=[edge[0] for edge in s.minimal_separator_sets if len(edge)==1]
  if len(single)>=2:
   print("REF",ref,"SINGLE",single)
   for i,a in enumerate(single):
    for b in single[i+1:]:
     same=partition(groups[ref],a)==partition(groups[ref],b)
     print(" ",a,b,"SAME_OCC_PARTITION",same)
