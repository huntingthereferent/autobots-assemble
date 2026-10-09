from arc_agi import Arcade,OperationMode
from arcengine import GameAction
p1=(3,3,3,1,1,1,1,4,4,4,1,1,1)
p2=(1,4,1,1,1,1,1,4,4,2,4,2,2,2,2,2,2,1,2,2,3,3,4,1,4,1,1,1,1,1,1,1,3,3,3,3,3,3,2,3,2,2,2,2,2)
p3=(1,1,1,1,1,1,1,1,3,2,2,2,2,2,2,2,2,1,1,1,3,3,1,4,4,4,4,4,4,4,1,1,1,3,1,2,1,4,2)
p4=(3,3,3,2,2,2,3,2,2,3,3,1,2,1,2,1,2,1,1,3,3,1,2,3,3,1,1,1,2,2,4,1,1,1,1,4,1,4,1,1,3,3,3)
p5=(1,3,1,1,3,3,3,4,3,4,3,4,1,1,3,3,3,3,1,3,3,3,4,4,2,2,2,2,2,4,4,3,2,2,4,2,4,4,4,4,4,4,4,1)
p6=(1,1,2,1,2,4,4,1,4,1,1,1,3,3,4,4,1,1,4,4,1,1,4,2,2,1,1,3,1,2,3,3,3,3,1,2,3,3,2,2,2,2,1,4,4,4,3,3,3,1,1,1,1,1,1,4,4,4,4,4,4,2,4,4,1,1,4,2,2,2,2,2)
from collections import deque
import time
e=Arcade(operation_mode=OperationMode.NORMAL).make('ls20')
for a in p1+p2+p3+p4+p5+p6:e.step(GameAction.from_id(a),data={})
g=e._game
wall={(s.x,s.y) for s in g.current_level.get_sprites_by_tag('ihdgageizm')}
refills=[(s.x-1,s.y-1) for s in g.current_level.get_sprites_by_tag('npxgalaybz')]
color={(s.x,s.y) for s in g.current_level.get_sprites_by_tag('soyhouuebz')}
shape={(s.x,s.y) for s in g.current_level.get_sprites_by_tag('ttfwljgohq')}
launcher={}
for p in g.hasivfwip:
 n=p.ullzqnksoj(g.gudziatsk)
 orig=(p.sprite.x+p.dx,p.sprite.y+p.dy)
 launcher[orig]=(orig[0]+5*p.dx*n,orig[1]+5*p.dy*n)
rotor=g.wsoslqeku[0]
rot_positions=[]
for t in range(10):
 rot_positions.append((rotor._sprite.x,rotor._sprite.y))
 rotor.step()
goal=(g.plrpelhym[0].x,g.plrpelhym[0].y,g.ehwheiwsk[0],g.yjdexjsoa[0],g.ldxlnycps[0])
start=(g.gudziatsk.x,g.gudziatsk.y,g.cklxociuu,g.hiaauhahz,g.fwckfzsyc,g._step_counter_ui.current_steps,0,0)
print('START',start,'GOAL',goal,'PICKUPS',refills,'LAUNCHERS',launcher,'ROTOR',rot_positions,'CONTROLS',shape,color,'COST',g._step_counter_ui.efipnixsvl,flush=True)
D=((1,0,-5),(2,0,5),(3,-5,0),(4,5,0))
def canon(st):
 x,y,r,c,sh,rem,mask,phase=st
 return (x,y,r,c,sh,mask,phase)
seen={canon(start):42};stlist=[start];parents=[(-1,0)];queue=deque([0]);tic=time.time();solution=-1
best=(-1,None)
while queue and len(stlist)<2200000:
 i=queue.popleft();st=stlist[i];x,y,r,c,sh,rem,mask,phase=st
 if seen.get(canon(st),-1)>rem:continue
 for a,dx,dy in D:
  nx,ny=x+dx,y+dy
  if not (9<=nx<=54 and 5<=ny<=50) or (nx,ny) in wall:continue
  nx,ny=launcher.get((nx,ny),(nx,ny))
  p=(phase+1)%10
  nr=(r+1)%4 if (nx,ny)==rot_positions[p] else r
  nc=(c+1)%4 if (nx,ny) in color else c
  nsh=(sh+1)%6 if (nx,ny) in shape else sh
  if (nx,ny)==goal[:2] and (nr,nc,nsh)!=goal[2:]:continue
  mm=mask;rr=rem-2
  for k,pos in enumerate(refills):
   if (nx,ny)==pos and not (mask>>k&1):
    mm|=1<<k;rr=42
  if rr<0:continue
  ns=(nx,ny,nr,nc,nsh,rr,mm,p)
  key=canon(ns)
  if seen.get(key,-1)>=rr:continue
  seen[key]=rr
  j=len(stlist);stlist.append(ns);parents.append((i,a));queue.append(j)
  if (nx,ny,nr,nc,nsh)==goal:
   solution=j;break
 if solution>=0:break
 if len(stlist)%250000<3:print('PROGRESS',len(stlist),'FRONTIER',len(queue),'SECONDS',round(time.time()-tic,1),flush=True)
 if time.time()-tic>115:print('TIME_BOUND',flush=True);break
if solution>=0:
 path=[];j=solution
 while j>0:
  j,a=parents[j];path.append(a)
 path=path[::-1]
 print('SOLVED','PATH',tuple(path),'LENGTH',len(path),'NODES',len(stlist),'END',stlist[solution],'SECONDS',round(time.time()-tic,2),flush=True)
else:print('SEARCH_LIMIT','NODES',len(stlist),'LEFT',len(queue),'SECONDS',round(time.time()-tic,2),flush=True)
