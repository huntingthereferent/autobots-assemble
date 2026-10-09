from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import deque
a=Arcade(operation_mode=OperationMode.NORMAL)
ROOT=[3]*5+[2]*10+[7,5]+[2]*4
def run(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return o.frame[0],o
R,_=run(ROOT); origN=R==11
# Exact L1 positive 24 mask normalized
P,_=run([3]*5+[2]*9);Q,_=run([3]*5+[2]*10)
m=np.argwhere((P==11)&(Q==4)); y0,x0=m.min(0)
TARGET=set((int(x-x0),int(y-y0)) for y,x in m)
# compare current yellow-on-original-navy mask under translations and D4 transforms to positive mask
def pts(A): return set((int(x),int(y)) for y,x in np.argwhere(origN&(A==4)))
def norm(S):
 if not S:return set()
 x0=min(x for x,y in S);y0=min(y for x,y in S);return set((x-x0,y-y0) for x,y in S)
def transforms(S):
 if not S:return []
 S=norm(S); mx=max(x for x,y in S);my=max(y for x,y in S)
 fs=[S,{(mx-x,y) for x,y in S},{(x,my-y) for x,y in S},{(mx-x,my-y) for x,y in S}]
 return [norm(z) for z in fs]
q=deque([[]]); seen=set(); walls=0
while q and walls<120:
 h=q.popleft();A,o=run(ROOT+h); k=A.tobytes()
 if k in seen:continue
 seen.add(k)
 S=pts(A); match=len(S)==24 and any(t==TARGET for t in transforms(S))
 if h:
  walls+=1
  if len(S)>=16 or match: print('W',walls,'h',h,'lvl',o.levels_completed,'YN',len(S),'MATCH',match,'BLACK',int(np.sum(A==0)))
 if o.levels_completed>1:
  print('SOLVED',ROOT+h);break
 if match:
  print('TARGET_STATE',ROOT+h)
  # immediately test every simple continuation from exact L mask
  for z in [1,2,3,4,5,7]:
   B,r=run(ROOT+h+[z]);print(' TARGET+',z,'lvl',r.levels_completed,'YN',len(pts(B)),'black',int(np.sum(B==0)))
   if r.levels_completed>1:print('SOLVED',ROOT+h+[z]);raise SystemExit
 if len(h)<6:
  for z in [1,2,3,4,5,7]:q.append(h+[z])
print('DONE',walls,'states',len(seen))
