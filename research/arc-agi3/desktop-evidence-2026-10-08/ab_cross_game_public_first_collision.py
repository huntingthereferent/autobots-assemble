from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib,copy
from collections import defaultdict
from ab_family_closure import Occurrence,ab_family

GAMES=["bp35","cd82","dc22","ft09","g50t","ka59","lf52","lp85","ls20","m0r0","r11l","re86","s5i5","sb26","sc25","sk48","sp80","su15","tn36","tr87","tu93","vc33","wa30"]
PROBES=[("rep1",[1]*10),("rep2",[2]*10),("rep3",[3]*10),("rep4",[4]*10),("rep5",[5]*10),
("alt12",[1,2]*5),("alt34",[3,4]*5),("alt45",[4,5]*5),("alt54",[5,4]*5)]

def fh(r):
 if not getattr(r,"frame",None):return "EMPTY"
 try:return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]
 except:return hashlib.sha1(repr(r.frame).encode()).hexdigest()[:12]

a=Arcade(operation_mode=OperationMode.NORMAL)
for game in GAMES:
 try:base=a.make(game)
 except Exception as ex:
  print(game,"MAKE_FAIL",type(ex).__name__);continue
 occ=[]
 for pname,seq in PROBES:
  e=copy.deepcopy(base); prior=[]; cur="START"
  for t,z in enumerate(seq):
   outs=[]
   for az in [1,2,3,4,5]:
    q=copy.deepcopy(e)
    try:
     rr=q.step(GameAction.from_id(az),data={})
     outs.append((az,fh(rr),rr.levels_completed,rr.state.name))
    except Exception as ex:
     outs.append((az,"ERR",type(ex).__name__,None))
   rel=tuple((f"prev{i}",prior[-i] if len(prior)>=i else None) for i in range(1,5))+(("probe",pname),)
   occ.append(Occurrence(cur,rel,tuple(outs)))
   try:r=e.step(GameAction.from_id(z),data={})
   except Exception:break
   cur=fh(r);prior.append(cur)
   if r.state.name!="NOT_FINISHED":break
 try:states=ab_family(occ)
 except Exception as ex:
  print(game,"AB_FAIL",type(ex).__name__,str(ex)[:80],flush=True);continue
 split={k:v for k,v in states.items() if v.retained_names}
 print(game,"RAW",len(states),"SPLIT",len(split),flush=True)
 for ref,s in list(split.items())[:6]:print(" ",ref,"=>",s.retained_names,flush=True)
 if split:
  break
