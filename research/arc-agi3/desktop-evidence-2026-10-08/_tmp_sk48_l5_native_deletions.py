"""SK48 Level5 positive route deletion A/B, native public first-completion oracle.

Every test uses acknowledged RESET, witnessed L1-L4 stage handoff and
native Level5 completion. This is reference-assisted action necessity
analysis; NOT a blind solver. No game cloning or private engine reads.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame
import json,numpy as np,hashlib,logging,time
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
L2=min((v for v in json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"]
 if v["passed"] and v["different_from_saved_reference"]),key=lambda v:len(v["L2_actions"]))["L2_actions"]
L3=json.loads((F/"sk48_l3_native_fresh_macro_wins.json").read_text())["results"][0]["L3_path"]
L4=next(v["path"] for v in json.loads((F/"sk48_l4_native_reference_mutation_ab.json").read_text())["successful_interventions"] if v["method"]=="swap_adjacent")
P5=json.loads((F/"sk48_l5_saved_positive_control_calibration.json").read_text())["saved_candidate_actions"]
OUT=F/"sk48_l5_native_single_delete_ab.json"
g=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
calls=0;extra=0;root=None
def advance(z):
 global calls
 o=g.step(z,data={});calls+=1;return o
def enter():
 global root,extra
 for t in range(8):
  o=advance(GameAction.RESET)
  if o.levels_completed==0:break
  extra+=1
 else:raise RuntimeError("RESET not acknowledged")
 for goal,sequence in enumerate((L1,L2,L3,L4),1):
  for z in sequence:
   o=advance(GameAction.from_id(z))
   if o.levels_completed>=goal:break
  if o.levels_completed!=goal:raise RuntimeError(("handoff",goal))
 now=hashlib.sha256(frame(o).tobytes()).hexdigest()
 if root is None:root=now
 if root!=now:raise RuntimeError("Level5 entry drift")
 return o
def test(path):
 enter()
 for i,z in enumerate(path,1):
  o=advance(GameAction.from_id(z))
  if o.levels_completed>=5:return {"pass":True,"completion":i,"level":int(o.levels_completed)}
 return {"pass":False,"completion":None,"level":int(o.levels_completed)}
t=time.monotonic()
base=test(P5);assert base["pass"] and base["completion"]==65
out=[]
for i in range(len(P5)):
 variant=P5[:i]+P5[i+1:]
 result=test(variant)
 row={"removed_index":i,"removed_action":P5[i],"first_completed":result["completion"],
      "success":result["pass"],"result_level":result["level"],"candidate":variant if result["pass"] else None}
 out.append(row)
 if result["pass"]:print("L5_DELETION_SURVIVES","INDEX",i,"ACTION",P5[i],
                         "WIN_STEP",result["completion"],flush=True)
 if (i+1)%10==0:
  print("L5_AB_PROGRESS",i+1,"OF",len(P5),"SUCCESS",sum(x["success"] for x in out),
        "NATIVE_CALLS",calls,"SEC",round(time.monotonic()-t,2),flush=True)
 obj={"native_public_only":True,"source":"old positive route, reference-assisted deletion A/B",
      "baseline":base,"tests":out,"survivors":[x for x in out if x["success"]],
      "reset_retries":extra,"native_calls":calls}
 OUT.write_text(json.dumps(obj,indent=2),encoding="utf-8")
print("L5_AB_DONE","SURVIVORS",sum(x["success"] for x in out),
      "TESTS",len(out),"SECONDS",round(time.monotonic()-t,2),"SAVED",OUT,flush=True)
