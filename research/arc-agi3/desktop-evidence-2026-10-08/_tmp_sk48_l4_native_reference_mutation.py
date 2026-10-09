"""SK48 native Level4 positive-reference A/B minimal mutation.

Each candidate changes exactly one known Level4 route element: delete
one move or exchange adjacent different moves. Fresh native RESET ack,
verified Level4 entry, then returned levels_completed determines result.
No game cloning or private state; not blind Level4 discovery.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame
from hashlib import sha256
import json,logging,time
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
L2=min((v for v in json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"]
 if v["passed"] and v["different_from_saved_reference"]),key=lambda v:len(v["L2_actions"]))["L2_actions"]
L3=json.loads((F/"sk48_l3_native_fresh_macro_wins.json").read_text())["results"][0]["L3_path"]
REF=json.loads((F/"sk48_l4_positive_regression_calibration.json").read_text())["positive_L4_actions"]
def variants():
 yield {"method":"reference_control","edit":None,"path":REF}
 for i in range(len(REF)):
  yield {"method":"remove_one_action","edit":i,"path":REF[:i]+REF[i+1:]}
 for i in range(len(REF)-1):
  if REF[i]==REF[i+1]:continue
  p=REF.copy();p[i],p[i+1]=p[i+1],p[i]
  yield {"method":"swap_adjacent","edit":i,"path":p}
game=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
calls=0;reset_retry=0;root=None
def step(z):
 global calls
 o=game.step(z,data={});calls+=1;return o
def test(seq):
 global root,reset_retry
 for n in range(8):
  o=step(GameAction.RESET)
  if o.levels_completed==0:break
  reset_retry+=1
 else:raise RuntimeError("native RESET wall")
 for z in L1+L2+L3:o=step(GameAction.from_id(z))
 if o.levels_completed!=3:raise RuntimeError("Level4 entry not reproduced")
 current=sha256(frame(o).tobytes()).hexdigest()
 if root is None:root=current
 if current!=root:raise RuntimeError("Level4 entry frame changed")
 for k,z in enumerate(seq,1):
  o=step(GameAction.from_id(z))
  if o.levels_completed>=4:
   return k,int(o.levels_completed)
 return None,int(o.levels_completed)
rows=[];wins=[];t0=time.monotonic()
for candidate in variants():
 hit,level=test(candidate["path"])
 rec={**candidate,"first_win_action":hit,"native_level":level,
      "success":hit is not None}
 rows.append(rec)
 if rec["success"]:
  wins.append(rec)
  print("L4_NATIVE_AB_SURVIVES",rec["method"],rec["edit"],
        "INPUT_LEN",len(rec["path"]),"WIN_ACTION",hit,flush=True)
print("L4_AB_MUTATIONS","TOTAL",len(rows),"WIN",len(wins),
      "BY_METHOD",{m:sum(x["success"] for x in rows if x["method"]==m)
                   for m in ("reference_control","remove_one_action","swap_adjacent")},
      "NATIVE_CALLS",calls,"SECONDS",round(time.monotonic()-t0,2),flush=True)
out=F/"sk48_l4_native_reference_mutation_ab.json"
out.write_text(json.dumps({"method":"reference-assisted single-action or adjacent-order intervention",
 "native_public_only":True,"old_saved_L4_route_was_source":True,
 "root_native_sha":root,"results":rows,"successful_interventions":wins,
 "calls":calls,"reset_retry":reset_retry},indent=2),encoding="utf-8")
print("SAVED",out,flush=True)
