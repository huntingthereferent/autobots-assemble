from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
from collections import deque
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
H1=(2,2,2,1,1); H2=(5,5,4,5,7,2); ACTS=[1,2,3,4,5,7]
base=a.make('ar25');r0=None
for z in SOL:r0=base.step(GameAction.from_id(z),data={})
def after(h):
 e=copy.deepcopy(base);r=r0
 for z in h:r=e.step(GameAction.from_id(z),data={})
 return e,r
def key(e,r):
 g=e._game
 sel=-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu)
 stack=tuple((tuple(s["ouurgkpbbjj"]),tuple(s["jtkyjqznbnp"])) for s in g.flqblmrxsla)
 objs=tuple((s.x,s.y,s.pixels.shape,s.pixels.tobytes()) for s in g.ayyvxqrhnzw)
 ovo=tuple(sorted((g.ayyvxqrhnzw.index(s) if s in g.ayyvxqrhnzw else -1,v) for s,v in g.ovoizfolxfq.items()))
 return (r.frame[0].tobytes(),g.level_index,sel,stack,objs,ovo,g.xukxeewuexo,g.xjwpeqpcxav,g.qehjebksqcm,g.hujpxmlafgh,g.hsiusrsrdkswnt,g.lelsvjlwneo.current_steps)
def bfs(seed,depth):
 e,r=after(seed);k=key(e,r);seen={k:()};envs={k:(e,r)};q=deque([((),e,r)])
 while q:
  h,e0,r0=q.popleft()
  if len(h)>=depth:continue
  for z in ACTS:
   ee=copy.deepcopy(e0);rr=ee.step(GameAction.from_id(z),data={})
   nh=h+(z,)
   if rr.levels_completed>2:
    print("CLOSE",seed,nh,rr.levels_completed);continue
   if rr.state.name!='NOT_FINISHED' or rr.levels_completed!=2:continue
   kk=key(ee,rr)
   if kk not in seen:
    seen[kk]=nh;envs[kk]=(ee,rr);q.append((nh,ee,rr))
 return seen
S1=bfs(H1,5);S2=bfs(H2,5)
meet=set(S1)&set(S2)
print("S1",len(S1),"S2",len(S2),"MEET",len(meet))
for k in sorted(meet,key=lambda k:(len(S1[k])+len(S2[k]),S1[k],S2[k]))[:30]:
 print("MEET",S1[k],S2[k])
