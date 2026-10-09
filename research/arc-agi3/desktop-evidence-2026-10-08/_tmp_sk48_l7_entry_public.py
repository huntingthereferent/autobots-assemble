"""SK48 Level7 native-public entry via alternates at Levels2-6.
No stored Level7 actions are used for the entrance or probe.
ACTION6 is resolved from visible 6x6 control heads, not private state.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame
from hashlib import sha256
import numpy as np,json,logging
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
L2=json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"][1]["L2_actions"]
L3=json.loads((F/"sk48_l3_native_fresh_macro_wins.json").read_text())["results"][1]["L3_path"]
L4=next(x["path"] for x in json.loads((F/"sk48_l4_native_reference_mutation_ab.json").read_text())["successful_interventions"] if x["method"]=="swap_adjacent")
L5=json.loads((F/"sk48_l5_native_fresh_swap_witnesses.json").read_text())["routes"][1]["actions"]
L6=json.loads((F/"sk48_l6_native_fresh_swap_witnesses.json").read_text())["results"][0]["route"]
def controls(a):
 found=[]
 for y in range(0,49):
  for x in range(0,55):
   v=int(a[y,x])
   if v not in (6,15):continue
   b=a[y:y+6,x:x+6]
   if b.shape!=(6,6) or not(np.all(b[0,:]==v) and np.all(b[:,0]==v)):continue
   if int(b[1,1]) not in (0,4) or not any(int(t)!=v for t in b[1:5,1:5].flat):continue
   found.append([x,y,v])
 return sorted(found,key=lambda q:q[0])
def enter():
 e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
 used=[]
 for level,p in enumerate((L1,L2,L3,L4,L5,L6),1):
  active=0
  for k,z in enumerate(p,1):
   if z==6:
    hs=controls(frame(o));x,y,_=hs[1-active]
    o=e.step(GameAction.ACTION6,data={"x":x+2,"y":y+2})
    active=1-active
   else:o=e.step(GameAction.from_id(z),data={})
   if o.levels_completed>=level:break
  if o.levels_completed!=level:raise RuntimeError(("handoff",level,o.levels_completed))
  used.append(k)
 return e,o,used
e,o,used=enter()
a=frame(o);digest=sha256(a.tobytes()).hexdigest()
print("LEVEL7_NATIVE_ROOT","LEVELS",o.levels_completed,"STAGES",used,
      "SHA",digest,"HEADS",controls(a),flush=True)
for y in range(0,62):
 s="".join("0123456789ABCDEF"[q] for q in a[y,2:62])
 if y in (2,3,7,12,19,25,26,27,28,31,37,43,56,57,58,59,60) or len(set(s))>6:
  print(f"LEVEL7_PUBLIC_ROW {y:02d} {s}",flush=True)
records=[]
for direction in (1,2,3,4):
 e,o,_=enter();b=frame(o).copy()
 nextobs=e.step(GameAction.from_id(direction),data={})
 c=frame(nextobs);ys,xs=np.where(c!=b)
 item={"direction":direction,"pixel_diff":len(xs),"level":int(nextobs.levels_completed),
       "sha":sha256(c.tobytes()).hexdigest()}
 records.append(item)
 print("L7_ONE_STEP",item,flush=True)
out=F/"sk48_l7_native_public_entry.json"
out.write_text(json.dumps({"entry_level_completed":6,"stage_consumption":used,
 "entry_sha":digest,"visible_controls":controls(a),
 "prior_routes_reference_assisted":True,"saved_L7_route_used":False,
 "immediate_action_probes":records},indent=2),encoding="utf-8")
print("SAVED",out,flush=True)
