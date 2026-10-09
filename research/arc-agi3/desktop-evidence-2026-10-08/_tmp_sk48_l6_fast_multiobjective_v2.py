from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,random,gc,time
random.seed(4804)
p1=(4,4,4,1,1,1,4,3,2,2,4,3,1,4)
p2=(4,4,4,1,1,4,4,1,4,3,3,1,4,4,3,3,3,3,1,4,4,1,4,2,4,3,3,2,4,4)
p3=(1,1,4,1,4,1,4,2,2,3,2,4,4,4,4,1,3,3,3,3,1,1,1,4,2,2,2,3,1,1,1,1,4)
p4=(1,1,3,4,1,4,1,1,3,2,3,3,2,2,2,4,4,4,1,1,3,3,1,4,2,3,1)
p5=(3,1,3,3,4,4,4,2,1,4,4,1,4,2,3,3,3,2,2,3,2,4,4,4,4,3,1,4,4,3,2,4,1,3,3,3,3,1,3,3,3,4,1,4,4,4,4,4,1,4,2,3,3,3,3,3,3,2,4,4,2,4,4,4,4)
prefix=p1+p2+p3+p4+p5
root=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
for a in prefix:root.step(GameAction.from_id(a),data={})
g=root._game
pairs=list(g.xpmcmtbcv.items())
import random
TOP=tuple(i for i,t in enumerate(g.vbelzuaian) if t.y<53)
def real(e):
 g=e._game
 k=list(g.xpmcmtbcv)
 return (int(g.vzvypfsnt is k[1]),int(k[0].y),len(g.mwfajkguqx[k[0]]),int(k[1].x),len(g.mwfajkguqx[k[1]]),tuple((int(g.vbelzuaian[i].x),int(g.vbelzuaian[i].y)) for i in TOP))
START=real(root)
def fast(st,a):
 active,hy,hl,vx,vl,pads=st
 if a==6:return (1-active,hy,hl,vx,vl,pads)
 if active==0:
  dx,dy={1:(0,-6),2:(0,6),3:(-6,0),4:(6,0)}[a]
  ahead=(1,0); y=hy;length=hl;start=(5,hy);grow=a==4;shrink=a==3;perp=a in (1,2)
 else:
  dx,dy={1:(0,-6),2:(0,6),3:(-6,0),4:(6,0)}[a]
  ahead=(0,1); y=2;length=vl;start=(vx,2);grow=a==2;shrink=a==1;perp=a in (3,4)
 if shrink and length==1:return st
 nlen=length+(1 if grow else -1 if shrink else 0)
 nx=vx+dx if active==1 and perp else vx
 ny=hy+dy if active==0 and perp else hy
 old=[(start[0]+6*ahead[0]*i,start[1]+6*ahead[1]*i) for i in range(length)]
 movers=old[1:] if shrink else old
 def wall(pos):
  x,y=pos
  return x<11 or x>47 or y<8 or y>44 or pos==(29,26)
 if grow:
  dest=(start[0]+ahead[0]*6*length,start[1]+ahead[1]*6*length)
  if wall(dest):return st
 if perp:
  for x,y in old:
   if wall((x+dx,y+dy)) and not wall((x,y)):return st
 if active==0 and perp and (ny<8 or ny>44):return st
 if active==1 and perp and (nx<11 or nx>47):return st
 pindex={p:i for i,p in enumerate(pads)}
 moved=set()
 def push(i, stack):
  if i in moved:return True
  if i in stack:return True
  stack.add(i)
  x,y=pads[i];dest=(x+dx,y+dy)
  if wall(dest):return False
  other=([(vx,2+6*j) for j in range(vl)] if active==0 else [(5+6*j,hy) for j in range(hl)])
  if dest in other or (x,y) in other:return False
  t=pindex.get(dest)
  if t is not None and t not in moved and not push(t,stack):return False
  moved.update(stack)
  return True
 for x,y in movers:
  for pos in ((x,y),(x+dx,y+dy)):
   i=pindex.get(pos)
   if i is not None and i not in moved:
    ok=push(i,set())
    if not ok and perp:return st
 pp=tuple((x+dx,y+dy) if i in moved else (x,y) for i,(x,y) in enumerate(pads))
 return (active,ny,nlen,nx,vl,pp) if active==0 else (active,hy,hl,nx,nlen,pp)
from collections import defaultdict
import time,random
random.seed(603)
C=(8,8,9,8,9,9)
INDS9=(2,4,5);INDS8=(0,1,3)
def hits(st):
 _,hy,hl,vx,vl,pads=st
 mp={pads[i]:C[i] for i in range(6)}
 h=tuple(mp[(5+6*j,hy)] for j in range(hl) if (5+6*j,hy) in mp)
 v=tuple(mp[(vx,2+6*j)] for j in range(vl) if (vx,2+6*j) in mp)
 return h,v
def canon(st):
 a,hy,hl,vx,vl,p=st
 return (a,hy,hl,vx,vl,tuple(sorted(p[i] for i in INDS9)),tuple(sorted(p[i] for i in INDS8)))
def value(st):
 a,hy,hl,vx,vl,p=st
 h,v=hits(st)
 g9=sum(z==9 for z in h[:3]); g8=sum(z==8 for z in v[:3])
 w9=sum(z!=9 for z in h[:3]); w8=sum(z!=8 for z in v[:3])
 dp9=sum(min(abs(p[i][0]-(5+6*j))+abs(p[i][1]-hy) for j in range(hl)) for i in INDS9)
 dp8=sum(min(abs(p[i][0]-vx)+abs(p[i][1]-(2+6*j)) for j in range(vl)) for i in INDS8)
 row9=sum(p[i][1]==hy for i in INDS9)
 col8=sum(p[i][0]==vx for i in INDS8)
 moved=sum(p[i]!=START[5][i] for i in range(6))
 sc=(g9+g8)*220-(w9+w8)*115-(dp9+dp8)*1.7+row9*22+col8*22+moved*2
 cl=(min(3,g9),min(3,g8),a)
 return sc+random.random()*12,cl,h,v
start=time.time();seen={canon(START)}
beam=[(START,())];best=(-1e20,None,None,None);WIDTH=4500
for depth in range(1,101):
 bins=defaultdict(list);sol=None
 for st,path in beam:
  for a in (1,2,3,4,6):
   ns=fast(st,a)
   k=canon(ns)
   if k in seen:continue
   seen.add(k); pp=path+(a,)
   sc,cl,h,v=value(ns)
   if len(h)>=3 and h[:3]==(9,9,9) and len(v)>=3 and v[:3]==(8,8,8):
    sol=(pp,ns,len(seen));break
   if sc>best[0]:best=(sc,pp,h,v)
   bins[cl].append((sc,ns,pp))
  if sol:break
 if sol:
  print('CANDIDATE_PATH',sol[0],'DEPTH',len(sol[0]),'SEEN',sol[2],'HITS',hits(sol[1]),'ELAPSED',round(time.time()-start,2),flush=True)
  break
 if not bins:print('EXHAUSTED',depth,len(seen),best,flush=True);break
 nbin=len(bins);quota=max(20,WIDTH//nbin)
 nexts=[]
 for cl,vv in bins.items():
  vv.sort(key=lambda z:z[0],reverse=True)
  nexts.extend(vv[:quota])
 nexts.sort(key=lambda z:z[0],reverse=True)
 beam=[(s,p) for sc,s,p in nexts[:WIDTH]]
 if depth%5==0 or depth<=5:
  print('DEPTH',depth,'STATES',len(seen),'BINS',nbin,'BEAM',len(beam),'BEST',(round(best[0],1),best[2],best[3]),'SEC',round(time.time()-start,1),flush=True)
 if time.time()-start>88 or len(seen)>2200000:
  print('BOUNDARY',depth,len(seen),'BEST',best,'ELAPSED',round(time.time()-start,2),flush=True);break
