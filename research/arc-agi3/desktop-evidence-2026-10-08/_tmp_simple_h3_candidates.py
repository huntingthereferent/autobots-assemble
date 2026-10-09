from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,hashlib,numpy as np,itertools
def H(r):return (hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12],r.state.name,r.levels_completed)
cfg={"g50t":([1,2,3,4,5],[1,3,5]),"tu93":([1,2,3,4],[1,2,3])}
arc=Arcade(operation_mode=OperationMode.NORMAL)
for name,(A,C) in cfg.items():
 root=arc.make(name); states={}
 for c in C:
  e=copy.deepcopy(root);e.step(GameAction.from_id(c),data={});states[c]=e
 print("\nGAME",name)
 for i,a in enumerate(C):
  for b in C[i+1:]:
   ea,eb=states[a],states[b]
   dif=[]
   va,vb=vars(ea._game),vars(eb._game)
   for k in sorted(set(va)|set(vb)):
    x,y=va.get(k),vb.get(k)
    if isinstance(x,(int,float,bool,str,type(None))) and isinstance(y,(int,float,bool,str,type(None))) and x!=y:dif.append((k,x,y))
    elif isinstance(x,(list,tuple,dict,set)) and isinstance(y,type(x)):
     try:
      if len(x)!=len(y):dif.append((k,"len",len(x),len(y)))
     except:pass
   first=None;diffcount=0
   for suf in itertools.product(A,repeat=3):
    qa,qb=copy.deepcopy(ea),copy.deepcopy(eb);ra=qa._last_response;rb=qb._last_response
    for z in suf:
     ra=qa.step(GameAction.from_id(z),data={});rb=qb.step(GameAction.from_id(z),data={})
     if ra.state.name!="NOT_FINISHED" or rb.state.name!="NOT_FINISHED":break
    if H(ra)!=H(rb):
     diffcount+=1
     if first is None:first=(suf,H(ra),H(rb))
   print("PAIR",a,b,"SCALAR",dif[:30],"H3_DIFF_SUFFIXES",diffcount,"FIRST",first)
