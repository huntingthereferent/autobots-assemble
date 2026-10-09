"""SK48 final Level8 positive-reference native calibration.

Saved 24-action P8 positive trace used ONLY as separate reference;
prior seven levels use verified alternative directions and visual
control-click selection. Native WIN state is required, not visual guess.
"""
from _sk48_native_public_stage_harness import F,enter,run_level
from _sk48_public_goal_sensor import frame
from hashlib import sha256
import json,ast,logging
logging.disable(logging.CRITICAL)
L7s=[x["route"] for x in json.loads((F/"sk48_l7_native_fresh_swaps.json").read_text())["routes"] if x["all_pass"]]
tree=ast.parse((F/"_tmp_sk48_complete_replay.py").read_text())
ref=list(next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="P8" for t in n.targets)))
runs=[]
for i in range(2):
 e,o,stages=enter(7,selector=i)
 o,n,c=run_level(e,o,L7s[i%len(L7s)],7)
 entry=sha256(frame(o).tobytes()).hexdigest()
 o,k,sw=run_level(e,o,ref,8)
 rec={"trial":i,"native_levels_completed":int(o.levels_completed),
   "state_name":o.state.name,"first_completed_at":k,
   "L8_entry_sha":entry,"L8_switch_clicks":sw,
   "L7_actions":n,"upstream_consumed":[q[1] for q in stages]}
 runs.append(rec)
 print("SK48_L8_REFERENCE",rec,flush=True)
dest=F/"sk48_l8_native_positive_public_reference.json"
dest.write_text(json.dumps({"source":"saved positive P8, not blind new solve",
 "P8":ref,"native_public_only":True,"trials":runs},indent=2),encoding="utf-8")
print("SAVED",dest,flush=True)
