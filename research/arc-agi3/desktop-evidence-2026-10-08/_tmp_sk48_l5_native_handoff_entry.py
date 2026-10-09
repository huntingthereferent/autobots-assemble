"""SK48 native-public Level5 transfer through A/B corrected stage handoff.

No saved Level5 route or engine internals; choose verified alternative
Level2 and Level3 routes and an adjacent-swap Level4 route. Every stage
breaks immediately at its own native completion signal.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame
from _sk48_public_connected_goal import connected_features
from hashlib import sha256
import numpy as np,json,logging
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
L2=min((v for v in json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"] if v["passed"] and v["different_from_saved_reference"]),key=lambda v:len(v["L2_actions"]))["L2_actions"]
L3=json.loads((F/"sk48_l3_native_fresh_macro_wins.json").read_text())["results"][0]["L3_path"]
L4=json.loads((F/"sk48_l4_native_handoff_corrected.json").read_text())
swap=json.loads((F/"sk48_l4_native_reference_mutation_ab.json").read_text())
L4route=next(x["path"] for x in swap["successful_interventions"] if x["method"]=="swap_adjacent")
def enter():
 game=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
 lengths=[]
 for target,route in enumerate((L1,L2,L3,L4route),1):
  for k,z in enumerate(route,1):
   obs=game.step(GameAction.from_id(z),data={})
   if obs.levels_completed>=target:break
  else:raise RuntimeError(("stage failed",target))
  lengths.append(k)
 assert obs.levels_completed==4
 return game,obs,lengths
def pos(a,color):
 y,x=np.where(a[:53,:]==color)
 return [int(x.min()),int(y.min()),int(x.max()),int(y.max()),len(x)] if len(x) else None
rows=[]
for action in (None,1,2,3,4):
 e,o,used=enter();before=frame(o).copy()
 if action is not None:o=e.step(GameAction.from_id(action),data={})
 after=frame(o);q=connected_features(after)
 yy,xx=np.where(before!=after)
 row={"action":action,"level":int(o.levels_completed),"stage_action_consumed":used,
      "entry_sha":sha256(before.tobytes()).hexdigest(),
      "after_sha":sha256(after.tobytes()).hexdigest(),
      "reference":list(q["reference"]),"control_heads":q["controls"],
      "connected_sequences":[c["connected_colors"] for c in q["candidates"]],
      "changed_pixels":int(len(xx)),
      "color_positions":{str(color):pos(after,color) for color in (8,9,12,14,10,11,6,15)},
      "palette":{str(int(c)):int(n) for c,n in zip(*np.unique(after,return_counts=True))}}
 rows.append(row)
 print("LEVEL5_PUBLIC_ENTRY",row,flush=True)
out=F/"sk48_l5_native_public_handoff_entry.json"
out.write_text(json.dumps({"native_public_only":True,"L5_saved_route_used":False,
 "handoff_is_gated_at_each_level":True,"level5_probes":rows},indent=2),encoding="utf-8")
print("SAVED",out,flush=True)
