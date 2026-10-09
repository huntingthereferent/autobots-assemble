"""SK48 L6 A/B: which public visual control moves after native selection?"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame
import numpy as np,json,logging
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
L2=min((x for x in json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"] if x["passed"] and x["different_from_saved_reference"]),key=lambda x:len(x["L2_actions"]))["L2_actions"]
L3=json.loads((F/"sk48_l3_native_fresh_macro_wins.json").read_text())["results"][0]["L3_path"]
L4=next(x["path"] for x in json.loads((F/"sk48_l4_native_reference_mutation_ab.json").read_text())["successful_interventions"] if x["method"]=="swap_adjacent")
L5=json.loads((F/"sk48_l5_native_fresh_swap_witnesses.json").read_text())["routes"][0]["actions"]
def enter():
 e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
 for n,path in enumerate((L1,L2,L3,L4,L5),1):
  for z in path:
   o=e.step(GameAction.from_id(z),data={})
   if o.levels_completed>=n:break
 assert o.levels_completed==5
 return e,o
for move in (1,2,3,4):
 for selected in ("lower_default","upper_click"):
  e,o=enter()
  if selected=="upper_click":
   o=e.step(GameAction.ACTION6,data={"x":31,"y":4})
  before=frame(o).copy()
  after=e.step(GameAction.from_id(move),data={})
  b=frame(after)
  q={"move":move,"selected":selected,
      "changed_top_0to17":int(np.count_nonzero(b[:18,:]!=before[:18,:])),
      "changed_center_18to35":int(np.count_nonzero(b[18:36,:]!=before[18:36,:])),
      "changed_bottom_36to53":int(np.count_nonzero(b[36:54,:]!=before[36:54,:])),
      "native_level":int(after.levels_completed)}
  print("LEVEL6_SELECTED_AB",json.dumps(q),flush=True)
