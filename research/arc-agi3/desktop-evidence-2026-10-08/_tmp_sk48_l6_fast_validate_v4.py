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
print('START',START,flush=True)
random.seed(6606)
count=0;mis=[]
for case in range(150):
 e=copy.deepcopy(root);st=START;path=[]
 for j in range(40):
  a=random.choice((1,2,3,4,6))
  path.append(a)
  g=e._game
  if a==6:
   other=next(k for k in g.xpmcmtbcv if k!=g.vzvypfsnt)
   e.step(GameAction.ACTION6,data={'x':int(other.x+2),'y':int(other.y+2)})
  else:e.step(GameAction.from_id(a),data={})
  st=fast(st,a);rr=real(e);count+=1
  if st!=rr:
   mis.append((case,j,a,tuple(path),st,rr))
   if len(mis)>=7:break
 if len(mis)>=7:break
print('CHECKS',count,'FAILS',len(mis),flush=True)
for item in mis:print('MISMATCH',item,flush=True)
