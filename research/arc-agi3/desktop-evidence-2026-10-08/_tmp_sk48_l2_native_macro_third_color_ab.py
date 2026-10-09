"""SK48 native Level2 A/B macro-run contrast (reference-assisted operator family).

Start from independently witnessed public 2-color state, not saved L2 route.
Test variable-length extend / retract / vertical-shift macros against the
next public color goal. This family is informed by structural positive
regression; a hit is not a blind independent whole-level solve.
"""
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame,features
from pathlib import Path
import json,logging,time,hashlib
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
seed=json.loads((F/"sk48_l2_native_second_color_ab.json").read_text())["found_witnesses"][0]["path"]
game=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
calls=0;retries=0
def go(seq):
 global calls,retries
 for t in range(8):
  o=game.step(GameAction.RESET,data={});calls+=1
  if o.levels_completed==0:break
  retries+=1
 else:raise RuntimeError("RESET UNKNOWN")
 for z in L1+seed+seq:
  o=game.step(GameAction.from_id(z),data={});calls+=1
 return o
tests=[];hits=[];start=time.monotonic()
for a in range(1,5):
 for b in range(1,7):
  for c in range(1,4):
   suffix=[4]*a+[3]*b+[1]+[4]*c+[1,4,2]
   o=go(suffix);ft=features(frame(o))
   rec={"extend_a":a,"retract_b":b,"reextend_c":c,
        "suffix":suffix,"prefix":ft["best_prefix"],
        "colors":[list(x["attached_row"]) for x in ft["candidates"]],
        "level":int(o.levels_completed),"native_frame_sha256":hashlib.sha256(frame(o).tobytes()).hexdigest()}
   tests.append(rec)
   if rec["prefix"]>=3 or rec["level"]>=2:
    hits.append(rec);print("NATIVE_MACRO_STAGE3_HIT",rec,flush=True)
  print("A_B_MACRO_A",a,"TESTED",len(tests),"HITS",len(hits),
        "NATIVE",calls,"SECONDS",round(time.monotonic()-start,1),flush=True)
out=F/"sk48_l2_native_macro_third_color_ab.json"
out.write_text(json.dumps({"status":"reference-assisted structural macro A/B",
  "native_SDK_only":True,"saved_Level2_route_loaded":False,
  "seed_native_second_color":seed,"candidate_count":len(tests),"hits":hits,
  "tests":tests,"native_calls":calls,"reset_retries":retries,
  "elapsed_seconds":round(time.monotonic()-start,2)},indent=2),encoding="utf-8")
print("MACRO_RESULT",len(hits),"OF",len(tests),"SAVED",out,flush=True)
