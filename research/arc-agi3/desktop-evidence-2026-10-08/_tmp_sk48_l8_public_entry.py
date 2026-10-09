"""SK48 Level8 native public entry from alternative Level7.
No previously saved Level8 actions. Public observations only.
"""
from _sk48_native_public_stage_harness import enter,run_level,F,controls
from _sk48_public_goal_sensor import frame
from hashlib import sha256
import numpy as np,json,logging
from arcengine import GameAction
logging.disable(logging.CRITICAL)
L7=json.loads((F/"sk48_l7_native_fresh_swaps.json").read_text())["routes"][0]["route"]
def enter8(selector=0):
 e,o,previous=enter(7,selector=selector)
 o,used,clicks=run_level(e,o,L7,7)
 assert o.levels_completed==7
 return e,o,previous,used,clicks
e,o,prior,used,clicks=enter8()
a=frame(o).copy()
print("L8_ROOT",int(o.levels_completed),"SHA",sha256(a.tobytes()).hexdigest(),
 "L7_LAST",used,"HEADS",controls(a),flush=True)
for y in range(0,62):
 s="".join("0123456789ABCDEF"[v] for v in a[y,2:62])
 if y in (2,3,7,12,19,25,26,27,28,31,37,43,56,57,58,59,60) or len(set(s))>6:
  print("L8_BOARD",y,s,flush=True)
probes=[]
for move in (1,2,3,4):
 e,o,prior,used,clicks=enter8()
 before=frame(o).copy()
 o=e.step(GameAction.from_id(move),data={})
 b=frame(o)
 rec={"move":move,"levels":int(o.levels_completed),
      "changed":int(np.count_nonzero(b!=before)),
      "sha":sha256(b.tobytes()).hexdigest()}
 probes.append(rec)
 print("L8_DIRECTIONAL",rec,flush=True)
out=F/"sk48_l8_native_public_entry.json"
out.write_text(json.dumps({"public_only":True,"old_L8_route_loaded":False,
 "entry_sha":sha256(a.tobytes()).hexdigest(),"native_completed_prior":7,
 "head_positions":controls(a),"first_direction_probes":probes},indent=2),encoding="utf-8")
print("SAVED",out,flush=True)
