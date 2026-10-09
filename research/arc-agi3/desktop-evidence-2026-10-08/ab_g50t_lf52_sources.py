from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib,copy
from ab_family_all_minima import Occurrence,ab_family_all

def fh(r):
 if not getattr(r,"frame",None):return "EMPTY"
 return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]

def scan(game):
 a=Arcade(operation_mode=OperationMode.NORMAL);root=a.make(game)
 nodes=[(root,"START",(),())];occ=[]
 for depth in range(3):
  nxt=[]
  for env,obs,oh,ah in nodes:
   outs=[]
   for z in [1,2,3,4,5]:
    q=copy.deepcopy(env)
    try:r=q.step(GameAction.from_id(z),data={});outs.append((z,fh(r),r.levels_completed,r.state.name))
    except Exception as ex:outs.append((z,"ERR",type(ex).__name__,None))
   rel=[]
   for i in range(1,4):
    rel += [(f"prev_obs{i}",oh[-i] if len(oh)>=i else None),(f"prev_action{i}",ah[-i] if len(ah)>=i else None)]
   occ.append(Occurrence(obs,tuple(rel),tuple(outs)))
   for z in [1,2,3,4,5]:
    q=copy.deepcopy(env)
    try:r=q.step(GameAction.from_id(z),data={})
    except:continue
    if r.state.name=="NOT_FINISHED":nxt.append((q,fh(r),oh+(obs,),ah+(z,)))
  nodes=nxt[:80]
 st=ab_family_all(occ)
 print(game.upper(),"RAW",len(st))
 for ref,s in st.items():
  if s.minimal_separator_sets!=((),):
   print(" ",ref,"=>",s.minimal_separator_sets)
 return st

scan("g50t")
scan("lf52")
