"""SK48 Level5 separate positive-reference calibration; source disclaimed.

A previously saved 65-action Level5 native-history candidate is loaded
as a regression *only*. All upstream stages use verified alternative
routes with first-completion handoff. No private engine state.
"""
from pathlib import Path
import ast,json,numpy as np,logging,hashlib
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
R2=json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"]
L2=min((v for v in R2 if v["passed"] and v["different_from_saved_reference"]),key=lambda v:len(v["L2_actions"]))["L2_actions"]
L3=json.loads((F/"sk48_l3_native_fresh_macro_wins.json").read_text())["results"][0]["L3_path"]
L4=next(v["path"] for v in json.loads((F/"sk48_l4_native_reference_mutation_ab.json").read_text())["successful_interventions"] if v["method"]=="swap_adjacent")
tree=ast.parse((F/"_tmp_sk48_l5_ab_verification.py").read_text())
P5=None
for n in tree.body:
 if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="P5" for t in n.targets):
  P5=list(ast.literal_eval(n.value))
assert P5 and len(P5)==65
def enter():
 e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
 lengths=[]
 for target,route in enumerate((L1,L2,L3,L4),1):
  for k,z in enumerate(route,1):
   o=e.step(GameAction.from_id(z),data={})
   if o.levels_completed>=target:break
  assert o.levels_completed==target,(target,o.levels_completed)
  lengths.append(k)
 return e,o,lengths
t=[]
for trial in range(2):
 e,o,pre=enter()
 start=hashlib.sha256(frame(o).tobytes()).hexdigest()
 for n,z in enumerate(P5,1):
  o=e.step(GameAction.from_id(z),data={})
  if o.levels_completed>=5:break
 print("L5_OLD_POSITIVE_CONTROL","TRIAL",trial,
    "FIRST_WIN",n if o.levels_completed>=5 else None,
    "LEVEL",o.levels_completed,"P5_LEN",len(P5),
    "ENTRY",start,"UPSTREAM",pre,flush=True)
 t.append({"trial":trial,"L5_first_completion":n if o.levels_completed>=5 else None,
           "levels_completed":int(o.levels_completed),"entry_sha256":start,"upstream_action_consumed":pre})
out=F/"sk48_l5_saved_positive_control_calibration.json"
out.write_text(json.dumps({"source":"old saved local candidate P5 positive control",
 "provenance":"reference-assisted, never blind","saved_candidate_actions":P5,"trials":t},indent=2),encoding="utf-8")
print("SAVED",out,flush=True)
