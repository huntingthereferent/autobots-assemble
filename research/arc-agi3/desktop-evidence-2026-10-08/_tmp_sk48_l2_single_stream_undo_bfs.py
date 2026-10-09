"""SK48 L2 one-native-stream A/B frontier, validated undo, resumable.

Native operations: RESET, ACTION1..4, ACTION7, frame, levels_completed.
No private game objects, cloned simulator, Level 2 route, or hidden ontology.
Each parent replay is checked. Each tested ACTION7 must recover its exact
parent frame; on mismatch, restore the parent by acknowledged RESET/replay.
Resume from the last checkpoint without falsifying completed frontier depth.
"""
from __future__ import annotations
# REJECTED after native counterexample: chained ACTION7 kept the same public
# frame but changed valid future transitions. This unchecked optimizer must
# not be reused as an independent solver or valid search frontier.
raise SystemExit("REJECTED: chained undo aliases falsely merged; see SK48_NATIVE_PHASE_AB_REPORT_2026-10-08.md")
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from pathlib import Path
from hashlib import sha256
import numpy as np,json,logging,time
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
CHECK=F/"sk48_level2_undo_bfs_checkpoint.json"
game=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
total_calls=0;reset_retries=0;undo_failures=0;replay_failures=[]
def advance(z,data=None):
 global total_calls
 r=game.step(z,data=data or {})
 total_calls+=1
 return r
def key(r):
 a=np.asarray(r.frame[-1],dtype=np.uint8)
 return f"{int(r.levels_completed)}|{r.state.name}|{sha256(a.tobytes()).hexdigest()}"
def enter_l2(path):
 global reset_retries
 for k in range(8):
  r=advance(GameAction.RESET)
  if r.levels_completed==0:break
  reset_retries+=1
 else:raise RuntimeError("WALL: no level 0 native reset acknowledgement")
 for z in L1:r=advance(GameAction.from_id(z))
 if r.levels_completed!=1:raise RuntimeError("WALL: L1 replay not in level 2")
 for z in path:r=advance(GameAction.from_id(z))
 return r
def dump(state):
 state.update({"calls_current_session":total_calls,"reset_retries_current_session":reset_retries,
               "undo_failures_current_session":undo_failures,
               "replay_failures":replay_failures})
 CHECK.write_text(json.dumps(state,separators=(",",":")),encoding="utf-8")
if CHECK.exists():
 state=json.loads(CHECK.read_text(encoding="utf-8"))
 if state.get("complete") or state.get("solution"):
  print("PRIOR_RESULT",state.get("solution"),flush=True)
  raise SystemExit
 print("RESTORED_CHECKPOINT","DEPTH",state["depth"],
       "FRONTIER",len(state["frontier"]),"INDEX",state["at"],
       "SEEN",len(state["seen"]),flush=True)
else:
 start=enter_l2(())
 state={"schema":"sk48:l2:single-stream:undo-v1","depth":1,
        "frontier":[{"path":[],"key":key(start)}],
        "next":[],"at":0,"seen":{key(start):[]},
        "finished":[],"solution":None,"complete":False,
        "uses_game_clone":False,"uses_private_engine":False,"has_saved_l2_route":False}
 dump(state)
t0=time.monotonic();session_edges=0
while state["depth"]<=31:
 cur=state["frontier"]
 if state["at"]>=len(cur):
  record={"depth":state["depth"],"expanded_parents":len(cur),
    "unique_new":len(state["next"]),"unique_total":len(state["seen"]),
    "elapsed_session_seconds":round(time.monotonic()-t0,2),
    "native_calls_session":total_calls,"undo_failures_session":undo_failures}
  state["finished"].append(record)
  print("AB_DEPTH_COMPLETE",record,flush=True)
  if not state["next"]:state["complete"]=True;dump(state);break
  state["depth"]+=1;state["frontier"]=state["next"];state["next"]=[];state["at"]=0
  dump(state);continue
 if state["at"]%10==0 and time.monotonic()-t0>=43:
  print("AB_SESSION_WALL","DEPTH",state["depth"],"PARENT",state["at"],
        "OF",len(cur),"SEEN",len(state["seen"]),"CALLS",total_calls,flush=True)
  dump(state);break
 parent=cur[state["at"]]
 path=parent["path"];expected=parent["key"]
 before=enter_l2(path)
 actual=key(before)
 if actual!=expected:
  replay_failures.append({"path":path,"expected":expected,"actual":actual})
  dump(state)
  raise RuntimeError("AB replay mismatch; do not merge divergent referents")
 for z in (1,2,3,4):
  after=advance(GameAction.from_id(z))
  next_key=key(after);session_edges+=1
  if after.levels_completed>=2:
   state["solution"]={"actions":path+[z],"level2_length":len(path)+1,
                      "native_observed_level":int(after.levels_completed),
                      "last_public_frame":next_key,
                      "level2_action":z}
   dump(state)
   print("INDEPENDENT_LEVEL2_SOLVE",state["solution"],flush=True)
   raise SystemExit
  if after.state.name!="GAME_OVER" and next_key not in state["seen"]:
   child_path=path+[z]
   state["seen"][next_key]=child_path
   state["next"].append({"path":child_path,"key":next_key})
  # Never promote unverified rollback as proof.
  undone=advance(GameAction.ACTION7)
  if key(undone)!=expected:
   undo_failures+=1
   restored=enter_l2(path)
   if key(restored)!=expected:
    dump(state);raise RuntimeError("AB rollback AND replay failed")
 state["at"]+=1
 if state["at"]%30==0:dump(state)
 if len(state["seen"])>=10000:
  dump(state);print("AB_STATE_CAP",len(state["seen"]),flush=True);break
print("AB_SESSION_RESULT",json.dumps({
 "depth":state["depth"],"at":state["at"],"frontier":len(state["frontier"]),
 "next":len(state["next"]),"total_unique":len(state["seen"]),
 "native_calls":total_calls,"reset_retries":reset_retries,
 "undo_failures":undo_failures,"session_edges":session_edges,
 "elapsed_seconds":round(time.monotonic()-t0,2),
 "solution":state["solution"]}),flush=True)
dump(state)
