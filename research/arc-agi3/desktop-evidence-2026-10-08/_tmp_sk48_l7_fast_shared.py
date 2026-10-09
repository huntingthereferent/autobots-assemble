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
p6=(4,4,2,4,6,2,2,4,4,2,1,4,2,3,1,3,2,6,4,4,4,3,3,3,3,2,2,4,1,3,1,4,6,2,2,2)
root=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
for a in p1+p2+p3+p4+p5+p6:
 if a==6:
  gg=root._game;other=next(k for k in gg.xpmcmtbcv if k!=gg.vzvypfsnt)
  root.step(GameAction.ACTION6,data={'x':int(other.x+2),'y':int(other.y+2)})
 else:root.step(GameAction.from_id(a),data={})
g=root._game
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
  return x<11 or x>47 or y<8 or y>44
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
  if (active==0 and dx!=0) or (active==1 and dy!=0):
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
random.seed(707)
COL=(9,9,8,8,14);WANT=((9,14,9),(8,14,8))
def hits(st):
 a,hy,hl,vx,vl,pads=st
 mp={pads[i]:COL[i] for i in range(len(COL))}
 h=tuple(mp[(5+6*j,hy)] for j in range(hl) if (5+6*j,hy) in mp)
 v=tuple(mp[(vx,2+6*j)] for j in range(vl) if (vx,2+6*j) in mp)
 return h,v
def canon(st):
 a,hy,hl,vx,vl,p=st
 return (a,hy,hl,vx,vl,tuple(sorted(p[i] for i in (0,1))),tuple(sorted(p[i] for i in (2,3))),p[4])
def value(st):
 a,hy,hl,vx,vl,p=st
 h,v=hits(st)
 good=sum(i<3 and z==WANT[0][i] for i,z in enumerate(h[:3]))+sum(i<3 and z==WANT[1][i] for i,z in enumerate(v[:3]))
 bad=sum(i<3 and z!=WANT[0][i] for i,z in enumerate(h[:3]))+sum(i<3 and z!=WANT[1][i] for i,z in enumerate(v[:3]))
 d9=sum(min(abs(p[i][0]-(5+6*j))+abs(p[i][1]-hy) for j in range(hl)) for i in (0,1))
 d8=sum(min(abs(p[i][0]-vx)+abs(p[i][1]-(2+6*j)) for j in range(vl)) for i in (2,3))
 d14=abs(p[4][0]-vx)+abs(p[4][1]-hy)
 cross=(vx==p[4][0] and hy==p[4][1])
 hcross=(vx-5)%6==0 and (vx-5)//6<hl
 vcross=(hy-2)%6==0 and (hy-2)//6<vl
 sc=good*230-bad*105-(d9+d8)*1.3-d14*3.5+cross*200+(hcross and vcross)*70
 cl=(sum(i<3 and z==WANT[0][i] for i,z in enumerate(h[:3])),sum(i<3 and z==WANT[1][i] for i,z in enumerate(v[:3])),int(cross),a)
 return sc+random.random()*12,cl,h,v
start=time.time();seen={canon(START)};beam=[(START,())];best=(-1e20,None,None,None);WIDTH=5000
for depth in range(1,131):
 bins=defaultdict(list);sol=None
 for st,path in beam:
  for a in (1,2,3,4,6):
   ns=fast(st,a);k=canon(ns)
   if k in seen:continue
   seen.add(k);pp=path+(a,)
   sc,cl,h,v=value(ns)
   if len(h)>=3 and h[:3]==WANT[0] and len(v)>=3 and v[:3]==WANT[1]:
    sol=(pp,ns,len(seen));break
   if sc>best[0]:best=(sc,pp,h,v)
   bins[cl].append((sc,ns,pp))
  if sol:break
 if sol:
  print('CANDIDATE_PATH',sol[0],'DEPTH',len(sol[0]),'SEEN',sol[2],'HITS',hits(sol[1]),'ELAPSED',round(time.time()-start,2),flush=True);break
 if not bins:print('EXHAUSTED',depth,len(seen),best,flush=True);break
 quota=max(15,WIDTH//len(bins));nexts=[]
 for cl,ss in bins.items():
  ss.sort(key=lambda x:x[0],reverse=True);nexts.extend(ss[:quota])
 nexts.sort(key=lambda x:x[0],reverse=True);beam=[(ns,p) for sc,ns,p in nexts[:WIDTH]]
 if depth%5==0 or depth<=5:
  print('DEPTH',depth,'STATES',len(seen),'BINS',len(bins),'BEAM',len(beam),'BEST',(round(best[0],1),best[2],best[3]),'SEC',round(time.time()-start,1),flush=True)
 if time.time()-start>95 or len(seen)>1600000:
  print('BOUNDARY',depth,len(seen),'BEST',best,'ELAPSED',round(time.time()-start,2),flush=True);break
