from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,random,collections,heapq,math
random.seed(48)
root=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
A=(1,2,3,4)
def key(g):
 return (tuple((s.x,s.y,s.rotation,tuple((t.x,t.y,t.rotation) for t in g.mwfajkguqx[s])) for s in g.xpmcmtbcv),tuple((s.x,s.y,int(s.pixels[1,1])) for s in g.vbelzuaian),len(g.ljprkjlji),len(g.pzzwlsmdt),g.lgdrixfno)
def score(g):
 body=g.mwfajkguqx[g.vzvypfsnt]
 upper=g.vjfbwggsd[g.vzvypfsnt]
 colors=[int(t.pixels[1,1]) for t in upper]
 goal=[8,14,9]
 ordered=sum(1 for i,v in enumerate(colors) if i<len(goal) and v==goal[i])
 nearest=sum(min(abs(s.x-t.x)+abs(s.y-t.y) for s in body) for t in g.vbelzuaian[:3])
 moved=sum(abs(t.x-41)+abs(t.y-y) for t,y in zip(g.vbelzuaian[:3],[30,24,18]))
 return (len(upper)*25+ordered*80-nearest/6.0+min(moved/6,20)*0.4,colors,nearest,moved)
seen={key(root._game)}
beam=[((),root)]
best=(-1,None,None)
for dep in range(1,46):
 pool=[];solved=None
 for p,e in beam:
  for z in A:
   q=copy.deepcopy(e);r=q.step(GameAction.from_id(z),data={})
   g=q._game
   if g._current_level_index>0 or r.levels_completed>0 or r.state.name=='WIN':
    solved=(p+(z,),r.levels_completed,g._current_level_index,r.state.name);break
   if r.state.name!='NOT_FINISHED':continue
   k=key(g)
   if k in seen:continue
   seen.add(k)
   v,colors,near,moved=score(g)
   if v>best[0]:best=(v,p+(z,),(colors,near,moved,len(g.mwfajkguqx[g.vzvypfsnt])))
   pool.append((v+random.random()*2,p+(z,),q))
  if solved:break
 if solved:
  print('SOLVED',solved,'SEEN',len(seen),flush=True)
  break
 if not pool:
  print('EXHAUSTED',dep,'SEEN',len(seen),'BEST',best,flush=True);break
 pool.sort(key=lambda x:x[0],reverse=True)
 beam=[(p,e) for v,p,e in pool[:160]]
 if dep%2==0 or dep==1:
  print('DEPTH',dep,'SEEN',len(seen),'POOL',len(pool),'BEAM',len(beam),'BEST',best,'TOP',[(round(v,1),p) for v,p,e in pool[:2]],flush=True)
else:print('LIMIT 45','BEST',best,'SEEN',len(seen),flush=True)
