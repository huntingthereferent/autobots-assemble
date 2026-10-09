"""A/B the native successful SK48 reference and public-frame alternative."""
from pathlib import Path
import numpy as np,hashlib,logging
from arc_agi import Arcade, OperationMode
from arcengine import GameAction,GameState
src=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\_tmp_sk48_public_switch_route.py").read_text()
parts=src.split("logging.disable(logging.CRITICAL)")[0]
ns={}
exec(parts,ns)
actions=ns["actions"]; top_keys=ns["top_keys"]; frame=ns["frame"]
logging.disable(logging.CRITICAL)
a=Arcade(operation_mode=OperationMode.NORMAL); ref=a.make("sk48")
b=Arcade(operation_mode=OperationMode.NORMAL); pub=b.make("sk48")
active_idx=0;prev=0
for step,z in enumerate(actions,1):
 native=ref._game
 expected=None;actual=None;active_before=None
 if z==6:
  pairs=list(native.xpmcmtbcv.items())
  active=native.vzvypfsnt
  active_before=next(((kind,i) for i,(key,mate) in enumerate(pairs)
   for kind,v in (("key",key),("mate",mate)) if v is active),None)
  expected=next((int(key.x+2),int(key.y+2)) for key,mate in pairs if key is not active)
  keys=top_keys(pub.observation_space)
  if len(keys)!=2: raise RuntimeError(("missing public keys",step,keys))
  choice=(1 if active_idx==0 else 0)
  x,y,_=keys[choice];actual=(x+2,y+2)
  r_ref=ref.step(GameAction.ACTION6,data={"x":expected[0],"y":expected[1]})
  r_pub=pub.step(GameAction.ACTION6,data={"x":actual[0],"y":actual[1]})
  active_idx=choice
  print("SWITCH",step,"LEVEL",prev,"ACTIVE_BEFORE",active_before,"EXPECTED",expected,
        "PUBLIC",actual,"KEYS",keys,"MATCH",np.array_equal(frame(r_ref),frame(r_pub)),flush=True)
 else:
  r_ref=ref.step(GameAction.from_id(z),data={})
  r_pub=pub.step(GameAction.from_id(z),data={})
 if not np.array_equal(frame(r_ref),frame(r_pub)) or r_ref.levels_completed !=r_pub.levels_completed:
  print("FIRST_DIVERGENCE",step,"ACT",z,"REF_LEVEL",r_ref.levels_completed,
     "PUB_LEVEL",r_pub.levels_completed,
     "PIXEL_DIFFERENCES",int(np.count_nonzero(frame(r_ref)!=frame(r_pub))),flush=True)
  break
 if r_ref.levels_completed!=prev:
  prev=r_ref.levels_completed;active_idx=0
else:print("IDENTICAL_ALL",len(actions),r_ref.state.name,flush=True)
