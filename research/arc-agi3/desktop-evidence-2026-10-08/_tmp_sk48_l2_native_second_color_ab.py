"""SK48 native A/B: independently search the next colored target.

Seed is read from a previous goal-guided native search (NOT the saved
Level2 solution). Enumerate all 1..5 move continuations and verify
prefix gain with the public-frame control/colored-row sensor.
No private engine reads or cloned game.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame,features
from hashlib import sha256
import json,logging,time
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
checkpoint=json.loads((F/"sk48_l2_goal_seed444_checkpoint.json").read_text())
first_color=next(m for m in checkpoint["milestones"] if m["max_prefix"]>=1)
seed=tuple(first_color["top_paths"][0]["p"])
print("NATIVE_FIRST_COLOR_SEED",seed,"FROM_DEPTH",first_color["depth"],flush=True)
g=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
calls=0;retry=0
def advance(z):
 global calls
 o=g.step(z,data={});calls+=1;return o
def run(route):
 global retry
 for i in range(8):
  o=advance(GameAction.RESET)
  if o.levels_completed==0:break
  retry+=1
 else:raise RuntimeError("native RESET acknowledgment failed")
 for z in L1:o=advance(GameAction.from_id(z))
 if o.levels_completed!=1:raise RuntimeError("native L2 not entered")
 for z in route:o=advance(GameAction.from_id(z))
 return o
root=run(seed);base=features(frame(root))
assert base["best_prefix"]==1,(seed,base)
front=[()]
found=[];seen_by_depth=[];t0=time.monotonic()
for extra in range(1,6):
 next_front=[];distinct=set();pred=0;exp=0
 for p in front:
  for z in (1,2,3,4):
   route=seed+p+(z,)
   o=run(route)
   fit=features(frame(o));exp+=1
   if o.levels_completed>=2 or fit["best_prefix"]>=2:
    witness={"path":list(route),"additional_actions":extra,
     "prefix":fit["best_prefix"],"colors":[q["attached_row"] for q in fit["candidates"]],
     "native_level":int(o.levels_completed),
     "target":list(fit["target"]),
     "frame_sha256":sha256(frame(o).tobytes()).hexdigest()}
    found.append(witness)
    print("NATIVE_SECOND_COLOR_WITNESS",witness,flush=True)
   signature=(sha256(frame(o).tobytes()).digest(),route[-3:])
   if signature in distinct:continue
   distinct.add(signature)
   if fit["best_prefix"]<2 and o.state.name!="GAME_OVER":
    next_front.append(p+(z,))
  if found and len(found)>=5:break
 record={"extra_depth":extra,"paths_at_depth":len(front)*4,
         "unique_next":len(next_front),"witnesses":len(found),
         "native_calls":calls,"seconds":round(time.monotonic()-t0,2)}
 seen_by_depth.append(record)
 print("A_B_NEXT_COLOR",record,flush=True)
 if found:break
 front=next_front
 if calls>35000:
  print("SEARCH_WALL action budget",flush=True);break
result={"seed_source":"prior native beam witness, not saved Level2 answer",
        "seed":list(seed),"method":"exhaustive bounded next-color action search",
        "native_only":True,"uses_game_clone":False,
        "found_witnesses":found,"levels":seen_by_depth,
        "native_calls":calls,"reset_retries":retry}
out=F/"sk48_l2_native_second_color_ab.json"
out.write_text(json.dumps(result,indent=2),encoding="utf-8")
print("SAVED",out,"FOUND",len(found),flush=True)
