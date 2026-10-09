from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import deque
a=Arcade(operation_mode=OperationMode.NORMAL)
BASE=[3]*5+[2]*10+[7,5]
def comp72(A,c):
 # components 4-neighbor
 seen=set(); out=[]
 ys,xs=np.where(A==c)
 pts=set(zip(xs.tolist(),ys.tolist()))
 for p in list(pts):
  if p in seen: continue
  q=[p];seen.add(p);cc=[]
  while q:
   x,y=q.pop();cc.append((x,y))
   for n in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
    if n in pts and n not in seen:seen.add(n);q.append(n)
  if len(cc)>=40: out.append(cc)
 return out
def bbox(cc): return (min(x for x,y in cc),max(x for x,y in cc),min(y for x,y in cc),max(y for x,y in cc))
# recursive correspondence controller: receiver anchor from B8 fixed 11 component bbox 3..17,42..53.
e=a.make('ar25');o=None
for z in BASE:o=e.step(GameAction.from_id(z),data={})
A=o.frame[0].copy()
recv=(3,42)
seq=[]
print("START")
for step in range(40):
 cs=comp72(A,4)
 if not cs: print("NO_MOVER",step);break
 # choose large color4 component nearest 72
 cc=min(cs,key=lambda q:abs(len(q)-72)); b=bbox(cc); ax,ay=b[0],b[2]
 dx,dy=recv[0]-ax,recv[1]-ay
 print(step,"bbox",b,"n",len(cc),"delta",dx,dy,"lvl",o.levels_completed)
 if o.levels_completed>1: print("SOLVED",seq);break
 # movement witnessed at B8: A4 decreases x; A3 increases x; A2 increases y; A1 decreases y.
 # Re-evaluate after EVERY returned board, prioritize larger remaining axis in lattice units.
 if dx<0: act=4
 elif dx>0: act=3
 elif dy>0: act=2
 elif dy<0: act=1
 else:
  print("REGISTERED_NO_CLOSE",seq); break
 o=e.step(GameAction.from_id(act),data={}); seq.append(act); A=o.frame[0].copy()
 if o.levels_completed>1: print("SOLVED_AFTER",step+1,seq,"lvl",o.levels_completed);break
 if str(o.state).endswith("GAME_OVER"): print("GAME_OVER",seq);break
print("FINAL",seq,o.levels_completed,o.state)
