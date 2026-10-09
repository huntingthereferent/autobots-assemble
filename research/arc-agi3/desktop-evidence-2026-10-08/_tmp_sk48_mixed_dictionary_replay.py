from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy, collections
root=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
A=(1,2,3,4,7)
def hist(g):
 return [tuple((int(x),int(y),int(n)) for _,x,y,n in frame) for frame in g.seghobzez]
def encode(h):
 unique=[];idx=[]
 for frame in h:
  if frame not in unique:unique.append(frame)
  idx.append(unique.index(frame))
 return unique,idx
front=[((),root)]; patterns={}
for depth in range(5):
 next_front=[]
 for p,e in front:
  h=hist(e._game);d,i=encode(h)
  patterns.setdefault(tuple(i),p)
  if depth<4:
   for a in A:
    q=copy.deepcopy(e);r=q.step(GameAction.from_id(a),data={})
    if r.state.name=='NOT_FINISHED':next_front.append((p+(a,),q))
 front=next_front
print('PATTERNS',len(patterns),flush=True)
passed=0; failed=[]; saved=0; original=0
for pattern,p in sorted(patterns.items(),key=lambda x:(len(x[0]),x[0])):
 e=copy.deepcopy(root)
 for a in p:e.step(GameAction.from_id(a),data={})
 g=e._game; h=hist(g);dictionary,ids=encode(h)
 original+=len(h);saved+=len(dictionary)
 check=[]
 for undo in range(len(h)+2):
  actual=hist(e._game)
  predicted=[dictionary[i] for i in ids[:max(1,len(ids)-undo)]]
  actualpos=[(int(s.x),int(s.y),int(s.rotation)) for s in e._game.mwfajkguqx]
  predpos=[(x,y,int(s.rotation)) for s,x,y,n in e._game.seghobzez[-1] if s in e._game.mwfajkguqx]
  if actual!=predicted:check.append(('history',undo,actual,predicted))
  if actualpos and predpos and actualpos!=predpos:check.append(('pos',undo,actualpos,predpos))
  e.step(GameAction.ACTION7,data={})
 if check:failed.append((p,pattern,check[0]))
 else:passed+=1
 print('CASE',p,'PATTERN',pattern,'DISTINCT',len(dictionary),'UNDO',len(h)+2,'PASS',not bool(check),flush=True)
print('RESULT',passed,'/',len(patterns),'SNAPSHOTS',original,'DICTIONARY_ENTRIES',saved,'FAILURES',failed[:3],flush=True)
