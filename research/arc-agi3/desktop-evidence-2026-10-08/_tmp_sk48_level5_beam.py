from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,random,gc,time
random.seed(4805)
p1=(4,4,4,1,1,1,4,3,2,2,4,3,1,4)
p2=(4,4,4,1,1,4,4,1,4,3,3,1,4,4,3,3,3,3,1,4,4,1,4,2,4,3,3,2,4,4)
p3=(1,1,4,1,4,1,4,2,2,3,2,4,4,4,4,1,3,3,3,3,1,1,1,4,2,2,2,3,1,1,1,1,4)
p4=(1,1,3,4,1,4,1,1,3,2,3,3,2,2,2,4,4,4,1,1,3,3,1,4,2,3,1)
prefix=p1+p2+p3+p4
root=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
for a in prefix:root.step(GameAction.from_id(a),data={})
g=root._game
pair=list(g.xpmcmtbcv.items())[0]; target=[int(s.pixels[1,1]) for s in g.vjfbwggsd[pair[1]]]
print('L5 TARGET',target,'UPPER',[(s.x,s.y,int(s.pixels[1,1])) for s in g.vbelzuaian if s.y<53],flush=True)
def key(g):
 return (tuple((s.name,s.x,s.y,s.rotation,tuple((t.x,t.y,t.rotation) for t in b)) for s,b in g.mwfajkguqx.items()),tuple((s.x,s.y,int(s.pixels[1,1])) for s in g.vbelzuaian),len(g.ljprkjlji),len(g.pzzwlsmdt),g.lgdrixfno)
def score(g):
 body=g.mwfajkguqx[g.vzvypfsnt]
 colors=[int(t.pixels[1,1]) for t in g.vjfbwggsd[g.vzvypfsnt]]
 ordered=sum(i<len(target) and c==target[i] for i,c in enumerate(colors))
 pref=0
 for x,y in zip(colors,target):
  if x!=y:break
  pref+=1
 top=[t for t in g.vbelzuaian if t.y<53]
 if not top:top=g.vbelzuaian[:len(target)]
 dist=sum(min(abs(t.x-s.x)+abs(t.y-s.y) for s in body) for t in top)
 return (len(colors)*22+ordered*95+pref*28-dist/6.0,colors)
seen={key(root._game)};beam=[((),root)];best=(-1e10,None,None);start=time.time()
gc.disable()
for dep in range(1,61):
 pool=[];solved=None
 for p,e in beam:
  for a in (1,2,3,4):
   q=copy.deepcopy(e);r=q.step(GameAction.from_id(a),data={})
   if q._game._current_level_index>4 or r.levels_completed>4:
    solved=(p+(a,),r.levels_completed);break
   if r.state.name!='NOT_FINISHED':continue
   k=key(q._game)
   if k in seen:continue
   seen.add(k)
   s,colors=score(q._game)
   if s>best[0]:best=(s,p+(a,),colors)
   pool.append((s+random.random()*3,p+(a,),q))
  if solved:break
 if solved:
  print('SOLVED_LEVEL5',solved,'TOTAL',prefix+solved[0],'STATES',len(seen),flush=True);break
 if not pool:print('EXHAUSTED',dep,len(seen),best,flush=True);break
 pool.sort(key=lambda x:x[0],reverse=True)
 beam=[(p,e) for v,p,e in pool[:70]]
 pool=[];gc.collect()
 print('D',dep,'ELAPSED',round(time.time()-start,1),'STATES',len(seen),'BEST',(round(best[0],1),best[1],best[2]),flush=True)
 if time.time()-start>95:
  print('TIME_BOUND_STOP',dep,flush=True);break
else:print('DEPTH_LIMIT',best,flush=True)
gc.enable()
