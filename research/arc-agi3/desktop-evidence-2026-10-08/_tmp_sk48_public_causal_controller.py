"""SK48 public causal controller for the already-discovered 280-direction route.

Click targets AND which of two controls is active are inferred from public
frame differences; never accesses the engine's private _game state.
This is replay of learned direction sequence, not an independent new-game plan.
"""
from pathlib import Path
from collections import Counter
import json,hashlib,logging
import numpy as np
from arc_agi import Arcade,OperationMode
from arcengine import GameAction,GameState

src=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\_tmp_sk48_public_switch_route.py").read_text()
ns={}
exec(src.split("logging.disable(logging.CRITICAL)")[0],ns)
actions=ns["actions"]; top_keys=ns["top_keys"]; frame=ns["frame"]

def active_from_movement(before,after,prior):
 old=top_keys(before);new=top_keys(after)
 if len(old)!=2 or len(new)!=2:return prior,None
 moved=[i for i in range(2) if old[i][:2]!=new[i][:2]]
 if len(moved)==1:return moved[0], moved[0]
 if len(moved)>1:return None,"ambiguous"
 return prior,None

logging.disable(logging.CRITICAL)
output=[]
for trial in range(2):
 arc=Arcade(operation_mode=OperationMode.NORMAL);game=arc.make("sk48")
 active=None;milestones=[];clicks=[];changed_motion=Counter();reset_hypotheses=[];wall=None;last_level=0
 for step,z in enumerate(actions,1):
  before=game.observation_space
  if z==6:
   keys=top_keys(before)
   if len(keys)!=2:
    wall={"at_step":step,"reason":"public controls not isolated","keys":keys,"active":active}
    break
   if active is None:
    # Hypothesis learned from prior level starts; validate via future native
    # completions rather than pretending the frame proves the control.
    active=0
    reset_hypotheses.append({"step":step,"level":int(before.levels_completed)+1})
   chosen=1-active
   x,y,color=keys[chosen]
   click=(x+2,y+2)
   after=game.step(GameAction.ACTION6,data={"x":click[0],"y":click[1]})
   clicks.append({"step":step,"level":int(before.levels_completed)+1,
                  "chosen_key":chosen,"coordinate":click,"native_source":"public_frame"})
   active=chosen
  else:
   after=game.step(GameAction.from_id(z),data={})
   if after.levels_completed==before.levels_completed:
    active,change=active_from_movement(before,after,active)
    if change is not None:changed_motion[str(change)]+=1
  if after.levels_completed>last_level:
   last_level=after.levels_completed
   milestones.append({"action":step,"levels_completed":last_level})
   active=None
  if after.state.name in ("GAME_OVER","WIN"):break
 result={
  "trial":trial,"status":after.state.name,"levels":after.levels_completed,
  "actions":step,"local_sdk_score":arc.get_scorecard().score,
  "milestones":milestones,"clicks":clicks,"motion_classifications":dict(changed_motion),
  "unresolved_initial_control_hypotheses":reset_hypotheses,
  "wall":wall,
 }
 output.append(result)
 print("PUBLIC_CAUSAL",trial,"STATUS",result["status"],"LEVELS",result["levels"],
       "STEPS",step,"CLICKS",len(clicks),"MOTION",dict(changed_motion),
       "WALL",wall,"MILESTONES",milestones,flush=True)

path=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\sk48_public_causal_280.json")
path.write_text(json.dumps({"game":"sk48","method":"public-frame movement inferred control + saved directional replay",
                            "no_engine_private_reads":True,"not_independently_solved":True,
                            "runs":output},indent=2),encoding="utf-8")
print("SAVED",path,flush=True)
