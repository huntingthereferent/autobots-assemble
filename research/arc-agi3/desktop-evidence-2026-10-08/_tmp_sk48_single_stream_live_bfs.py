"""SK48: truly single-instance public A/B breadth-first exploration.

No game copying, no engine internals, no saved action route, no guessed
level target. Native RESET + replay is verified before each expansion.
Records observed public-frame quotient and explicit live action evidence.
"""
from __future__ import annotations
from collections import defaultdict,Counter
from pathlib import Path
from hashlib import sha256
import json,time,logging
import numpy as np
from arc_agi import Arcade, OperationMode
from arcengine import GameAction

logging.disable(logging.CRITICAL)
OUT=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\sk48_live_single_stream_bfs.json")
arcade=Arcade(operation_mode=OperationMode.NORMAL)
game=arcade.make("sk48")
def signature(obs):
 return sha256(np.asarray(obs.frame[-1],dtype=np.uint8).tobytes()).hexdigest()
def key(obs):
 return (int(obs.levels_completed),obs.state.name,signature(obs))
start=game.observation_space
start_key=key(start)
frontier=[((),start_key)]
seen={start_key:()}
edges=0
native_actions=0
replay_failures=[]
first_witness=None
began=time.monotonic()
history=[]
for depth in range(1,18):
 upcoming=[]
 census=Counter()
 for path,parent_key in frontier:
  for action in (1,2,3,4):
   current=game.step(GameAction.RESET,data={})
   native_actions+=1
   if key(current)!=start_key:
    raise RuntimeError(("RESET diverged from initial native frame",depth,path))
   for previous_action in path:
    current=game.step(GameAction.from_id(previous_action),data={})
    native_actions+=1
   actual_parent=key(current)
   if actual_parent!=parent_key:
    example={"depth":depth,"path":list(path),"expected":parent_key,"actual":actual_parent}
    replay_failures.append(example)
    raise RuntimeError(("REPLAY not stable",example))
   output=game.step(GameAction.from_id(action),data={})
   native_actions+=1
   edges+=1
   after_key=key(output)
   census["changed" if after_key!=parent_key else "no_visible_change"]+=1
   if output.levels_completed>0:
    first_witness={
      "path":list(path+(action,)),
      "actions_to_complete":len(path)+1,
      "levels_completed":int(output.levels_completed),
      "game_state":output.state.name,
      "native_before_sha256":parent_key[2],
      "native_after_sha256":after_key[2],
      "new_native_action":action,
      "local_sdk_score":arcade.get_scorecard().score
    }
    break
   if output.state.name=="GAME_OVER":
    census["game_over"]+=1
    continue
   if after_key not in seen:
    child_path=path+(action,)
    seen[after_key]=child_path
    upcoming.append((child_path,after_key))
  if first_witness:break
 record={
   "depth":depth,"frontier":len(frontier),
   "new_unique_visible":len(upcoming),
   "total_unique":len(seen),
   "expanded_edges":edges,
   "native_actions_including_resets_and_replays":native_actions,
   "elapsed_seconds":round(time.monotonic()-began,2),
   "movement":dict(census),
 }
 history.append(record)
 print("LIVE_BFS",record,flush=True)
 if first_witness or not upcoming:break
 frontier=upcoming
 if time.monotonic()-began>165 or native_actions>75000 or len(seen)>3200:
  print("BOUNDARY search budget reached",flush=True);break
summary={
 "game":"sk48",
 "method":"single live instance, RESET and public verified replay; no game clones",
 "used_private_game_state":False,"loaded_saved_route":False,
 "levels":history,
 "distinct_public_states":len(seen),
 "native_actions":native_actions,
 "expanded_edges":edges,
 "replay_failures":replay_failures,
 "solution":first_witness,
 "elapsed_seconds":round(time.monotonic()-began,2),
}
OUT.write_text(json.dumps(summary,indent=2),encoding="utf-8")
print("LIVE_BFS_SUMMARY",json.dumps({k:v for k,v in summary.items() if k!="levels"}),flush=True)
print("EVIDENCE_PATH",OUT,flush=True)
