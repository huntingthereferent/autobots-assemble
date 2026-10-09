"""SK48 route-blind L2 native A/B staged runner.

Usage:
  python sk48_route_blind_l2_runner.py           # inspect existing witnesses
  python sk48_route_blind_l2_runner.py --run     # rerun native search and verification

The --run pipeline reads the previously independently discovered
Level1 entrance and pre-existing public sensor, but NOT any saved
successful Level2 action sequence. Only the POST-search integration
step makes a novelty comparison with the old positive reference.

This is not an unseen-task blind ARC-AGI-3 solver and does not submit.
"""
from pathlib import Path
import json, subprocess, sys
F=Path(__file__).resolve().parent
STAGES=[
 ("first and second color", "_tmp_sk48_l2_route_blind_bounded_ab.py"),
 ("third color", "_tmp_sk48_l2_route_blind_stage3.py"),
 ("generic macro final color", "_tmp_sk48_l2_route_blind_macro_final.py"),
 ("fresh full-chain integration", "_tmp_sk48_cold_l2_full_integration.py"),
]
ARTIFACTS=[
 "sk48_l2_route_blind_a_b_search_2026-10-08.json",
 "sk48_l2_route_blind_third_color_2026-10-08.json",
 "sk48_l2_route_blind_fourth_macro_2026-10-08.json",
 "SK48_ROUTE_BLIND_L2_NATIVE_WIN_INTEGRATION_2026-10-08.json",
]
def verify():
 a,b,c,d=(json.loads((F/n).read_text(encoding="utf-8")) for n in ARTIFACTS)
 p2=a["second_color_witness"]["p"]
 p3=b["first_third_color"]["p"]
 p4=c["native_Level2_completions"][0]["suffix"]
 actual=d["cold_L2_direction_actions"]
 assert p3[:len(p2)]==p2
 assert actual==p3+p4 and len(actual)==30
 assert a["saved_L2_solution_loaded"] is False
 assert b["prior_saved_positive_l2_read"] is False
 assert c["saved_positive_L2_route_loaded"] is False
 assert d["new_L2_differs_from_old_positive_reference"]
 assert len(d["cold_L2_fresh_replays"])==3
 assert all(x["native_levels_completed"]==2 for x in d["cold_L2_fresh_replays"])
 assert d["whole_game_fresh_native_WINS"]==3
 assert all(x["native_WIN"] for x in d["runs"])
 print("SK48_ROUTE_BLIND_L2_VERIFY: PASS",flush=True)
 print("  Level2 from public evidence:",len(actual),"native directional actions",flush=True)
 print("  Fresh Level2 replays: 3/3",flush=True)
 print("  Fresh all-level WINs: 3/3 (later levels reference-assisted)",flush=True)
 print("  Native action paths loaded for cold L2 search: no positive L2 route",flush=True)
if __name__=="__main__":
 if sys.argv[1:]==["--run"]:
  for name,filename in STAGES:
   print("STAGE",name,flush=True)
   subprocess.run([sys.executable,str(F/filename)],cwd=str(F),check=True)
 elif len(sys.argv)>1:
  raise SystemExit("Usage: python sk48_route_blind_l2_runner.py [--run]")
 verify()
