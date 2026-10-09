from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,itertools,hashlib
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
MEET=[2,2,2,1,1]
ACTS=[1,2,3,4,5,7]
e=a.make('ar25');r=None
for z in SOL+MEET+[5]: r=e.step(GameAction.from_id(z),data={})
root=copy.deepcopy(e)
rootk=r.frame[0].tobytes()
def run(word):
 x=copy.deepcopy(root); rr=r
 for z in word: rr=x.step(GameAction.from_id(z),data={})
 return rr.levels_completed,rr.state.name,rr.frame[0].tobytes()
print("X5",r.levels_completed,r.state.name,hashlib.sha1(rootk).hexdigest()[:12])
for d in [1,2,3]:
 ws=list(itertools.product(ACTS,repeat=d)); classes={}
 for w in ws:
  L,S,k=run(w); classes.setdefault((L,S,k),[]).append(w)
 print("DEPTH",d,"WORDS",len(ws),"CLASSES",len(classes))
 for g in sorted(classes.values(), key=lambda g:(len(g[0]),g[0])):
  if len(g)>1 or d==1: print("CLASS",g)
  for w in g:
   L,S,k=run(w)
   if L>2: print("SOLVED",w,L,S); raise SystemExit
# direct relations around 3/4
pairs=[((3,),(4,)),((3,3),(4,4)),((3,4),(4,3)),((5,3),(5,4)),((3,5),(4,5))]
for u,v in pairs: print("REL",u,v,run(u)==run(v))
