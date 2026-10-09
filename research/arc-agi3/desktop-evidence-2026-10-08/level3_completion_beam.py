from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
from collections import defaultdict
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
MEET=(5,5,4,5,7,2,5)
ACTS=[1,2,3,4,5,7]
root=a.make('ar25'); rr=None
for z in SOL+list(MEET): rr=root.step(GameAction.from_id(z),data={})
def key(e,r):
 g=e._game
 sel=-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu)
 stack=tuple((tuple(s["ouurgkpbbjj"]),tuple(s["jtkyjqznbnp"])) for s in g.flqblmrxsla[-8:])
 objs=tuple((s.x,s.y,s.pixels.shape,s.pixels.tobytes()) for s in g.ayyvxqrhnzw)
 return (r.frame[0].tobytes(),sel,len(g.flqblmrxsla),stack,objs,g.xukxeewuexo,g.qehjebksqcm,g.hujpxmlafgh,g.hsiusrsrdkswnt,g.lelsvjlwneo.current_steps)
def score(e):
 g=e._game;b=g.naxbskjmlg()
 return sum(1 for t in g.fswikrcrdmx if int(b[t.y,t.x])>=0)
beam=[((),copy.deepcopy(root),rr)]
seen={key(root,rr)}
best=-1
WIDTH=500
for depth in range(1,31):
 cand=[]
 for h,e0,r0 in beam:
  for z in ACTS:
   e=copy.deepcopy(e0);r=e.step(GameAction.from_id(z),data={});nh=h+(z,)
   if r.levels_completed>2:
    print("SOLVED",nh,"FULL",SOL+list(MEET)+list(nh),"DEPTH",depth);raise SystemExit
   if r.state.name!='NOT_FINISHED' or r.levels_completed!=2:continue
   k=key(e,r)
   if k in seen:continue
   seen.add(k);s=score(e)
   if s>best:
    best=s;print("BEST",best,"DEPTH",depth,"H",nh)
   g=e._game
   sel=-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu)
   cand.append((s,-len(g.flqblmrxsla),-sel,nh,e,r))
 cand.sort(key=lambda x:(x[0],x[1],x[2]),reverse=True)
 beam=[(x[3],x[4],x[5]) for x in cand[:WIDTH]]
 print("DEPTH_DONE",depth,"CAND",len(cand),"BEAM",len(beam),"BEST",best)
 if not beam:break
print("NO_SOLVE","BEST",best,"SEEN",len(seen))
