from arc_agi import Arcade,OperationMode
from arcengine import GameAction
p1=(3,3,3,1,1,1,1,4,4,4,1,1,1)
p2=(1,4,1,1,1,1,1,4,4,2,4,2,2,2,2,2,2,1,2,2,3,3,4,1,4,1,1,1,1,1,1,1,3,3,3,3,3,3,2,3,2,2,2,2,2)
p3=(1,1,1,1,1,1,1,1,3,2,2,2,2,2,2,2,2,1,1,1,3,3,1,4,4,4,4,4,4,4,1,1,1,3,1,2,1,4,2)
p4=(3,3,3,2,2,2,3,2,2,3,3,1,2,1,2,1,2,1,1,3,3,1,2,3,3,1,1,1,2,2,4,1,1,1,1,4,1,4,1,1,3,3,3)
e=Arcade(operation_mode=OperationMode.NORMAL).make('ls20')
for z in p1+p2+p3+p4:e.step(GameAction.from_id(z),data={})
from collections import deque
g=e._game
wall={(s.x,s.y) for s in g.current_level.get_sprites_by_tag('ihdgageizm')}
pickups=[(s.x-1,s.y-1) for s in g.current_level.get_sprites_by_tag('npxgalaybz')]
color={(s.x,s.y) for s in g.current_level.get_sprites_by_tag('soyhouuebz')}
shape={(s.x,s.y) for s in g.current_level.get_sprites_by_tag('ttfwljgohq')}
rot={(s.x,s.y) for s in g.current_level.get_sprites_by_tag('rhsxkxzdjz')}
launchers={}
for p in g.hasivfwip:
 n=p.ullzqnksoj(g.gudziatsk)
 origin=(p.sprite.x+p.dx,p.sprite.y+p.dy)
 target=(origin[0]+5*p.dx*n,origin[1]+5*p.dy*n)
 launchers[origin]=target
goal=(g.plrpelhym[0].x,g.plrpelhym[0].y,g.ehwheiwsk[0],g.yjdexjsoa[0],g.ldxlnycps[0])
start=(g.gudziatsk.x,g.gudziatsk.y,g.cklxociuu,g.hiaauhahz,g.fwckfzsyc,g._step_counter_ui.current_steps,0)
print('START',start,'GOAL',goal,'REFILLS',pickups,'LAUNCHERS',launchers,'SWITCHES',(shape,color,rot),'STEP',g._step_counter_ui.efipnixsvl,flush=True)
delta={1:(0,-5),2:(0,5),3:(-5,0),4:(5,0)}
q=deque([(start,())]);seen={start};found=None
while q and len(seen)<1000000:
 st,p=q.popleft();x,y,r,c,sh,rem,mask=st
 if (x,y,r,c,sh)==goal:
  found=(p,st);break
 for a,(dx,dy) in delta.items():
  nx,ny=x+dx,y+dy
  if not (9<=nx<=54 and 5<=ny<=50) or (nx,ny) in wall:continue
  nx,ny=launchers.get((nx,ny),(nx,ny))
  nr=(r+1)%4 if (nx,ny) in rot else r
  nc=(c+1)%len(g.tnkekoeuk) if (nx,ny) in color else c
  ns=(sh+1)%len(g.ijessuuig) if (nx,ny) in shape else sh
  if (nx,ny)==goal[:2] and (nr,nc,ns)!=goal[2:]:continue
  rr=rem-g._step_counter_ui.efipnixsvl;mm=mask
  for i,refill in enumerate(pickups):
   if (nx,ny)==refill and not (mask>>i&1):mm|=1<<i;rr=g._step_counter_ui.osgviligwp
  if rr<0:continue
  nexts=(nx,ny,nr,nc,ns,rr,mm)
  if nexts in seen:continue
  seen.add(nexts);q.append((nexts,p+(a,)))
print('SEARCH_STATES',len(seen),'FOUND',found,'DEPTH',len(found[0]) if found else None,flush=True)
