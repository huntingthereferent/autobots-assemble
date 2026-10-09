from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,hashlib,numpy as np,collections,time
def H(r):return (hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12],r.state.name,r.levels_completed)
games=["ft09","lp85","r11l","s5i5","tn36","vc33"]
arc=Arcade(operation_mode=OperationMode.NORMAL)
for name in games:
 root=arc.make(name);outs=collections.defaultdict(list);errs=collections.Counter();t=time.time()
 for y in range(64):
  for x in range(64):
   q=copy.deepcopy(root)
   try:r=q.step(GameAction.ACTION6,data={"x":x,"y":y});outs[H(r)].append((x,y))
   except Exception as e:errs[type(e).__name__]+=1
 print("\nGAME",name,"CLASSES",len(outs),"ERRS",dict(errs),"SEC",round(time.time()-t,2),flush=True)
 for i,(k,pts) in enumerate(sorted(outs.items(),key=lambda kv:-len(kv[1]))[:30]):
  print(" C",i,"N",len(pts),"REP",pts[0],"KEY",k)
