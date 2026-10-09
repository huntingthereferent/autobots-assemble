from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL)
BASE=[3]*5+[2]*10+[7,5]
# Completion-referent test: Level1 closes when the two moving halves reach fixed counterparts together.
# At B8 derive fixed large components and test whether coupled movers can simultaneously align under reachable translations.
def state(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return e,o,o.frame[0].copy()
def bbox_color(A,c,minn=20):
 pts=set((int(x),int(y)) for y,x in zip(*np.where(A==c))); seen=set(); out=[]
 for p in list(pts):
  if p in seen:continue
  q=[p];seen.add(p);cc=[]
  while q:
   x,y=q.pop();cc.append((x,y))
   for n in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
    if n in pts and n not in seen:seen.add(n);q.append(n)
  if len(cc)>=minn: out.append((len(cc),(min(x for x,y in cc),max(x for x,y in cc),min(y for x,y in cc),max(y for x,y in cc))))
 return sorted(out,reverse=True)
# Test the earned coupled-state lattice: horizontal positions reachable -1..+ several, vertical -6..+11.
# For each canonical endpoint, A5 and A7 are completion checks/re-expression, not arbitrary long histories.
walls=0
for hact,hn in [(4,1),(None,0),(3,1),(3,2),(3,3),(3,4),(3,5),(3,6)]:
 for vact,vn in [(1,6),(1,4),(1,2),(None,0),(2,2),(2,4),(2,6),(2,8),(2,10),(2,11)]:
  seq=BASE+(([hact]*hn) if hact else [])+(([vact]*vn) if vact else [])
  e,o,A=state(seq)
  if o.levels_completed>1: print("SOLVED_ENDPOINT",seq);raise SystemExit
  # closure-bearing transforms A5/A7 at relational endpoint
  for check in [5,7]:
   oo=e.step(GameAction.from_id(check),data={})
   walls+=1
   if oo.levels_completed>1:
    print("SOLVED_CHECK",seq+[check],"walls",walls);raise SystemExit
   # recreate so checks are independent
   e,o,A=state(seq)
print("WALLS",walls,"NO_CLOSE")
# print structures at central and extrema to compare simultaneous fixed relation
for name,seq in [('LEFT_Y42',BASE+[4]+[2]*8),('CENTER_Y42',BASE+[2]*8),('IN1_Y42',BASE+[3]+[2]*8),('IN4_Y42',BASE+[3]*4+[2]*8)]:
 e,o,A=state(seq)
 print(name,"lvl",o.levels_completed,"c4",bbox_color(A,4),"c5",bbox_color(A,5),"c11",bbox_color(A,11))
