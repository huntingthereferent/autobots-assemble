"""SK48 public-native fourth color macro tests and completion probe.

Candidate histories are built from observed native stage-2 witness + stage-3
macro hits; the saved Level 2 solution is never loaded into this script.
The macro family is reference-assisted, so distinguish this from blind solve.
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
SEED=json.loads((F/"sk48_l2_native_second_color_ab.json").read_text())["found_witnesses"][0]["path"]
HITS=json.loads((F/"sk48_l2_native_macro_third_color_ab.json").read_text())["hits"]
# Four distinct native frame endpoints, not copies of the saved solution.
unique={}
for hit in HITS:unique.setdefault(hit["native_frame_sha256"],hit)
pivots=list(unique.values())[:4]
print("MACRO_PIVOTS",[(h["extend_a"],h["retract_b"],h["reextend_c"]) for h in pivots],flush=True)
g=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
calls=0;retry=0
def go(route):
 global calls,retry
 for i in range(8):
  o=g.step(GameAction.RESET,data={});calls+=1
  if o.levels_completed==0:break
  retry+=1
 else:raise RuntimeError("Native RESET UNKNOWN")
 for z in L1+route:o=g.step(GameAction.from_id(z),data={});calls+=1
 return o
t0=time.monotonic();tests=[];stage4=[];wins=[]
for si,h in enumerate(pivots):
 pivot=SEED+h["suffix"]
 for a in (1,2,3):
  for b in (1,2,3,4):
   for c in (1,2,3):
    suffix=[4]*a+[3]*b+[2]*c
    full=pivot+suffix
    o=go(full)
    f=features(frame(o))
    is_stage4=f["best_prefix"]>=4
    rec={"pivot":si,"a":a,"b":b,"c":c,"path":full,
         "prefix":f["best_prefix"],"level":int(o.levels_completed),
         "sha":sha256(frame(o).tobytes()).hexdigest()}
    tests.append(rec)
    if is_stage4 or o.levels_completed>=2:
     stage4.append(rec)
     print("NATIVE_FOURTH_COLOR",{"pivot":si,"macro":[a,b,c],"length":len(full),
      "prefix":f["best_prefix"],"completed":o.levels_completed},flush=True)
     if o.levels_completed>=2:
      wins.append({**rec,"finisher":[]})
     else:
      # Check native completion without assuming identical visual frame == win.
      for k,final_z in enumerate((4,4,4),1):
       o=g.step(GameAction.from_id(final_z),data={});calls+=1
       if o.levels_completed>=2:
        wins.append({**rec,"finisher_steps_required":k,
                     "complete_path":full+[4]*k,
                     "native_completed":int(o.levels_completed)})
        break
  print("PIVOT",si,"TESTS",len(tests),"STAGE4",len(stage4),
        "WIN_CANDIDATES",len(wins),"NATIVE_CALLS",calls,
        "SECONDS",round(time.monotonic()-t0,1),flush=True)
out=F/"sk48_l2_native_macro_fourth_color_ab.json"
out.write_text(json.dumps({"game":"sk48","method":"reference-assisted native macro A/B",
 "loaded_saved_L2_solution":False,"pivots":pivots,"tested":len(tests),
 "stage4":stage4,"wins_provisional":wins,"all_tests":tests,
 "native_calls":calls,"reset_retries":retry},indent=2),encoding="utf-8")
print("STAGE4_RESULT",len(stage4),"WIN_HINTS",len(wins),"SAVED",out,flush=True)
