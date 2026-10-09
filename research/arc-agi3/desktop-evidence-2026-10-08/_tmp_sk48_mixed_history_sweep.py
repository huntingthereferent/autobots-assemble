from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,collections
root=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
A=(1,2,3,4,7)
def hist(e):
 return [tuple((int(x),int(y),int(n)) for _,x,y,n in frame) for frame in e._game.seghobzez]
def encode(h):
 ids=[];unique=[]
 for s in h:
  if s not in unique:unique.append(s)
  ids.append(unique.index(s))
 return ids,unique
stats=collections.Counter(); patterns={}; cases=[]
front=[((),root)]
for d in range(5):
 nxt=[]
 for p,e in front:
  h=hist(e); ids,unique=encode(h)
  periodic=all(ids[i]==ids[i%2] for i in range(len(ids)))
  stats[(d,periodic,len(unique))]+=1
  if not periodic and len(cases)<20:
   cases.append((p,ids,len(h),e._game.qiercdohl))
  patterns.setdefault(tuple(ids),p)
  if d<4:
   for a in A:
    q=copy.deepcopy(e); r=q.step(GameAction.from_id(a),data={})
    if r.state.name=='NOT_FINISHED':nxt.append((p+(a,),q))
 front=nxt
print('COUNT',sum(stats.values()),flush=True)
print('BY_DEPTH',sorted(stats.items()),flush=True)
print('NONPERIODIC_EXAMPLES',cases,flush=True)
print('UNIQUE_SYMBOL_PATTERNS',len(patterns),flush=True)
for k,p in sorted(patterns.items(),key=lambda x:(len(x[0]),x[0]))[:28]:
 print('PATTERN',k,'PATH',p,flush=True)
