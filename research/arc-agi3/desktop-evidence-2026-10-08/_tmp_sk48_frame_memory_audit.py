from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from collections import defaultdict,Counter
import ast,hashlib,numpy as np,pathlib
path=pathlib.Path(r'C:\Users\teepa\arc3\AB_ARC_EVIDENCE\_tmp_sk48_complete_replay.py')
tree=ast.parse(path.read_text(encoding='utf-8'))
tables={}
for node in tree.body:
 if isinstance(node,ast.Assign):
  for t in node.targets:
   if isinstance(t,ast.Name) and t.id in ('p1','p2','p3','p4','p5','P6','P7','P8'):
    tables[t.id]=ast.literal_eval(node.value)
paths=sum((tables[k] for k in ('p1','p2','p3','p4','p5','P6','P7','P8')),())
def sh(r):
 a=np.asarray(r.frame[-1],dtype=np.int16)
 return hashlib.sha256(a.tobytes()).hexdigest()[:18]
arc=Arcade(operation_mode=OperationMode.NORMAL)
e=arc.make('sk48')
records=[]; clicks=[]
for i,z in enumerate(paths):
 before=e._last_response
 h=sh(before);level=before.levels_completed
 data={}
 if z==6:
  g=e._game;other=next(k for k in g.xpmcmtbcv if k!=g.vzvypfsnt)
  data={'x':int(other.x+2),'y':int(other.y+2)}
  clicks.append((i+1,level,h,data))
 records.append((i,level,h,z,tuple(sorted(data.items()))))
 e.step(GameAction.from_id(z),data=data)
assert e._last_response.state.name=='WIN'
for span in (1,2,3,4,5,8,12,25):
 maps=defaultdict(set);n=0
 for i,l,h,z,data in records:
  key=(l,tuple(x[2] for x in records[max(0,i-span+1):i+1]))
  maps[key].add((z,data))
 collisions={k:v for k,v in maps.items() if len(v)>1}
 ambiguous=sum(1 for i,l,h,z,d in records if (l,tuple(x[2] for x in records[max(0,i-span+1):i+1])) in collisions)
 print('WINDOW',span,'UNIQUE',len(maps),'COLLISIONS',len(collisions),'AMBIGUOUS_STEPS',ambiguous,flush=True)
print('CLICK_COUNT',len(clicks),'CLICK_OBSERVATIONS',clicks,flush=True)
print('END',e._last_response.state.name,flush=True)
