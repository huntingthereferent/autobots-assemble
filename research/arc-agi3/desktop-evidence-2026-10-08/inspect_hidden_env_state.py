from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,pprint
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
MEET=[2,2,2,1,1]
base=a.make('ar25');r0=None
for z in SOL+MEET:r0=base.step(GameAction.from_id(z),data={})
def run(w):
 e=copy.deepcopy(base);r=r0
 for z in w:r=e.step(GameAction.from_id(z),data={})
 return e,r
for w in [(2,),(1,7,7),(7,2,7)]:
 e,r=run(w)
 print("\nWORD",w)
 print("R_TYPE",type(r), "R_DICT",getattr(r,'__dict__',None))
 print("E_TYPE",type(e))
 d=getattr(e,'__dict__',{})
 print("E_KEYS",list(d.keys()))
 for k,v in d.items():
  if k.startswith('_') or k in ('game','_game'):
   try:
    print(" ",k,type(v),getattr(v,'__dict__',None))
   except Exception as ex: print(" ",k,type(v),ex)
  elif isinstance(v,(int,float,str,bool,type(None),tuple,list,dict)):
   print(" ",k,repr(v)[:1000])
