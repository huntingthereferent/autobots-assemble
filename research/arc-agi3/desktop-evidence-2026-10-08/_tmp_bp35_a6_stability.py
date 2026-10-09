from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,hashlib,numpy as np,collections,time
def H(r): return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]
arc=Arcade(operation_mode=OperationMode.NORMAL);root=arc.make("bp35")
states=[("ROOT",root)]
for z in [3,4,7]:
 q=copy.deepcopy(root);q.step(GameAction.from_id(z),data={});states.append((f"S{z}",q))
for lab,e in states:
 t=time.time();outs=collections.defaultdict(list)
 for y in range(64):
  for x in range(64):
   q=copy.deepcopy(e);r=q.step(GameAction.ACTION6,data={"x":x,"y":y});outs[H(r)].append((x,y))
 print(lab,"CLASSES",len(outs),"SEC",round(time.time()-t,2))
 for h,pts in sorted(outs.items(),key=lambda kv:-len(kv[1])):
  print(" ",len(pts),pts[0],h)
