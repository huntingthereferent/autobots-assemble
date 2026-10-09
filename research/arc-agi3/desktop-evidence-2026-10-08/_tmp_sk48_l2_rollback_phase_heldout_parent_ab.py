"""SK48 A/B rollback phase held-out parent-state transfer.

Does 'same public frame + number of action/undo cycles' retain predictive
closure at newly reached Level2 parents, or is it only the entry-state
relation? No private native state or saved L2 solution.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from hashlib import sha256
import json,logging,numpy as np
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
g=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
def H(o):
 return "%d:%s:%s"%(o.levels_completed,o.state.name,sha256(np.asarray(o.frame[-1],dtype=np.uint8).tobytes()).hexdigest()[:18])
def enter(parent):
 for j in range(8):
  o=g.step(GameAction.RESET,data={})
  if o.levels_completed==0:break
 else:raise RuntimeError("RESET boundary")
 for z in L1:o=g.step(GameAction.from_id(z),data={})
 assert o.levels_completed==1
 for z in parent:o=g.step(GameAction.from_id(z),data={})
 return o
parents=[(),(1,),(4,),(1,4),(4,1),(4,4),(1,1),(3,)]
report=[]
for parent in parents:
 p=enter(parent);base=H(p)
 states={}
 for cycles in range(4):
  variants=[]
  for probe in (1,4):
   before=enter(parent)
   assert H(before)==base, ("native parent replay changed",parent)
   history=[]
   clean=True
   for i in range(cycles):
    o=g.step(GameAction.from_id(probe),data={})
    o=g.step(GameAction.ACTION7,data={})
    history.append(H(o))
    if H(o)!=base:
     clean=False;break
   if clean:
    next_frame=g.step(GameAction.ACTION4,data={})
    result=H(next_frame)
   else:result=None
   variants.append({"cycle_action":probe,"returned_to_same_public":clean,
                    "continuation_action4":result,"cycle_observations":history})
  states[str(cycles)]=variants
 row={"parent":parent,"public_parent":base,"cycles":states}
 report.append(row)
 print("HELDOUT_PARENT",parent,"FIRST_DIFFERING_CYCLE",
       next((i for i in range(1,4) if states[str(i)][0]["continuation_action4"]!=states["0"][0]["continuation_action4"]),None),
       "CYCLE_ACTIONS_AGREE",[(i,states[str(i)][0]["continuation_action4"]==states[str(i)][1]["continuation_action4"]) for i in range(4)],
       "RETURNED",[all(v["returned_to_same_public"] for v in states[str(i)]) for i in range(4)],flush=True)
out=F/"sk48_l2_rollback_phase_heldout_parent_ab.json"
out.write_text(json.dumps({"native_public_only":True,"parents_tested":len(parents),
 "rollback_actions":[1,4],"repeats":[0,1,2,3],"next_action":4,
 "results":report},indent=2),encoding="utf-8")
print("SAVED",out,flush=True)
