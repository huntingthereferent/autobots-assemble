from arc_agi import Arcade,OperationMode
from collections import deque,defaultdict
from arcengine import GameAction
e=Arcade(operation_mode=OperationMode.NORMAL).make('ls20')
p1=(3,3,3,1,1,1,1,4,4,4,1,1,1)
for z in p1:e.step(GameAction.from_id(z),data={})
g=e._game
W={(s.x,s.y) for s in g.current_level.get_sprites_by_tag('ihdgageizm')}
C=[(s.x-1,s.y-1) for s in g.current_level.get_sprites_by_tag('npxgalaybz')]
print('WALLS',len(W),'PICKUPS',C,'SWITCH',(49,45),'GOAL',(14,40),'START',(g.gudziatsk.x,g.gudziatsk.y,g.cklxociuu,g._step_counter_ui.current_steps),flush=True)
start=(g.gudziatsk.x,g.gudziatsk.y,g.cklxociuu,g._step_counter_ui.current_steps,0)
delta={1:(0,-5),2:(0,5),3:(-5,0),4:(5,0)}
q=deque([(start,())]);visited={start};best=defaultdict(lambda:(-100,None));out=None
while q:
 st,path=q.popleft();x,y,rot,remaining,mask=st
 if (x,y,rot)==(14,40,3):
  out=(path,st);break
 for action,(dx,dy) in delta.items():
  nx,ny=x+dx,y+dy
  if not (9<=nx<=54 and 5<=ny<=50):continue
  if (nx-0,ny) in W:continue
  if (nx,ny)==(14,40) and rot!=3:continue
  re=remaining-2
  # collectible recharges on the same movement
  nmask=mask
  for i,p in enumerate(C):
   if (nx,ny)==p and not (mask>>i&1):
    nmask|=1<<i;re=42
  if re<0:continue
  nro=(rot+1)%4 if (nx,ny)==(49,45) else rot
  ns=(nx,ny,nro,re,nmask)
  if ns in visited:continue
  visited.add(ns);q.append((ns,path+(action,)))
print('SEARCH',len(visited),'RESULT',out,'MAX_DEPTH',max(0,len(out[0]) if out else 0),flush=True)
for k in sorted(C):print('PICKUP_REACHED',k,sum(1 for st in visited if (st[0],st[1])==k),flush=True)
