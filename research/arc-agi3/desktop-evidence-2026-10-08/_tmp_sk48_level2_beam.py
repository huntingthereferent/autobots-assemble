from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,random
random.seed(48)
prefix=(4,4,4,1,1,1,4,3,2,2,4,3,1,4)
root=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
for a in prefix:root.step(GameAction.from_id(a),data={})
assert root._game._current_level_index==1
A=(1,2,3,4)
g=root._game
key_head=list(g.xpmcmtbcv)[0]
target=[int(s.pixels[1,1]) for s in g.vjfbwggsd[g.xpmcmtbcv[key_head]]]
startpads=[(s.x,s.y,int(s.pixels[1,1])) for s in g.vbelzuaian if s.y<53]
print('START LEVEL2 TARGET',target,'PADS',startpads,flush=True)
def key(g):
 return (tuple((s.x,s.y,s.rotation,tuple((t.x,t.y,t.rotation) for t in g.mwfajkguqx[s])) for s in g.xpmcmtbcv),tuple((s.x,s.y,int(s.pixels[1,1])) for s in g.vbelzuaian),len(g.ljprkjlji),len(g.pzzwlsmdt),g.lgdrixfno)
def score(g):
 active=g.vzvypfsnt
 body=g.mwfajkguqx[active]
 upper=g.vjfbwggsd[active]
 colors=[int(t.pixels[1,1]) for t in upper]
 ordered=sum(1 for i,v in enumerate(colors) if i<len(target) and v==target[i])
 prefix=next((i for i,(x,y) in enumerate(zip(colors,target)) if x!=y),min(len(colors),len(target)))
 firstpads=[t for t in g.vbelzuaian if t.y<53]
 if not firstpads:firstpads=g.vbelzuaian[:len(target)]
 nearest=sum(min(abs(s.x-t.x)+abs(s.y-t.y) for s in body) for t in firstpads)
 moved=sum(abs(t.x-x)+abs(t.y-y) for t,(x,y,c) in zip(firstpads,startpads))
 return (len(upper)*22+ordered*95+prefix*28-nearest/6.0+min(moved/6,30)*0.2, colors,nearest,moved)
seen={key(root._game)};beam=[((),root)]
best=(-1e9,None,None)
for dep in range(1,71):
 pool=[];solved=None
 for p,e in beam:
  for z in A:
   q=copy.deepcopy(e);r=q.step(GameAction.from_id(z),data={})
   g=q._game
   if g._current_level_index>1 or r.levels_completed>1 or r.state.name=='WIN':
    solved=(p+(z,),r.levels_completed,g._current_level_index,r.state.name);break
   if r.state.name!='NOT_FINISHED':continue
   k=key(g)
   if k in seen:continue
   seen.add(k)
   v,colors,near,moved=score(g)
   if v>best[0]:best=(v,p+(z,),(colors,near,moved,len(g.mwfajkguqx[g.vzvypfsnt])))
   pool.append((v+random.random()*3,p+(z,),q))
  if solved:break
 if solved:
  print('SOLVED_LEVEL2',solved,'SEEN',len(seen),'FULL_PATH',prefix+solved[0],flush=True);break
 if not pool:
  print('EXHAUSTED',dep,'SEEN',len(seen),'BEST',best,flush=True);break
 pool.sort(key=lambda x:x[0],reverse=True)
 beam=[(p,e) for v,p,e in pool[:230]]
 if dep%3==0 or dep==1:
  print('DEPTH',dep,'SEEN',len(seen),'POOL',len(pool),'BEST',best,'TOP',[(round(v,1),p) for v,p,e in pool[:2]],flush=True)
else:print('LIMIT70','BEST',best,'SEEN',len(seen),flush=True)
