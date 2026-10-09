from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,itertools,collections
root=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
A=(1,2,3,4,7)
def signature(g):
 return (tuple((int(s.x),int(s.y),int(s.rotation),tuple((int(t.x),int(t.y),int(t.rotation)) for t in g.mwfajkguqx[s])) for s in g.xpmcmtbcv),g.qiercdohl)
def hsig(g):
 return tuple(tuple((int(x),int(y),int(n)) for _,x,y,n in frame) for frame in g.seghobzez)
states=[];front=[((),root)]
for depth in range(5):
 nxt=[]
 for p,e in front:
  states.append((p,signature(e._game),hsig(e._game)))
  if depth<4:
   for act in A:
    q=copy.deepcopy(e);r=q.step(GameAction.from_id(act),data={})
    if r.state.name=='NOT_FINISHED':nxt.append((p+(act,),q))
 front=nxt
print('STATES',len(states),flush=True)
groups=collections.defaultdict(list)
for p,s,h in states:
 groups[(s,h[-2:])].append((p,h))
candidates=[]
for key,items in groups.items():
 if len(items)>1:
  for a,b in itertools.combinations(items,2):
   if a[1]!=b[1]:
    candidates.append((a,b))
print('MATCH_TOP2_DIFF_DEEP',len(candidates),flush=True)
for a,b in candidates[:12]:
 print('PAIR',a[0],b[0],'H',len(a[1]),len(b[1]),'Y',tuple(x[1] for x in a[1]),tuple(x[1] for x in b[1]),flush=True)
