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

import random,time,collections
random.seed(501)
T9=tuple(i for i,(x,yy) in enumerate(START[2]) if yy<53 and COLORS[i]==9)
T8=tuple(i for i,(x,yy) in enumerate(START[2]) if yy<53 and COLORS[i]==8)
def canon(st):
 y,L,p=st
 return y,L,tuple(sorted(p[i] for i in T9)),tuple(sorted(p[i] for i in T8))
def contacts(st,yy,ll):
 p=st[2]; m={p[i]:COLORS[i] for i in T9+T8}
 return tuple(m[(5+6*j,yy)] for j in range(ll) if (5+6*j,yy) in m)
def ed(s,t=(8,9,8)):
 dp=list(range(len(t)+1))
 for i,a in enumerate(s,1):
  nd=[i]+[0]*len(t)
  for j,b in enumerate(t,1):
   nd[j]=min(nd[j-1]+1,dp[j]+1,dp[j-1]+int(a!=b))
  dp=nd
 return dp[-1]
def score(st):
 y,L,p=st
 present=contacts(st,y,L)
 if present==(8,9,8):return 10000
 d=ed(present); pref=0
 for a,b in zip(present,(8,9,8)):
  if a!=b:break
  pref+=1
 active=260-75*d+25*pref+15*len(present)
 best=-999
 for yy in range(6,43,6):
  for ll in range(2,9):
   cc=contacts(st,yy,ll)
   if not cc:continue
   dist=ed(cc)
   pr=0
   for a,b in zip(cc,(8,9,8)):
    if a!=b:break
    pr+=1
   q=280-72*dist+26*pr+10*len(cc)-abs(yy-y)*0.8-abs(ll-L)*2
   if q>best:best=q
 # sparse but useful: some 8 and 9 must coexist at a row without too many other pads
 yrows=collections.defaultdict(list)
 for i in T9+T8:yrows[p[i][1]].append((p[i][0],COLORS[i]))
 crossing=0
 for row, vals in yrows.items():
  vals.sort();c=[v for xx,v in vals]
  for j,a in enumerate(c):
   if a==8 and 9 in c[j+1:]: crossing=max(crossing,6)
 return max(active,best)+crossing+random.random()*8
seen={canon(START)}
beam=[(START,())];starttime=time.time()
best=(-1e9,None,None)
for d in range(1,91):
 nexts=[]
 for st,p in beam:
  for a in (1,2,3,4):
   ns=fast(st,a)
   key=canon(ns)
   if key in seen:continue
   seen.add(key)
   path=p+(a,)
   if contacts(ns,ns[0],ns[1])==(8,9,8):
    print('CANDIDATE',path,'DEPTH',len(path),'STATES',len(seen),'ELAPSED',round(time.time()-starttime,2),flush=True);quit()
   v=score(ns)
   if v>best[0]:best=(v,path,contacts(ns,ns[0],ns[1]))
   nexts.append((v,ns,path))
 if not nexts:print('EXHAUSTED',d,len(seen),best,flush=True);break
 nexts.sort(key=lambda x:x[0],reverse=True)
 beam=[(st,p) for v,st,p in nexts[:2200]]
 if d%5==0 or d<5:print('DEPTH',d,'SEEN',len(seen),'CANDIDATES',len(nexts),'BEST',best,'ELAPSED',round(time.time()-starttime,2),flush=True)
 if time.time()-starttime>75:print('BOUND',d,best,flush=True);break
