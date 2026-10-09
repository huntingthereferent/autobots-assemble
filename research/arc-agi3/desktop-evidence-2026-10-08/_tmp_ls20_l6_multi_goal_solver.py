from arc_agi import Arcade,OperationMode
from arcengine import GameAction
p1=(3,3,3,1,1,1,1,4,4,4,1,1,1)
p2=(1,4,1,1,1,1,1,4,4,2,4,2,2,2,2,2,2,1,2,2,3,3,4,1,4,1,1,1,1,1,1,1,3,3,3,3,3,3,2,3,2,2,2,2,2)
p3=(1,1,1,1,1,1,1,1,3,2,2,2,2,2,2,2,2,1,1,1,3,3,1,4,4,4,4,4,4,4,1,1,1,3,1,2,1,4,2)
p4=(3,3,3,2,2,2,3,2,2,3,3,1,2,1,2,1,2,1,1,3,3,1,2,3,3,1,1,1,2,2,4,1,1,1,1,4,1,4,1,1,3,3,3)
p5=(1,3,1,1,3,3,3,4,3,4,3,4,1,1,3,3,3,3,1,3,3,3,4,4,2,2,2,2,2,4,4,3,2,2,4,2,4,4,4,4,4,4,4,1)
from collections import deque
import time
e=Arcade(operation_mode=OperationMode.NORMAL).make('ls20')
for a in p1+p2+p3+p4+p5:e.step(GameAction.from_id(a),data={})
g=e._game
wall={(s.x,s.y) for s in g.current_level.get_sprites_by_tag('ihdgageizm')}
refills=[(s.x-1,s.y-1) for s in g.current_level.get_sprites_by_tag('npxgalaybz')]
targets=[(s.x,s.y,g.ehwheiwsk[i],g.yjdexjsoa[i],g.ldxlnycps[i]) for i,s in enumerate(g.plrpelhym)]
launcher={}
for p in g.hasivfwip:
 n=p.ullzqnksoj(g.gudziatsk)
 orig=(p.sprite.x+p.dx,p.sprite.y+p.dy)
 launcher[orig]=(orig[0]+5*p.dx*n,orig[1]+5*p.dy*n)
phases=[]
for phase in range(8):
 for m in g.wsoslqeku:
  pass
 phases.append(tuple((o._sprite.x,o._sprite.y) for o in g.wsoslqeku))
 for m in g.wsoslqeku:m.step()
print('TARGETS',targets,'START',(g.gudziatsk.x,g.gudziatsk.y,g.cklxociuu,g.hiaauhahz,g.fwckfzsyc,g._step_counter_ui.current_steps),'REFILL',refills,'LAUNCHERS',launcher,'PHASES',phases,flush=True)
# move with four actions, each consumes one budget unit except collecting refills
D=((1,0,-5),(2,0,5),(3,-5,0),(4,5,0))
start=(g.gudziatsk.x,g.gudziatsk.y,g.cklxociuu,g.hiaauhahz,g.fwckfzsyc,g._step_counter_ui.current_steps,0,0,0)
def signature(st):
 x,y,r,c,sh,rem,ref,goals,phase=st
 return (x,y,r,c,sh,ref,goals,phase)
visited={signature(start):start[5]};states=[start];parents=[(-1,0)];queue=deque([0]);starttime=time.time();solved=-1;best=(0,None)
while queue and len(states)<950000:
 idx=queue.popleft();st=states[idx];x,y,r,c,sh,rem,ref,goals,phase=st
 if visited.get(signature(st),-1)>rem:continue
 if goals.bit_count()>best[0]:best=(goals.bit_count(),idx);print('GOAL_PROGRESS',best[0],'DEPTH',None,'STATES',len(states),'SEC',round(time.time()-starttime,1),flush=True)
 for a,dx,dy in D:
  nx,ny=x+dx,y+dy
  if not (9<=nx<=54 and 5<=ny<=50) or (nx,ny) in wall:continue
  nx,ny=launcher.get((nx,ny),(nx,ny))
  newphase=(phase+1)%8
  rotpos,shpos,colpos=phases[newphase]
  nr=(r+1)%4 if (nx,ny)==rotpos else r
  nc=(c+1)%4 if (nx,ny)==colpos else c
  nsh=(sh+1)%6 if (nx,ny)==shpos else sh
  newgoals=goals
  blocked=False
  for k,(gx,gy,gr,gc,gs) in enumerate(targets):
   if (nx,ny)==(gx,gy) and not (goals&(1<<k)):
    if (nr,nc,nsh)==(gr,gc,gs):newgoals|=1<<k
    else:blocked=True
  if blocked:continue
  nrem=rem-1;nref=ref
  for k,pos in enumerate(refills):
   if (nx,ny)==pos and not (ref&(1<<k)):
    nref|=1<<k;nrem=42
  if nrem<0:continue
  nxt=(nx,ny,nr,nc,nsh,nrem,nref,newgoals,newphase)
  key=signature(nxt)
  if visited.get(key,-1)>=nrem:continue
  visited[key]=nrem
  j=len(states);states.append(nxt);parents.append((idx,a));queue.append(j)
  if newgoals==(1<<len(targets))-1:
   solved=j;break
 if solved>=0:break
 if len(states)%100000<3:print('PROGRESS',len(states),'QUEUE',len(queue),'SEC',round(time.time()-starttime,1),'GOALS',best[0],flush=True)
 if time.time()-starttime>100:print('TIME_BOUND',flush=True);break
if solved>=0:
 path=[];j=solved
 while j>0:
  j,a=parents[j];path.append(a)
 path=path[::-1]
 print('SOLUTION',tuple(path),'COUNT',len(path),'NODES',len(states),'FINAL',states[solved],'SEC',round(time.time()-starttime,2),flush=True)
else:
 print('SEARCH_BOUNDARY','NODES',len(states),'QUEUE',len(queue),'GOALS_FOUND',best[0],'TIME',round(time.time()-starttime,2),flush=True)
