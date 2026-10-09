"""SK48 Level6 public native entry via verified alternative Level5 path.

Strict first-completion handoff at all five levels, never replay
actions after a native level transition. No saved Level6 route.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame
import json,numpy as np,hashlib,logging
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
L2=min((x for x in json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"] if x["passed"] and x["different_from_saved_reference"]),key=lambda x:len(x["L2_actions"]))["L2_actions"]
L3=json.loads((F/"sk48_l3_native_fresh_macro_wins.json").read_text())["results"][0]["L3_path"]
L4=next(x["path"] for x in json.loads((F/"sk48_l4_native_reference_mutation_ab.json").read_text())["successful_interventions"] if x["method"]=="swap_adjacent")
L5=json.loads((F/"sk48_l5_native_fresh_swap_witnesses.json").read_text())["routes"][0]["actions"]
def enter():
 e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
 stage=[]
 for target,seq in enumerate((L1,L2,L3,L4,L5),1):
  for k,z in enumerate(seq,1):
   o=e.step(GameAction.from_id(z),data={})
   if o.levels_completed>=target:break
  assert o.levels_completed==target
  stage.append(k)
 return e,o,stage
rootgame,root,stage=enter()
arr=frame(root)
print("L6_ROOT","NATIVE_LEVEL",root.levels_completed,"STAGE_COUNTS",stage,
  "SHA",hashlib.sha256(arr.tobytes()).hexdigest(),flush=True)
for y in range(6,62):
 s="".join("0123456789ABCDEF"[v] for v in arr[y,2:62])
 if len(set(s))>5 or y in (7,12,19,25,26,27,28,31,37,43,56,57,58,59,60):
  print("L6_BOARD",y,s,flush=True)
for color in (8,9,12,14,6,15):
 yy,xx=np.where(arr[:53,:]==color)
 print("L6_PALETTE",color,"N",len(xx),"BOX",
   [int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())] if len(xx) else None,flush=True)
records=[]
for z in (1,2,3,4):
 e,o,_=enter()
 before=frame(o).copy()
 o=e.step(GameAction.from_id(z),data={})
 after=frame(o)
 yy,xx=np.where(before!=after)
 item={"action":z,"level":int(o.levels_completed),"pixel_changes":len(xx),
       "native_sha":hashlib.sha256(after.tobytes()).hexdigest()}
 records.append(item)
 print("L6_NATIVE_PROBE",item,flush=True)
out=F/"sk48_l6_native_public_entry.json"
out.write_text(json.dumps({"native_levels_completed":5,
 "entry_via_new_7way_verified_L5_alternative":True,
 "entry_sha":hashlib.sha256(arr.tobytes()).hexdigest(),
 "stage_consumed_actions":stage,
 "action_probes":records},indent=2),encoding="utf-8")
print("SAVED",out,flush=True)
