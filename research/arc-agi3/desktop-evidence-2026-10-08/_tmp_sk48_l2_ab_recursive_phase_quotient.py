"""Reconstruct the observed SK48 A/B phase quotient from native witnesses.

Language/data layer only: no game import, control policy, or architecture fork.
The quotient is referent-local and horizon-scoped.
"""
from __future__ import annotations
from pathlib import Path
from collections import defaultdict,Counter
from itertools import combinations
import json
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
tracefile=F/"sk48_l2_native_trajectory_horizon3_ab.json"
crossfile=F/"sk48_l2_directional_phase_cross_source_ab.json"
trace=json.loads(tracefile.read_text(encoding="utf-8"))
cross=json.loads(crossfile.read_text(encoding="utf-8"))
examples=trace["examples"]
assert len(examples)==64,(len(examples),"not every native suffix")
assert not trace["within_count_conflicts"]
assert not cross["same_phase_counterexamples"]
assert cross["tested_suffixes"]==64
sources={int(k):v for k,v in cross["source_variants"].items()}
classes={}
for h in (1,2,3):
 signature_family=defaultdict(list)
 for phase in range(4):
  signature=tuple(
   tuple(examples[s]["phase_trajectories"][str(phase)][:h])
   for s in sorted(examples)
  )
  signature_family[signature].append(phase)
 partition=tuple(sorted(tuple(v) for v in signature_family.values()))
 classes[h]=partition
 print("AB_PREDICTIVE_HORIZON",h,"CLASSES",partition,flush=True)
assert classes[1]==((0,1,2),(3,)),classes[1]
assert classes[2]==((0,1),(2,),(3,)),classes[2]
assert classes[3]==((0,),(1,),(2,),(3,)),classes[3]
separations={}
for a,b in combinations(range(4),2):
 firsts=Counter()
 for suffix in examples:
  A=examples[suffix]["phase_trajectories"][str(a)]
  B=examples[suffix]["phase_trajectories"][str(b)]
  first=next((i+1 for i,(v,w) in enumerate(zip(A,B)) if v!=w),None)
  firsts[first]+=1
 if None in firsts:raise AssertionError(("undistinguished",a,b,firsts))
 separations[f"{a}|{b}"]={str(k):v for k,v in sorted(firsts.items())}
print("AB_FIRST_SEPARATIONS",separations,flush=True)
quotient={
 "referent":"SK48 native public Level 2 entry, phase family",
 "method":"A/B equivalent witnessed public three-action continuation trajectories",
 "not_global_game_state":True,
 "native_frame_equal_before_test":True,
 "levels_tested":[2],
 "phase_counts":[0,1,2,3],
 "source_witnesses_per_phase":sources,
 "tested_three_action_suffixes":len(examples),
 "cross_source_native_continuations":64*sum(map(len,sources.values())),
 "within_class_counterexamples":len(cross["same_phase_counterexamples"]),
 "partitions_by_prediction_horizon":{str(k):v for k,v in classes.items()},
 "first_separating_action_by_phase_pair":separations,
 "input_witnesses":[tracefile.name,crossfile.name],
 "state_admission":"Preserve full native public frame AND witnessed action-phase relation; otherwise UNKNOWN",
 "solver_status":"Local independent SK48 Level 1 solved; independent Level 2 remains open",
}
out=F/"sk48_l2_ab_recursive_phase_quotient.json"
out.write_text(json.dumps(quotient,indent=2),encoding="utf-8")
print("ASSERTIONS_PASS","tested_suffixes",len(examples),"native_continuations",quotient["cross_source_native_continuations"],
      "witness_conflicts",quotient["within_class_counterexamples"],flush=True)
print("SAVED",out,flush=True)
