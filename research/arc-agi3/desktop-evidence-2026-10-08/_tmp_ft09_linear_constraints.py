from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from collections import Counter,defaultdict
import copy
e=Arcade(operation_mode=OperationMode.NORMAL).make('ft09');g=e._game
print('LEVEL',g.level_index,'LEVELS',len(g._levels),'ALLOWED','ACTION6 only','COLOR_VOCAB',g.gqb,'BUDGET',g.lpw.dzy,flush=True)
def centers(xs):return [(s.name,int(s.x),int(s.y),int(s.pixels[1,1])) for s in xs]
print('Hkx',centers(g.fhc),'NTi',centers(g.mou),'CONSTRAINT_SPRITES',len(g.gig),flush=True)
target=defaultdict(set)
for constraint in g.gig:
 col=int(constraint.pixels[1,1])
 for yi in (-1,0,1):
  for xi in (-1,0,1):
   if (xi,yi)==(0,0):continue
   cell=(constraint.x+4*xi,constraint.y+4*yi)
   candidate=next((obj for obj in g.fhc+g.mou if (obj.x,obj.y)==cell),None)
   if candidate is None:continue
   equal=int(constraint.pixels[yi+1,xi+1])==0
   desired=g.gqb.index(col) ^ (not equal)
   target[cell].add(int(desired))
print('TARGET',sorted((k,list(v)) for k,v in target.items()),'INCONSISTENT',sum(len(v)>1 for v in target.values()),flush=True)
for obj in (g.fhc+g.mou):
 q=copy.deepcopy(e); before={ (x.x,x.y):int(x.pixels[1,1]) for x in q._game.fhc+q._game.mou }
 r=q.step(GameAction.ACTION6,data={'x':obj.x*4,'y':obj.y*4})
 after={ (x.x,x.y):int(x.pixels[1,1]) for x in q._game.fhc+q._game.mou }
 ch=[k for k in before if before[k]!=after[k]]
 print('CLICK',obj.name,obj.x,obj.y,'FLIPS',ch,'LEVEL',r.levels_completed,flush=True)
