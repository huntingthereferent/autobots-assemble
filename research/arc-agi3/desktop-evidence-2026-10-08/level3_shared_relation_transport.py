from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,itertools
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
MEET=[2,2,2,1,1]
ACTS=[1,2,3,4,5,7]
e=a.make('ar25');r=None
for z in SOL+MEET:r=e.step(GameAction.from_id(z),data={})
root=copy.deepcopy(e)
def key(word):
 x=copy.deepcopy(root); rr=r
 for z in word: rr=x.step(GameAction.from_id(z),data={})
 return rr.levels_completed,rr.state.name,rr.frame[0].tobytes()
rels=[((2,),(1,7,7),'2=177'),((3,),(), '3=e'),((4,),(), '4=e')]
for depth in [0,1,2]:
 prefs=[()] if depth==0 else list(itertools.product(ACTS,repeat=depth))
 print("PREFIX_DEPTH",depth,"N",len(prefs))
 for lhs,rhs,name in rels:
  fail=[]
  for p in prefs:
   if key(p+lhs)!=key(p+rhs): fail.append(p)
  print(name,"FAIL",len(fail),"OF",len(prefs),"FIRST",fail[:20])
