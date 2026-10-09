from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
from collections import deque
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
MEET=(5,5,4,5,7,2,5)
ACTS=[1,2,3,4,5,7]
e=a.make('ar25');r=None
for z in SOL+list(MEET):r=e.step(GameAction.from_id(z),data={})
def key(e,r):
 g=e._game
 sel=-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu)
 stack=tuple((tuple(s["ouurgkpbbjj"]),tuple(s["jtkyjqznbnp"])) for s in g.flqblmrxsla)
 objs=tuple((s.x,s.y,s.pixels.shape,s.pixels.tobytes()) for s in g.ayyvxqrhnzw)
 ovo=tuple(sorted((g.ayyvxqrhnzw.index(s) if s in g.ayyvxqrhnzw else -1,v) for s,v in g.ovoizfolxfq.items()))
 return (r.frame[0].tobytes(),g.level_index,sel,stack,objs,ovo,g.xukxeewuexo,g.xjwpeqpcxav,g.qehjebksqcm,g.hujpxmlafgh,g.hsiusrsrdkswnt,g.lelsvjlwneo.current_steps)
root=copy.deepcopy(e);rootr=r;rootk=key(root,rootr)
seen={rootk:()};q=deque([((),root,rootr)]);walls=0;returns=[]
while q:
 h,e0,r0=q.popleft()
 if len(h)>=5:continue
 for z in ACTS:
  ee=copy.deepcopy(e0);rr=ee.step(GameAction.from_id(z),data={});walls+=1
  nh=h+(z,)
  if rr.levels_completed>2:
   print("SOLVED_L3","SUFFIX",nh,"FULL",SOL+list(MEET)+list(nh),"WALL",walls)
   raise SystemExit
  if rr.state.name!='NOT_FINISHED' or rr.levels_completed!=2:continue
  k=key(ee,rr)
  if k==rootk:returns.append(nh)
  if k not in seen:
   seen[k]=nh;q.append((nh,ee,rr))
print("NO_CLOSE","WALLS",walls,"STATES",len(seen),"RETURNS",len(returns))
for h in sorted(returns,key=lambda x:(len(x),x))[:40]:print("RETURN",h)
