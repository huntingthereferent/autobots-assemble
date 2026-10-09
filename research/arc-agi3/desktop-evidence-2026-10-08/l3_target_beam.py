from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
P=[5,5,4,5,7,2,5,2,2,2,2,3,5]
ACTS=[1,2,3,4,5,7]
root=a.make('ar25');rr=None
for z in SOL+P:rr=root.step(GameAction.from_id(z),data={})
def sc(e):
 g=e._game;b=g.naxbskjmlg()
 return sum(1 for t in g.fswikrcrdmx if int(b[t.y,t.x])>=0)
def key(e,r):
 g=e._game
 sel=-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu)
 stack=tuple((tuple(s["ouurgkpbbjj"]),tuple(s["jtkyjqznbnp"])) for s in g.flqblmrxsla[-6:])
 objs=tuple((s.x,s.y,s.pixels.shape,s.pixels.tobytes()) for s in g.ayyvxqrhnzw)
 return (r.frame[0].tobytes(),sel,len(g.flqblmrxsla),stack,objs,g.xukxeewuexo,g.qehjebksqcm,g.hujpxmlafgh,g.hsiusrsrdkswnt,g.lelsvjlwneo.current_steps)
beam=[((),copy.deepcopy(root),rr)]
seen={key(root,rr)}
best=sc(root);print("START",best)
for depth in range(1,16):
 cand=[]
 for h,e0,r0 in beam:
  for z in ACTS:
   e=copy.deepcopy(e0);r=e.step(GameAction.from_id(z),data={});nh=h+(z,)
   if r.levels_completed>2:
    print("SOLVED",nh,"FULL",SOL+P+list(nh));raise SystemExit
   if r.state.name!='NOT_FINISHED' or r.levels_completed!=2:continue
   s=sc(e)
   if s<4:continue
   k=key(e,r)
   if k in seen:continue
   seen.add(k)
   if s>best:best=s;print("BEST",best,"D",depth,"H",nh,"OBJ",[(o.x,o.y) for o in e._game.ayyvxqrhnzw])
   cand.append((s,nh,e,r))
 cand.sort(key=lambda x:x[0],reverse=True)
 beam=[(x[1],x[2],x[3]) for x in cand[:120]]
 print("DONE",depth,"N",len(cand),"B",len(beam),"BEST",best)
 if not beam:break
print("NO_SOLVE",best,len(seen))
