from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from collections import deque
import copy,time
start=Arcade(operation_mode=OperationMode.NORMAL).make('ls20')
P1=(3,3,3,1,1,1,1,4,4,4,1,1,1)
for z in P1:start.step(GameAction.from_id(z),data={})
def key(e):
 g=e._game
 return (g.gudziatsk.x,g.gudziatsk.y,g.cklxociuu,g.hiaauhahz,g.fwckfzsyc,tuple(g.lvrnuajbl),g.akoadfsur,g.ebfuxzbvn,len(g.euemavvxz))
seen={key(start)};q=deque([((),start)]);begin=time.time();best=(999,None,None);rotations=set()
while q and len(seen)<7000:
 p,e=q.popleft()
 g=e._game;rotations.add(g.cklxociuu)
 dist=abs(g.gudziatsk.x-14)+abs(g.gudziatsk.y-40)
 if dist<best[0]:best=(dist,p,(g.gudziatsk.x,g.gudziatsk.y,g.cklxociuu))
 for z in (1,2,3,4):
  nxt=copy.deepcopy(e);r=nxt.step(GameAction.from_id(z),data={})
  path=p+(z,)
  if r.levels_completed>=2:
   print('SOLVED_LEVEL2','ACTIONS',len(path),'PATH',path,'STATE',r.state.name,'STATES',len(seen),'SEC',round(time.time()-begin,2),flush=True);quit()
  if r.state.name!='NOT_FINISHED':continue
  k=key(nxt)
  if k in seen:continue
  seen.add(k)
  q.append((path,nxt))
 if len(seen)%75<4:print('PROGRESS','STATES',len(seen),'QUEUE',len(q),'DEPTH',len(p),'SEC',round(time.time()-begin,2),flush=True)
print('BOUNDARY','STATES',len(seen),'ROTATIONS',rotations,'NEAREST',best,'QUEUE',len(q),'SEC',round(time.time()-begin,2),flush=True)
