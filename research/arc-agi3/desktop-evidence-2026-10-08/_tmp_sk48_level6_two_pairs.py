from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,random,gc,time
random.seed(4804)
p1=(4,4,4,1,1,1,4,3,2,2,4,3,1,4)
p2=(4,4,4,1,1,4,4,1,4,3,3,1,4,4,3,3,3,3,1,4,4,1,4,2,4,3,3,2,4,4)
p3=(1,1,4,1,4,1,4,2,2,3,2,4,4,4,4,1,3,3,3,3,1,1,1,4,2,2,2,3,1,1,1,1,4)
p4=(1,1,3,4,1,4,1,1,3,2,3,3,2,2,2,4,4,4,1,1,3,3,1,4,2,3,1)
p5=(3,1,3,3,4,4,4,2,1,4,4,1,4,2,3,3,3,2,2,3,2,4,4,4,4,3,1,4,4,3,2,4,1,3,3,3,3,1,3,3,3,4,1,4,4,4,4,4,1,4,2,3,3,3,3,3,3,2,4,4,2,4,4,4,4)
prefix=p1+p2+p3+p4+p5
root=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
for a in prefix:root.step(GameAction.from_id(a),data={})
g=root._game
pairs=list(g.xpmcmtbcv.items())
targets={k.name:[int(s.pixels[1,1]) for s in g.vjfbwggsd[m]] for k,m in pairs}
print('TARGETS',targets,flush=True)
def key(g):
 return (tuple((s.name,s.x,s.y,s.rotation,tuple((t.x,t.y,t.rotation) for t in b)) for s,b in g.mwfajkguqx.items()),tuple((s.x,s.y,int(s.pixels[1,1])) for s in g.vbelzuaian),len(g.ljprkjlji),len(g.pzzwlsmdt),g.lgdrixfno)
def score(g):
 ordered=0;coverage=0;prefix=0
 for k,m in g.xpmcmtbcv.items():
  tgt=[int(s.pixels[1,1]) for s in g.vjfbwggsd[m]]
  cc=[int(s.pixels[1,1]) for s in g.vjfbwggsd[k]]
  ordered+=sum(i<len(tgt) and c==tgt[i] for i,c in enumerate(cc))
  coverage+=len(cc)
  for x,y in zip(cc,tgt):
   if x!=y:break
   prefix+=1
 correct_dist=0
 for tile in g.vbelzuaian:
  if tile.y>=53:continue
  c=int(tile.pixels[1,1])
  heads=[k for k,m in g.xpmcmtbcv.items() if c in [int(s.pixels[1,1]) for s in g.vjfbwggsd[m]]]
  if heads:correct_dist+=min(abs(tile.x-s.x)+abs(tile.y-s.y) for k in heads for s in g.mwfajkguqx[k])
 return (coverage*23+ordered*100+prefix*29-correct_dist/6.0,[(k.name,[int(s.pixels[1,1]) for s in g.vjfbwggsd[k]]) for k in g.xpmcmtbcv])
seen={key(root._game)};beam=[((),root)];best=(-1e10,None,None);start=time.time()
gc.disable()
for dep in range(1,66):
 pool=[];solved=None
 for p,e in beam:
  for a in (1,2,3,4):
   q=copy.deepcopy(e);r=q.step(GameAction.from_id(a),data={})
   if q._game._current_level_index>5 or r.levels_completed>5:
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
  print('SOLVED_LEVEL6',solved,'TOTAL',prefix+solved[0],'STATES',len(seen),flush=True);break
 if not pool:print('EXHAUSTED',dep,len(seen),best,flush=True);break
 pool.sort(key=lambda x:x[0],reverse=True)
 beam=[(p,e) for v,p,e in pool[:100]]
 pool=[];gc.collect()
 print('D',dep,'ELAPSED',round(time.time()-start,1),'STATES',len(seen),'BEST',(round(best[0],1),best[1],best[2]),flush=True)
 if time.time()-start>125:
  print('TIME_BOUND_STOP',dep,flush=True);break
else:print('DEPTH_LIMIT',best,flush=True)
gc.enable()
