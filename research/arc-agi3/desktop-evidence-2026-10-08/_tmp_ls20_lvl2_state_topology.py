from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from collections import deque,defaultdict
import copy
e=Arcade(operation_mode=OperationMode.NORMAL).make('ls20')
p1=(3,3,3,1,1,1,1,4,4,4,1,1,1)
for z in p1:e.step(GameAction.from_id(z),data={})
def key(g):
 return (g.gudziatsk.x,g.gudziatsk.y,g.cklxociuu,g.hiaauhahz,g.fwckfzsyc)
q=deque([((),e)]);seen={key(e._game)};at=defaultdict(list);rot=defaultdict(set);blocked=defaultdict(set)
while q:
 p,now=q.popleft();g=now._game;k=key(g);x,y,o,*_=k
 at[(x,y)].append((o,p))
 rot[(x,y)].add(o)
 for a in (1,2,3,4):
  nn=copy.deepcopy(now);r=nn.step(GameAction.from_id(a),data={});gg=nn._game;kk=key(gg)
  if r.levels_completed>1: print('SOLVED',p+(a,),flush=True);quit()
  if r.state.name!='NOT_FINISHED':continue
  if (x,y)==(14,35): blocked[o].add((a,gg.gudziatsk.x,gg.gudziatsk.y,gg.akoadfsur))
  if kk in seen:continue
  seen.add(kk);q.append((p+(a,),nn))
print('COUNT',len(seen),'UNIQUE_SPATIAL',len(rot),flush=True)
for pt in [(14,35),(14,40),(19,40),(19,35),(19,30),(49,45),(44,45),(49,40),(34,40),(29,40)]:
 v=at.get(pt,[]);print('POINT',pt,'ROTATIONS',sorted(set(o for o,p in v)),'PATHS',[(o,p) for o,p in v[:5]],flush=True)
print('GOAL_APPROACH_TESTS',dict(blocked),flush=True)
print('ROT3_POINTS',sorted(pt for pt,rr in rot.items() if 3 in rr),flush=True)
