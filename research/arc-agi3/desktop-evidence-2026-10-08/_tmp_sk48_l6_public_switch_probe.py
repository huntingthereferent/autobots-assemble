"""SK48 Level6 native-public two-control switch witness.
Level6 entered via fresh-verified alternates on Levels 1-5.
ACTION6 clicks are selected from observed bordered public 6x6 controls.
No saved Level6 route, private SDK engine, or copying.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame,head_and_controls
from hashlib import sha256
import json,numpy as np,logging
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
L2=min((x for x in json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"] if x["passed"] and x["different_from_saved_reference"]),key=lambda x:len(x["L2_actions"]))["L2_actions"]
L3=json.loads((F/"sk48_l3_native_fresh_macro_wins.json").read_text())["results"][0]["L3_path"]
L4=next(x["path"] for x in json.loads((F/"sk48_l4_native_reference_mutation_ab.json").read_text())["successful_interventions"] if x["method"]=="swap_adjacent")
L5=json.loads((F/"sk48_l5_native_fresh_swap_witnesses.json").read_text())["routes"][0]["actions"]
def enter():
 e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
 for goal,seq in enumerate((L1,L2,L3,L4,L5),1):
  for z in seq:
   obs=e.step(GameAction.from_id(z),data={})
   if obs.levels_completed>=goal:break
  assert obs.levels_completed==goal
 return e,obs
rows=[]
for move in (None,1,2,3,4):
 e,o=enter();a=frame(o).copy()
 heads=head_and_controls(a)
 # The existing head detector starts at y=6; Level6 has a second
 # native 15-bordered control above it, whose pixels begin at y=2.
 yy,xx=np.where(a[:53,:]==15)
 assert len(xx)>=16
 heads.append((int(xx.min()),int(yy.min()),15))
 assert len(heads)==2,heads
 chosen=next((h for h in heads if h[2]==15),None)
 assert chosen is not None,heads
 x,y,color=chosen
 switched=e.step(GameAction.ACTION6,data={"x":x+2,"y":y+2})
 changed=int(np.count_nonzero(a!=frame(switched)))
 f=frame(switched).copy()
 result=switched
 if move is not None:
  result=e.step(GameAction.from_id(move),data={})
 b=frame(result)
 row={"after_switch_action":move,"click":[x+2,y+2],
      "public_heads":heads,"switch_changed_pixels":changed,
      "total_changed_pixels":int(np.count_nonzero(a!=b)),
      "level":int(result.levels_completed),
      "before_sha":sha256(a.tobytes()).hexdigest(),
      "after_sha":sha256(b.tobytes()).hexdigest()}
 rows.append(row)
 print("SK48_L6_PUBLIC_SWITCH",row,flush=True)
out=F/"sk48_l6_public_native_control_switch.json"
out.write_text(json.dumps({"source":"native public control click","saved_L6_route_used":False,
 "stage_gate":"first native completion","tests":rows},indent=2),encoding="utf-8")
print("SAVED",out,flush=True)
