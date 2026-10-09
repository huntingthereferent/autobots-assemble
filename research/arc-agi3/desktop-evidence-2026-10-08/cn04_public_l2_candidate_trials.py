from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import Counter

PLANS=[
{1:(0,12,5),2:(0,8,4),0:(0,7,2),3:(1,14,7)},
{1:(0,12,5),2:(0,8,4),0:(0,7,2),3:(3,16,7)},
{1:(0,12,4),2:(0,8,3),0:(0,7,1),3:(1,14,6)},
{1:(0,12,4),2:(0,8,3),0:(0,7,1),3:(3,16,6)},
{1:(0,11,4),2:(0,7,3),0:(0,6,1),3:(1,13,6)},
{1:(0,11,4),2:(0,7,3),0:(0,6,1),3:(3,15,6)},
]
a=Arcade(operation_mode=OperationMode.NORMAL)

def pg(e):
 r=e.step(GameAction.from_id(7),data={})
 if not r.frame:
  return None,r
 F=np.array(r.frame[0],int)
 G=np.array([[F[2+3*y,2+3*x] for x in range(20)] for y in range(20)],int)
 return G,r

def seg(G):
 bg=Counter(G.flatten().tolist()).most_common(1)[0][0]
 S={(x,y) for y in range(20) for x in range(20) if int(G[y,x])!=bg}
 out=[]
 while S:
  p=S.pop();q=[p];c={p}
  while q:
   x,y=q.pop()
   for n in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
    if n in S:S.remove(n);c.add(n);q.append(n)
  vals={int(G[y,x]) for x,y in c};m={(x,y) for x,y in c if int(G[y,x])==8}
  if m:out.append((c,vals,(min(x for x,y in c),min(y for x,y in c),max(x for x,y in c),max(y for x,y in c))))
 return out

def click(e,x,y):e.step(GameAction.from_id(6),data={"x":2+3*x,"y":2+3*y})

def l2():
 e=a.make("cn04");click(e,13,9);e.step(GameAction.from_id(5),data={})
 for _ in range(10):e.step(GameAction.from_id(3),data={})
 e.step(GameAction.from_id(1),data={})
 return e

def selbox(e):
 G,r=pg(e)
 if G is None:
  return None,r
 s=[o for o in seg(G) if 0 in o[1]]
 assert len(s)==1
 return s[0][2],r

def movebox(e,gx,gy):
 r=None
 while True:
  sb,pr=selbox(e)
  if sb is None:return pr
  if sb[0]==gx:break
  r=e.step(GameAction.from_id(4 if gx>sb[0] else 3),data={})
  if r.levels_completed>1:return r
 while True:
  sb,pr=selbox(e)
  if sb is None:return pr
  if sb[1]==gy:break
  r=e.step(GameAction.from_id(2 if gy>sb[1] else 1),data={})
  if r.levels_completed>1:return r
 return r

for j,p in enumerate(PLANS):
 e=l2();G,_=pg(e);objs=seg(G);objs.sort(key=lambda o:(o[2][1],o[2][0]))
 clicks=[]
 for c,vals,b in objs:
  ordinary=[q for q in c if int(G[q[1],q[0]])!=8]
  clicks.append(sorted(ordinary or list(c))[0])
 r=None
 for idx in [1,2,0,3]:
  cx,cy=clicks[idx];click(e,cx,cy)
  k,gx,gy=p[idx]
  for _ in range(k):
   r=e.step(GameAction.from_id(5),data={})
   if r.levels_completed>1:break
  if r is not None and r.levels_completed>1:break
  r=movebox(e,gx,gy) or r
  if r is not None and r.levels_completed>1:break
 if r is None:_,r=pg(e)
 print("CAND",j,"LC",r.levels_completed,"STATE",r.state.name,flush=True)
