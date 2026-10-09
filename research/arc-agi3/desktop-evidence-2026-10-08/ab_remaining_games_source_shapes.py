from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib,copy
from ab_family_all_minima import Occurrence,ab_family_all

GAMES=["m0r0","r11l","re86","s5i5","sb26","sc25","sk48","sp80","su15","tn36","tr87","tu93","vc33","wa30"]

def fh(r):
 if not getattr(r,"frame",None):return "EMPTY"
 try:return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]
 except:return hashlib.sha1(repr(r.frame).encode()).hexdigest()[:12]

a=Arcade(operation_mode=OperationMode.NORMAL)
for game in GAMES:
 try:root=a.make(game)
 except Exception as ex:
  print(game,"MAKE_FAIL",type(ex).__name__,flush=True);continue
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
  nodes=nxt[:40]
 try:
  st=ab_family_all(occ)
  fams=sorted({s.minimal_separator_sets for s in st.values() if s.minimal_separator_sets!=((),)},key=repr)
  print(game,"RAW",len(st),"SPLIT",sum(1 for s in st.values() if s.minimal_separator_sets!=((),)),"FAMS",fams,flush=True)
 except Exception as ex:
  print(game,"INSUFFICIENT",type(ex).__name__,str(ex)[:100],flush=True)
