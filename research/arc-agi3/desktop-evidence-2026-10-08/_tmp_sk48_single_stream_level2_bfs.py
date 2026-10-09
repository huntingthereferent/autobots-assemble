"""SK48 Level 2 single-live-stream A/B frontier.

Starts Level 2 by replaying the independently discovered Level 1 path.
No game cloning and no L2 route available to this script. Native RESET
before every branch; observed public state verifies replay fidelity.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
from hashlib import sha256
import json,time,logging
import numpy as np
from arc_agi import Arcade, OperationMode
from arcengine import GameAction
logging.disable(logging.CRITICAL)
FOLDER=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((FOLDER/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
OUT=FOLDER/"sk48_live_single_stream_level2_frontier.json"
arcade=Arcade(operation_mode=OperationMode.NORMAL)
game=arcade.make("sk48")
def key(o):
 return (int(o.levels_completed),o.state.name,
         sha256(np.asarray(o.frame[-1],dtype=np.uint8).tobytes()).hexdigest())
reset_attempts=0
reset_retries=0
def goto_level2():
 global reset_attempts,reset_retries
 for retry in range(8):
  o=game.step(GameAction.RESET,data={})
  reset_attempts+=1
  if o.levels_completed==0:break
  reset_retries+=1
 else:raise RuntimeError("native RESET not acknowledged; preserve boundary")
 for z in L1:o=game.step(GameAction.from_id(z),data={})
 if o.levels_completed!=1:
  raise RuntimeError(("L1 witnessed route no longer enters L2",o.levels_completed))
 return o
initial=goto_level2()
start_key=key(initial)
start_pixels=np.asarray(initial.frame[-1],dtype=np.uint8).copy().reshape(64,64)
front=[((),start_key)];seen={start_key:()}
history=[]
n_actions=len(L1)+1;edges=0
sol=None;start=time.monotonic();mismatches=0
for depth in range(1,32):
 next_front=[]
 counters=Counter()
 for path,parent in front:
  for z in (1,2,3,4):
   now=goto_level2()
   n_actions+=len(L1)+1
   if key(now)!=start_key:
    dd=np.asarray(now.frame[-1],dtype=np.uint8).reshape(64,64)!=start_pixels
    yy,xx=np.where(dd)
    print("REPLAY_START_COUNTEREXAMPLE", "EXPECTED",start_key,"ACTUAL",key(now),"PARENT_PATH",path,"PIXELS",int(dd.sum()),"BOX",(int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())) if len(xx) else None,flush=True)
    raise RuntimeError("L2 replay start changed")
   for a in path:
    now=game.step(GameAction.from_id(a),data={})
    n_actions+=1
   if key(now)!=parent:
    mismatches+=1
    raise RuntimeError(("L2 replay state disagrees",depth,path,parent,key(now)))
   after=game.step(GameAction.from_id(z),data={})
   n_actions+=1;edges+=1
   child=key(after)
   counters["MOVE" if child!=parent else "PRESERVE"]+=1
   if after.levels_completed>=2:
    sol={"L2_actions":list(path+(z,)),"L2_length":len(path)+1,
         "completed_levels":int(after.levels_completed),
         "status":after.state.name,"native_end_frame":child[2]}
    break
   if after.state.name=="GAME_OVER":
    counters["GAME_OVER"]+=1
    continue
   if child not in seen:
    seen[child]=path+(z,)
    next_front.append((path+(z,),child))
  if sol:break
 record={"depth":depth,"states_at_depth":len(front),
         "new_unique":len(next_front),"total_unique":len(seen),
         "expanded_edges":edges,"native_actions":n_actions+reset_retries,"reset_retries":reset_retries,
         "seconds":round(time.monotonic()-start,2),
         "next_move_types":dict(counters)}
 history.append(record)
 print("L2_AB",record,flush=True)
 if sol or not next_front:break
 front=next_front
 if time.monotonic()-start>85 or len(seen)>4000 or n_actions>130000:
  print("L2_WALL bounded resource frontier, no closure yet",flush=True);break
result={"game":"sk48","level":2,"method":"single native live game, reset + verified Level 1 replay",
        "loaded_saved_l2_solution":False,"used_deepcopy":False,"used_private_engine":False,
        "previously_discovered_L1_actions":len(L1),
        "level2_solution":sol,"replay_mismatches":mismatches,
        "states_seen":len(seen),"edges":edges,"native_actions":n_actions+reset_retries,
        "reset_retries":reset_retries,
        "elapsed_seconds":round(time.monotonic()-start,2),
        "depths":history}
OUT.write_text(json.dumps(result,indent=2),encoding="utf-8")
print("L2_SUMMARY",json.dumps({k:v for k,v in result.items() if k!="depths"}),flush=True)
print("EVIDENCE_PATH",OUT,flush=True)
