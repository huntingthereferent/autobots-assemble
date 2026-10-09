from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import random,copy
P1=(4,4,4,1,1,1,4,3,2,2,4,3,1,4);P2=(4,4,4,1,1,4,4,1,4,3,3,1,4,4,3,3,3,3,1,4,4,1,4,2,4,3,3,2,4,4);P3=(1,1,4,1,4,1,4,2,2,3,2,4,4,4,4,1,3,3,3,3,1,1,1,4,2,2,2,3,1,1,1,1,4);P4=(1,1,3,4,1,4,1,1,3,2,3,3,2,2,2,4,4,4,1,1,3,3,1,4,2,3,1)
root=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
for z in P1+P2+P3+P4:root.step(GameAction.from_id(z),data={})
g=root._game
pads=g.vbelzuaian
START=(24,4,tuple((int(t.x),int(t.y)) for t in pads))
COLORS=tuple(int(t.pixels[1,1]) for t in pads)
def real(e):
 g=e._game;body=g.mwfajkguqx[g.vzvypfsnt]
 return (int(g.vzvypfsnt.y),len(body),tuple((int(t.x),int(t.y)) for t in g.vbelzuaian))
def fast(st,z):
 y,L,pads=st
 dy=-6 if z==1 else 6 if z==2 else 0
 dx=6 if z==4 else -6 if z==3 else 0
 nl=L+(1 if z==4 else -1 if z==3 else 0);ny=y+dy
 if nl<1 or nl>8 or ny<6 or ny>42:return st
 old=[(5+6*i,y) for i in range(L)]
 movers=old if z!=3 else old[1:]
 if z==4 and (5+6*L,y)==(29,24):return st
 if z in (1,2) and any(x==29 and ny==24 for x,yy in movers):return st
 pindex={p:i for i,p in enumerate(pads)}
 moved=set()
 def push(i,vis):
  if i in moved:return True
  if i in vis:return True
  vis.add(i)
  x,yy=pads[i];nx=x+dx;yy2=yy+dy
  if nx<11 or nx>47 or yy2<6 or yy2>42 or (nx,yy2)==(29,24):return False
  if (nx,yy2) in pindex and pindex[(nx,yy2)] not in moved:
   if not push(pindex[(nx,yy2)],vis):return False
  moved.update(vis)
  return True
 for x,yy in movers:
  for pos in ((x,yy),(x+dx,yy+dy)):
   i=pindex.get(pos)
   if i is not None and i not in moved:
    if not push(i,set()) and z in (1,2):return st
 pp=tuple((x+dx,yy+dy) if i in moved else (x,yy) for i,(x,yy) in enumerate(pads))
 return (ny,nl,pp)

from collections import deque
import time
T9=tuple(i for i,(x,y) in enumerate(START[2]) if y<53 and COLORS[i]==9)
T8=tuple(i for i,(x,y) in enumerate(START[2]) if y<53 and COLORS[i]==8)
def canon(st):
 y,L,pads=st
 return (y,L,tuple(sorted(pads[i] for i in T9)),tuple(sorted(pads[i] for i in T8)))
def win(st):
 y,L,pads=st
 cmap={(pads[i][0],pads[i][1]):COLORS[i] for i in T9+T8}
 hits=[cmap[(5+6*j,y)] for j in range(L) if (5+6*j,y) in cmap]
 return hits==[8,9,8]
seen={canon(START):0};states=[START];parents=[(-1,0)];depth=[0];queue=deque([0]);starttime=time.time();maximum=250000
while queue and len(states)<maximum:
 ix=queue.popleft();st=states[ix]
 if win(st):
  sol=[];j=ix
  while j:
   k,a=parents[j];sol.append(a);j=k
  sol=sol[::-1]
  print('SOLUTION',sol,'DEPTH',len(sol),'SEEN',len(seen),'ELAPSED',round(time.time()-starttime,2),flush=True)
  break
 for a in (1,2,3,4):
  ns=fast(st,a)
  k=canon(ns)
  if k in seen:continue
  j=len(states);seen[k]=j;states.append(ns);parents.append((ix,a));depth.append(depth[ix]+1);queue.append(j)
 if len(states)%20000<4:
  print('STATES',len(states),'D',depth[-1],'ELAPSED',round(time.time()-starttime,1),'QUEUE',len(queue),flush=True)
else:print('SEARCH_LIMIT',len(states),'QUEUE',len(queue),'DEPTH',depth[-1],'ELAPSED',round(time.time()-starttime,1),flush=True)
