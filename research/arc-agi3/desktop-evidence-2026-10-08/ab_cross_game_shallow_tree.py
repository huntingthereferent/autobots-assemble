from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib,copy
from collections import defaultdict
from ab_family_closure import Occurrence,ab_family

def fh(r):
 if not getattr(r,"frame",None):return "EMPTY"
 return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]

a=Arcade(operation_mode=OperationMode.NORMAL)
for game in ["bp35","cd82","dc22","ft09","g50t","ka59"]:
 try:root=a.make(game)
 except Exception as ex:
  print(game,"MAKE_FAIL");continue
 # breadth-first public tree to depth 3 using actions 1..5
 nodes=[(root,"START",())]
 occ=[]
 for depth in range(3):
  nxt=[]
  for env,obs,hist in nodes:
   # response signature and children in one pass
   outs=[]
   for z in [1,2,3,4,5]:
    q=copy.deepcopy(env)
    try:r=q.step(GameAction.from_id(z),data={})
    except Exception:
     outs.append((z,"ERR"));continue
    no=fh(r);outs.append((z,no,r.levels_completed,r.state.name))
    if r.state.name=="NOT_FINISHED":nxt.append((q,no,hist+(obs,)))
   rel=tuple((f"prev{i}",hist[-i] if len(hist)>=i else None) for i in range(1,4))
   occ.append(Occurrence(obs,rel,tuple(outs)))
  nodes=nxt[:80]
 if not occ:
  print(game,"NO_DATA");continue
 try:s=ab_family(occ)
 except Exception as ex:
  print(game,"AB_FAIL",type(ex).__name__,str(ex)[:70]);continue
 split={k:v for k,v in s.items() if v.retained_names}
 print(game,"WIT",len(occ),"RAW",len(s),"SPLIT",len(split))
 for ref,st in list(split.items())[:8]:print(" ",ref,"=>",st.retained_names)
 if split:break
