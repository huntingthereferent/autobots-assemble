from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,random,gc,time
random.seed(4806)
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
 return (g.vzvypfsnt.name,tuple((s.name,s.x,s.y,s.rotation,len(body)) for s,body in g.mwfajkguqx.items()),tuple((s.x,s.y,int(s.pixels[1,1])) for s in g.vbelzuaian),len(g.ljprkjlji),len(g.pzzwlsmdt),g.lgdrixfno)
def score(g):
 good=0;bad=0;dist=0;contacts=[]
 for head,mate in g.xpmcmtbcv.items():
  target=[int(t.pixels[1,1]) for t in g.vjfbwggsd[mate]]
  got=[int(t.pixels[1,1]) for t in g.vjfbwggsd[head]]
  contacts.append((head.name,got))
  for i,t in enumerate(got[:len(target)]):
   if t==target[i]:good+=1
   else:bad+=1
  color=target[0]
  pads=[t for t in g.vbelzuaian if int(t.pixels[1,1])==color and t.y<53]
  axis=(6,0) if head.rotation in (0,180) else (0,6)
  future=[(head.x+axis[0]*j,head.y+axis[1]*j) for j in range(len(target)+1)]
  dist+=sum(min((abs(t.x-x)+abs(t.y-y)) for t in pads) for x,y in future[1:])
 return good*180-bad*105-dist*1.3,contacts
seen={key(root._game)};beam=[((),root)];best=(-1e10,None,None);start=time.time();gc.disable()
for dep in range(1,85):
 pool=[];solved=None
 for p,e in beam:
  for a in (1,2,3,4,6):
   q=copy.deepcopy(e)
   if a==6:
    other=next((k for k in q._game.xpmcmtbcv if k!=q._game.vzvypfsnt),None)
    if other is None:continue
    r=q.step(GameAction.ACTION6,data={'x':int(other.x+2),'y':int(other.y+2)})
    if q._game.vzvypfsnt is not other:continue
   else:r=q.step(GameAction.from_id(a),data={})
   if q._game._current_level_index>5 or r.levels_completed>5:
    solved=(p+(a,),r.levels_completed);break
   if r.state.name!='NOT_FINISHED':continue
   k=key(q._game)
   if k in seen:continue
   seen.add(k);v,colors=score(q._game)
   if v>best[0]:best=(v,p+(a,),colors)
   pool.append((v+random.random()*5,p+(a,),q))
  if solved:break
 if solved:
  print('SOLVED_LEVEL6',solved,'STATES',len(seen),'PREFIX_LEN',len(prefix),'TOTAL_PATH',p+(a,),flush=True);break
 if not pool:print('EXHAUSTED',dep,len(seen),best,flush=True);break
 pool.sort(key=lambda x:x[0],reverse=True)
 beam=[(p,e) for v,p,e in pool[:75]];pool=[];gc.collect()
 if dep%3==0 or dep<=5:print('DEPTH',dep,'SEC',round(time.time()-start,1),'SEEN',len(seen),'BEST',best,flush=True)
 if time.time()-start>118:print('TIME_BOUND',dep,'BEST',best,flush=True);break
gc.enable()
