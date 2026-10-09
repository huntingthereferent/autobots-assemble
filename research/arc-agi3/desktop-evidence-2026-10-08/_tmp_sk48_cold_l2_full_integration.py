"""SK48 route-blind Level2 native replay and whole-chain integration.

COLD LEVEL2 ROUTE is assembled exclusively from the fresh route-blind
Level2 third-color output and the fresh route-blind final macro output.
Old successful L2 reference is consulted ONLY after the route is fixed
for a post-hoc novelty comparison. Levels3-8 remain reference-assisted.
No private SDK game state or cloning; ACTION6 uses public frame pixels.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame
from _sk48_native_public_stage_harness import run_level
from hashlib import sha256
import numpy as np,json,logging,time,ast
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
S3=json.loads((F/"sk48_l2_route_blind_third_color_2026-10-08.json").read_text())
S4=json.loads((F/"sk48_l2_route_blind_fourth_macro_2026-10-08.json").read_text())
assert S4["actual_native_Level2_completion"]
L2=S3["first_third_color"]["p"]+S4["native_Level2_completions"][0]["suffix"]
assert len(L2)==30 and len(set(L2))>=3
print("COLD_L2_ROUTE_FROZEN",L2,"ACTIONS",len(L2),flush=True)
starts=[];native_root=None;native_after=None
for trial in range(3):
 e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
 o=e.observation_space
 o,k1,_=run_level(e,o,L1,1)
 before=sha256(frame(o).tobytes()).hexdigest()
 o,k2,_=run_level(e,o,L2,2)
 after=sha256(frame(o).tobytes()).hexdigest()
 assert k2==30 and o.levels_completed==2,(k2,o.levels_completed)
 if native_root is None:native_root=before;native_after=after
 assert before==native_root and after==native_after
 entry={"trial":trial,"L1_used":k1,"new_L2_used":k2,
  "start_frame_SHA256":before,"after_frame_SHA256":after,
  "native_levels_completed":int(o.levels_completed)}
 starts.append(entry)
 print("COLD_L2_FRESH_VERIFIED",entry,flush=True)
# POST-HOC COMPARISON ONLY (never used for constructing L2).
known_tree=ast.parse((F/"_tmp_sk48_complete_replay.py").read_text())
oldP2=list(next(ast.literal_eval(n.value) for n in known_tree.body
 if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="p2" for t in n.targets)))
posthoc_diff=(L2!=oldP2)
print("POSTHOC_OLD_SAVED_L2_DIFFERS",posthoc_diff,flush=True)
# Later levels: explicitly marked reference-assisted validated alternatives.
L3=[r["L3_path"] for r in json.loads((F/"sk48_l3_native_fresh_macro_wins.json").read_text())["results"] if r["passed"]]
L4=[r["path"] for r in json.loads((F/"sk48_l4_native_reference_mutation_ab.json").read_text())["successful_interventions"] if r["method"]=="swap_adjacent"]
L5=[r["actions"] for r in json.loads((F/"sk48_l5_native_fresh_swap_witnesses.json").read_text())["routes"] if r["passed"]]
L6=[r["route"] for r in json.loads((F/"sk48_l6_native_fresh_swap_witnesses.json").read_text())["results"] if r["all_pass"]]
L7=[r["route"] for r in json.loads((F/"sk48_l7_native_fresh_swaps.json").read_text())["routes"] if r["all_pass"]]
L8=[r["L8_route"] for r in json.loads((F/"sk48_l8_native_fresh_alternative_WINs.json").read_text())["results"] if r["both_fresh_WINS"]]
all_routes=[[L1],[L2],L3,L4,L5,L6,L7,L8]
runs=[];t0=time.monotonic()
for trial in range(3):
 e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
 o=e.observation_space;stages=[];total=0
 for level,variants in enumerate(all_routes,1):
  route=variants[(trial+level)%len(variants)]
  parent=sha256(frame(o).tobytes()).hexdigest()
  o,k,clicks=run_level(e,o,route,level)
  total+=k
  stage={"stage":level,"used":k,"original_candidates":len(route),
   "unused_actions":len(route)-k,"entry_SHA256":parent,
   "exit_SHA256":sha256(frame(o).tobytes()).hexdigest(),
   "public_control_clicks":clicks,"native_levels":int(o.levels_completed)}
  stages.append(stage)
 if o.levels_completed!=8 or o.state.name!="WIN":
  raise RuntimeError(("end not native WIN",trial,o.levels_completed,o.state.name))
 result={"trial":trial,"total_native_actions":total,"native_WIN":True,"stages":stages}
 runs.append(result)
 print("COLD_L2_ENTIRE_NATIVE_WIN",trial,"ACTIONS",total,
  "COLD_L2_USED",stages[1]["used"],"STATE",o.state.name,flush=True)
out=F/"SK48_ROUTE_BLIND_L2_NATIVE_WIN_INTEGRATION_2026-10-08.json"
out.write_text(json.dumps({"game":"sk48","result":"3 cold-L2 integrated native WINs",
 "L2_provenance":"route-blind, prior public sensor & A/B search principles",
 "L3toL8_provenance":"reference-assisted prior native witnesses",
 "native_SDK_only":True,"private_engine_read":False,
 "old_L2_route_compared_only_after_freeze":True,
 "new_L2_differs_from_old_positive_reference":posthoc_diff,
 "cold_L2_direction_actions":L2,"cold_L2_fresh_replays":starts,
 "whole_game_fresh_native_WINS":len(runs),"runs":runs,
 "elapsed_seconds":round(time.monotonic()-t0,2)},indent=2),encoding="utf-8")
print("ALL_TESTS_PASSED",len(starts),"COLD_L2_AND",len(runs),"ENTIRE_GAMES",
 "SAVED",out,flush=True)
