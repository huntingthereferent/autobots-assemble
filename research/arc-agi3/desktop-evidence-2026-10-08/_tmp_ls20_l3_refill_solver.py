from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from collections import deque
p1=(3,3,3,1,1,1,1,4,4,4,1,1,1)
p2=(1,4,1,1,1,1,1,4,4,2,4,2,2,2,2,2,2,1,2,2,3,3,4,1,4,1,1,1,1,1,1,1,3,3,3,3,3,3,2,3,2,2,2,2,2)
e=Arcade(operation_mode=OperationMode.NORMAL).make('ls20')
for z in p1+p2:e.step(GameAction.from_id(z),data={})
g=e._game
walls={(s.x,s.y) for s in g.current_level.get_sprites_by_tag('ihdgageizm')}
pickups=[(s.x-1,s.y-1) for s in g.current_level.get_sprites_by_tag('npxgalaybz')]
rot={(s.x,s.y) for s in g.current_level.get_sprites_by_tag('rhsxkxzdjz')}
color={(s.x,s.y) for s in g.current_level.get_sprites_by_tag('soyhouuebz')}
shape={(s.x,s.y) for s in g.current_level.get_sprites_by_tag('ttfwljgohq')}
goal=(g.plrpelhym[0].x,g.plrpelhym[0].y,g.ehwheiwsk[0],g.yjdexjsoa[0],g.ldxlnycps[0])
init=(g.gudziatsk.x,g.gudziatsk.y,g.cklxociuu,g.hiaauhahz,g.fwckfzsyc,g._step_counter_ui.current_steps,0)
print('START',init,'GOAL',goal,'PICKUPS',pickups,'ROTS',rot,'COLORS',color,'SHAPE',shape,'WALLS',len(walls),flush=True)
D={1:(0,-5),2:(0,5),3:(-5,0),4:(5,0)}
q=deque([(init,())]);seen={init};answer=None
while q and len(seen)<500000:
 state,p=q.popleft();x,y,r,c,sh,rem,mask=state
 if (x,y,r,c,sh)==goal:
  answer=(p,state);break
 for a,(dx,dy) in D.items():
  nx,ny=x+dx,y+dy
  if not (9<=nx<=54 and 5<=ny<=50) or (nx,ny) in walls:continue
  nrot=(r+1)%4 if (nx,ny) in rot else r
  ncol=(c+1)%4 if (nx,ny) in color else c
  nsh=(sh+1)%6 if (nx,ny) in shape else sh
  if (nx,ny)==goal[:2] and (nrot,ncol,nsh)!=goal[2:]:continue
  m=mask;rem2=rem-2
  for i,pt in enumerate(pickups):
   if (nx,ny)==pt and not mask>>i&1:
    m|=1<<i;rem2=42
  if rem2<0:continue
  ns=(nx,ny,nrot,ncol,nsh,rem2,m)
  if ns in seen:continue
  seen.add(ns);q.append((ns,p+(a,)))
print('END','STATES',len(seen),'QUEUE',len(q),'FOUND',answer,'DEPTH',len(answer[0]) if answer else None,flush=True)
