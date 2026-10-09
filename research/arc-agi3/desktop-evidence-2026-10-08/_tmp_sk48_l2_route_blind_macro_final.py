"""SK48 L2 route-blind, native macro A/B after fourth-color beam wall.

The generator enumerates rectangular control movements from *only* the
current-run route-blind third-color witness. It does not load any saved
L2 solution, macro, prior positive trace or private engine state.
Allowed prior: Level1 entrance and pre-existing public color sensor.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame
from _sk48_public_connected_goal import connected_features
from hashlib import sha256
import numpy as np,json,logging,time
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
cold3=json.loads((F/"sk48_l2_route_blind_third_color_2026-10-08.json").read_text())
SEED=cold3["first_third_color"]["p"]
assert cold3["first_third_color"]["prefix"]==3 and len(SEED)==21
game=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
calls=0;retries=0;root_hash=None;clock=time.monotonic()
def step(z):
 global calls
 o=game.step(z,data={});calls+=1;return o
def native(path):
 global retries,root_hash
 for t in range(8):
  o=step(GameAction.RESET)
  if o.levels_completed==0:break
  retries+=1
 else:raise RuntimeError("reset did not reach L1")
 for z in L1:
  o=step(GameAction.from_id(z))
  if o.levels_completed>=1:break
 assert o.levels_completed==1
 h=sha256(frame(o).tobytes()).hexdigest()
 if root_hash is None:root_hash=h
 assert root_hash==h
 for z in path:
  o=step(GameAction.from_id(z))
  if o.levels_completed>=2:break
 return o
root=native(SEED)
assert connected_features(frame(root))["connected_prefix"]>=3
# Symmetric action grammar: horizontal extension/retraction + vertical
# transport, with optional undo-side correction. These families do not
# contain any previously saved explicit direction sequence.
programs=[]
for v in (1,2):
 other=3-v
 for a in range(1,5):
  for b in range(1,7):
   for c in range(1,4):
    for k in range(0,3):
     V=[v]*c;H=[4]*a;R=[3]*b;tail=[4]*k
     programs.extend([
       ("extend_retract_shift",H+R+V+tail),
       ("retract_shift_extend",R+V+H+tail),
       ("shift_retract_extend",V+R+H+tail),
       ("retract_extend_shift",R+H+V+tail),
       ("shift_extend_retract",V+H+R+tail)])
seen=set();uniques=[];success=[];positives=[];window={}
for typ,program in programs:
 if len(uniques)>=1050:break
 key=tuple(program)
 if key in seen:continue
 seen.add(key)
 o=native(SEED+program)
 f=connected_features(frame(o))
 rec={"type":typ,"suffix":program,"prefix":f["connected_prefix"],
   "native_level":int(o.levels_completed),
   "native_sha":sha256(frame(o).tobytes()).hexdigest()}
 uniques.append(rec)
 if rec["prefix"]>=4 or rec["native_level"]>=2:
  positives.append(rec)
  print("ROUTE_BLIND_FOURTH_MACRO_WITNESS",rec,flush=True)
  if rec["native_level"]>=2:
   success.append(rec)
   break
 if len(uniques)%200==0:
  print("ROUTE_BLIND_FOURTH_MACRO_BATCH",len(uniques),
        "CONNECTED4",len(positives),"NATIVE_WINS",len(success),
        "SDK_CALLS",calls,"SECONDS",round(time.monotonic()-clock,1),flush=True)
 if time.monotonic()-clock>85 or calls>108000:break
OUT=F/"sk48_l2_route_blind_fourth_macro_2026-10-08.json"
result={"source":"native route-blind Level2 3-color entrance and generic symmetric control-run grammar",
 "saved_positive_L2_route_loaded":False,"partial_preexisting_route_loaded":False,
 "read_private_engine_state":False,"third_color_seed":SEED,
 "tested_unique_macro_suffixes":len(uniques),"prefix4_matches":positives,
 "native_Level2_completions":success,
 "actual_native_Level2_completion":bool(success),
 "attempts":uniques,
 "native_calls":calls,"reset_retries":retries,
 "elapsed_seconds":round(time.monotonic()-clock,2)}
OUT.write_text(json.dumps(result,indent=2),encoding="utf-8")
print("ROUTE_BLIND_FOURTH_MACRO_RESULT","TESTED",len(uniques),
 "CONNECTED4",len(positives),"NATIVE_WINS",len(success),"SAVED",OUT,flush=True)
